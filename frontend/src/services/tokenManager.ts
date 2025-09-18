/**
 * HushMCP Token Management Service
 * ===============================
 * 
 * Manages consent tokens, refresh functionality, and user-specific token storage
 * for the HushMCP framework integration
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_HUSHMCP_API_URL || 'https://hush-backend-sepia.vercel.app';

export interface ConsentToken {
  token: string;
  expires_at: number;
  scope: string;
  user_id: string;
  agent_id: string;
}

export interface TokenStorage {
  [scope: string]: {
    token: string;
    expires_at: number;
    created_at: number;
  };
}

export interface RefreshableToken {
  access_token: string;
  refresh_token?: string;
  expires_at: number;
  token_type: string;
}

class HushMCPTokenManager {
  private tokenCache: Map<string, TokenStorage> = new Map();
  private readonly TOKEN_CACHE_KEY = 'hushmcp_tokens';
  private readonly TOKEN_REFRESH_THRESHOLD = 5 * 60 * 1000; // 5 minutes in milliseconds

  constructor() {
    this.loadTokensFromStorage();
  }

  /**
   * Load tokens from localStorage
   */
  private loadTokensFromStorage(): void {
    try {
      const stored = localStorage.getItem(this.TOKEN_CACHE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        this.tokenCache = new Map(Object.entries(parsed));
      }
    } catch (error) {
      console.error('Error loading tokens from storage:', error);
    }
  }

  /**
   * Save tokens to localStorage
   */
  private saveTokensToStorage(): void {
    try {
      const obj = Object.fromEntries(this.tokenCache);
      localStorage.setItem(this.TOKEN_CACHE_KEY, JSON.stringify(obj));
    } catch (error) {
      console.error('Error saving tokens to storage:', error);
    }
  }

  /**
   * Get user-specific token cache key
   */
  private getUserCacheKey(userId: string): string {
    return `user_${userId}`;
  }

  /**
   * Check if a token is expired or needs refresh
   */
  private needsRefresh(expiresAt: number): boolean {
    return (expiresAt - Date.now()) < this.TOKEN_REFRESH_THRESHOLD;
  }

  /**
   * Create a new consent token for a user
   */
  async createConsentToken(
    userId: string, 
    agentId: string, 
    scope: string
  ): Promise<ConsentToken | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/consent/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          agent_id: agentId,
          scope: scope
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to create consent token: ${response.statusText}`);
      }

      const tokenData = await response.json();
      
      const consentToken: ConsentToken = {
        token: tokenData.token,
        expires_at: tokenData.expires_at,
        scope: tokenData.scope,
        user_id: userId,
        agent_id: agentId
      };

      // Cache the token
      this.cacheToken(userId, scope, {
        token: tokenData.token,
        expires_at: tokenData.expires_at,
        created_at: Date.now()
      });

      console.log(`✅ Created consent token for user ${userId}, scope: ${scope}`);
      return consentToken;

    } catch (error) {
      console.error('Error creating consent token:', error);
      return null;
    }
  }

  /**
   * Cache a token for a user
   */
  private cacheToken(userId: string, scope: string, tokenData: TokenStorage[string]): void {
    const userKey = this.getUserCacheKey(userId);
    const userTokens = this.tokenCache.get(userKey) || {};
    
    userTokens[scope] = tokenData;
    this.tokenCache.set(userKey, userTokens);
    this.saveTokensToStorage();
  }

  /**
   * Get a valid token for a user and scope (with automatic refresh)
   */
  async getValidToken(userId: string, agentId: string, scope: string): Promise<string | null> {
    try {
      const userKey = this.getUserCacheKey(userId);
      const userTokens = this.tokenCache.get(userKey);
      
      // Check if we have a cached token
      if (userTokens && userTokens[scope]) {
        const tokenData = userTokens[scope];
        
        // Check if token is still valid
        if (!this.needsRefresh(tokenData.expires_at)) {
          console.log(`🎫 Using cached token for user ${userId}, scope: ${scope}`);
          return tokenData.token;
        }
        
        console.log(`🔄 Token expired for user ${userId}, scope: ${scope}, refreshing...`);
      }

      // Create a new token
      const newToken = await this.createConsentToken(userId, agentId, scope);
      return newToken?.token || null;

    } catch (error) {
      console.error('Error getting valid token:', error);
      return null;
    }
  }

  /**
   * Validate a token with the backend
   */
  async validateToken(token: string, expectedScope: string): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/consent/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: token,
          expected_scope: expectedScope
        })
      });

      if (!response.ok) {
        return false;
      }

      const result = await response.json();
      return result.valid === true;

    } catch (error) {
      console.error('Error validating token:', error);
      return false;
    }
  }

  /**
   * Create tokens for multiple scopes (common use case)
   */
  async createTokenSet(
    userId: string, 
    agentId: string, 
    scopes: string[]
  ): Promise<Record<string, string>> {
    const tokens: Record<string, string> = {};
    
    for (const scope of scopes) {
      const token = await this.getValidToken(userId, agentId, scope);
      if (token) {
        tokens[scope] = token;
      }
    }
    
    return tokens;
  }

  /**
   * Clear all tokens for a user (logout)
   */
  clearUserTokens(userId: string): void {
    const userKey = this.getUserCacheKey(userId);
    this.tokenCache.delete(userKey);
    this.saveTokensToStorage();
    console.log(`🗑️ Cleared all tokens for user: ${userId}`);
  }

  /**
   * Clear all cached tokens
   */
  clearAllTokens(): void {
    this.tokenCache.clear();
    localStorage.removeItem(this.TOKEN_CACHE_KEY);
    console.log('🗑️ Cleared all cached tokens');
  }

  /**
   * Get token expiry info for debugging
   */
  getTokenInfo(userId: string, scope: string): any {
    const userKey = this.getUserCacheKey(userId);
    const userTokens = this.tokenCache.get(userKey);
    
    if (userTokens && userTokens[scope]) {
      const tokenData = userTokens[scope];
      return {
        scope: scope,
        expires_at: new Date(tokenData.expires_at).toISOString(),
        created_at: new Date(tokenData.created_at).toISOString(),
        expires_in_ms: tokenData.expires_at - Date.now(),
        needs_refresh: this.needsRefresh(tokenData.expires_at)
      };
    }
    
    return null;
  }

  /**
   * Common scope patterns for different agents
   */
  static readonly SCOPES = {
    VAULT_READ_EMAIL: 'vault.read.email',
    VAULT_WRITE_EMAIL: 'vault.write.email',
    VAULT_READ_CALENDAR: 'vault.read.calendar',
    VAULT_WRITE_CALENDAR: 'vault.write.calendar',
    VAULT_READ_CONTACTS: 'vault.read.contacts',
    VAULT_WRITE_CONTACTS: 'vault.write.contacts',
    VAULT_READ_FILE: 'vault.read.file',
    VAULT_WRITE_FILE: 'vault.write.file',
    AGENT_MAILERPANDA: 'agent.mailerpanda.execute',
    AGENT_ADDTOCALENDAR: 'agent.addtocalendar.execute',
    AGENT_CHANDUFINANCE: 'agent.chandufinance.execute',
    AGENT_RESEARCH: 'agent.research.execute',
    AGENT_RELATIONSHIP: 'agent.relationship.execute'
  } as const;

  /**
   * Helper method to create standard token sets for common agents
   */
  async createMailerPandaTokens(userId: string): Promise<Record<string, string>> {
    return this.createTokenSet(userId, 'agent_mailerpanda', [
      HushMCPTokenManager.SCOPES.VAULT_READ_EMAIL,
      HushMCPTokenManager.SCOPES.VAULT_READ_CONTACTS,
      HushMCPTokenManager.SCOPES.AGENT_MAILERPANDA
    ]);
  }

  async createAddToCalendarTokens(userId: string): Promise<Record<string, string>> {
    return this.createTokenSet(userId, 'agent_addtocalendar', [
      HushMCPTokenManager.SCOPES.VAULT_READ_EMAIL,
      HushMCPTokenManager.SCOPES.VAULT_WRITE_CALENDAR,
      HushMCPTokenManager.SCOPES.AGENT_ADDTOCALENDAR
    ]);
  }

  async createResearchTokens(userId: string): Promise<Record<string, string>> {
    return this.createTokenSet(userId, 'agent_research', [
      HushMCPTokenManager.SCOPES.VAULT_READ_FILE,
      HushMCPTokenManager.SCOPES.VAULT_WRITE_FILE,
      HushMCPTokenManager.SCOPES.AGENT_RESEARCH
    ]);
  }

  async createRelationshipTokens(userId: string): Promise<Record<string, string>> {
    return this.createTokenSet(userId, 'agent_relationship', [
      HushMCPTokenManager.SCOPES.VAULT_READ_EMAIL,
      HushMCPTokenManager.SCOPES.VAULT_READ_CONTACTS,
      HushMCPTokenManager.SCOPES.AGENT_RELATIONSHIP
    ]);
  }
}

// Export the class for direct instantiation
export { HushMCPTokenManager };

// Global instance
export const tokenManager = new HushMCPTokenManager();

// Convenience functions
export const getValidConsentToken = (userId: string, agentId: string, scope: string) => 
  tokenManager.getValidToken(userId, agentId, scope);

export const createConsentTokens = (userId: string, agentId: string, scopes: string[]) => 
  tokenManager.createTokenSet(userId, agentId, scopes);

export const validateConsentToken = (token: string, scope: string) => 
  tokenManager.validateToken(token, scope);

export const clearUserTokens = (userId: string) => 
  tokenManager.clearUserTokens(userId);
