// HushMCP Agent API Service
const API_BASE_URL = import.meta.env.VITE_HUSHMCP_API_URL || 'http://127.0.0.1:8000';

// Import EmailTemplate from MassMail.tsx
// EmailTemplate interface
export interface EmailTemplate {
  subject: string;
  body: string;
}

export interface ConsentTokenRequest {
  user_id: string;
  agent_id: string;
  scope: string;
}

export interface ChatMessageRequest {
  user_id: string;
  message: string;
  consent_tokens: Record<string, string>;
  session_id?: string;
}

export interface ConsentTokenResponse {
  token: string;
  expires_at: number;
  scope: string;
}

// AddToCalendar Agent Types
export interface AddToCalendarRequest {
  user_id: string;
  email_token: string;
  calendar_token: string;
  google_access_token: string;
  action: 'comprehensive_analysis' | 'manual_event' | 'analyze_only';
  confidence_threshold?: number;
  max_emails?: number;
  event_details?: {
    title: string;
    date: string;
    time: string;
    duration?: string;
    description?: string;
    location?: string;
  };
}

export interface AddToCalendarResponse {
  status: 'success' | 'error';
  user_id: string;
  action_performed: string;
  emails_processed?: number;
  events_extracted?: number;
  events_created?: number;
  calendar_links?: string[];
  extracted_events?: Array<{
    summary: string;
    start_time: string;
    end_time: string;
    confidence: number;
    description?: string;
    location?: string;
  }>;
  processing_time: number;
  trust_links?: string[];
  errors?: string[];
}

// Google provider and model names
const GOOGLE_PROVIDER = 'google';
const GOOGLE_MODEL = 'model-pro';

// MailerPanda Agent Types
export interface MailerPandaExecuteRequest {
  user_id: string;
  user_input: string;
  mode: 'interactive' | 'batch';
  consent_tokens: Record<string, string>;
  sender_email?: string;
  recipient_emails?: string[];
  require_approval?: boolean;
  use_ai_generation?: boolean;
  ai_provider?: 'openai' | 'google' | 'anthropic';
  ai_model?: string;
  body: string;
}

export interface MailerPandaResponse {
  status: 'awaiting_approval' | 'success' | 'completed' | 'error';
  user_id: string;
  mode: string;
  campaign_id?: string;
  email_template?: EmailTemplate;
  requires_approval?: boolean;
  approval_status?: string;
  processing_time?: number;
  errors?: string[];
  emails_sent?: number;
  recipients_processed?: number;
}

export interface ApprovalRequest {
  user_id: string;
  feedback?: string;
  action: 'approve' | 'reject';
}

export interface SessionResponse {
  campaign_id: string;
  status: string;
  start_time: string;
  requires_approval: boolean;
}

// Removed stray assignment statements from interfaces


export interface ChatMessageResponse {
  status: 'success' | 'permission_denied' | 'error';
  agent_id: string;
  agent_version?: string;
  user_id: string;
  session_id: string;
  response?: string;
  conversation_length?: number;
  timestamp?: string;
  hushh_mcp_compliant?: boolean;
  error?: string;
}

export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ConversationHistoryResponse {
  status: string;
  session_id: string;
  user_id: string;
  conversation_history: ConversationMessage[];
  message_count: number;
  last_activity: string;
  agent_id: string;
}

export interface UserSession {
  session_id: string;
  message_count: number;
  last_activity: string;
  created: string;
}

export interface UserSessionsResponse {
  status: string;
  user_id: string;
  sessions: Record<string, UserSession>;
  total_sessions: number;
  agent_id: string;
}

export interface ChatAgentStatusResponse {
  agent_id: string;
  name: string;
  version: string;
  status: string;
  required_scopes: string[];
  required_inputs: Record<string, string>;
}

// AI Configuration Types
export interface AIConfig {
  provider: 'openai' | 'google' | 'anthropic';
  model: string;
  apiKey?: string;
}

export const AI_PROVIDERS = {
  openai: {
    name: 'OpenAI',
    models: ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
    defaultModel: 'gpt-4'
  },
  google: {
    name: 'Google',
    models: ['model-pro', 'google-vision', 'google-1.5-pro'],
    defaultModel: 'model-pro'
  },
  anthropic: {
    name: 'Anthropic Claude',
    models: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
    defaultModel: 'claude-3-sonnet'
  }
} as const;

class HushMcpApiService {
  private aiConfig: AIConfig = {
    provider: 'openai',
    model: 'gpt-4'
  };

  private async makeRequest(endpoint: string, options: RequestInit = {}) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(errorData.detail || errorData.errors?.[0] || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // AI Configuration
  setAIProvider(provider: 'openai' | 'google' | 'anthropic', model?: string) {
    this.aiConfig.provider = provider;
    this.aiConfig.model = model || AI_PROVIDERS[provider].defaultModel;
  }

  getAIConfig(): AIConfig {
    return { ...this.aiConfig };
  }

  getAvailableProviders() {
    return AI_PROVIDERS;
  }

  // Health check
  async checkHealth() {
    return this.makeRequest('/health');
  }

  // List available agents
  async listAgents() {
    return this.makeRequest('/agents');
  }

  // Create consent token
  async createConsentToken(request: ConsentTokenRequest): Promise<ConsentTokenResponse> {
    return this.makeRequest('/consent/token', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // AddToCalendar Agent Methods
  async getAddToCalendarRequirements() {
    return this.makeRequest('/agents/addtocalendar/requirements');
  }

  async executeAddToCalendar(request: AddToCalendarRequest): Promise<AddToCalendarResponse> {
    return this.makeRequest('/agents/addtocalendar/execute', {
      method: 'POST',
      body: JSON.stringify({
        ...request,
        ai_provider: this.aiConfig.provider,
        ai_model: this.aiConfig.model
      }),
    });
  }

  // Helper method to create AddToCalendar consent tokens
  async createAddToCalendarTokens(userId: string): Promise<{ email_token: string; calendar_token: string }> {
    const [emailToken, calendarToken] = await Promise.all([
      this.createConsentToken({
        user_id: userId,
        agent_id: 'agent_addtocalendar',
        scope: 'vault.read.email'
      }),
      this.createConsentToken({
        user_id: userId,
        agent_id: 'agent_addtocalendar',
        scope: 'vault.write.calendar'
      })
    ]);

    return {
      email_token: emailToken.token,
      calendar_token: calendarToken.token
    };
  }

  // Quick calendar event creation method
  async createCalendarEvent(
    userId: string, 
    googleAccessToken: string,
    eventDetails: {
      title: string;
      date: string;
      time: string;
      duration?: string;
      description?: string;
      location?: string;
    }
  ): Promise<AddToCalendarResponse> {
    const tokens = await this.createAddToCalendarTokens(userId);
    
    return this.executeAddToCalendar({
      user_id: userId,
      email_token: tokens.email_token,
      calendar_token: tokens.calendar_token,
      google_access_token: googleAccessToken,
      action: 'manual_event',
      event_details: eventDetails
    });
  }

  // MailerPanda Agent Methods
  async getMailerPandaRequirements() {
    return this.makeRequest('/agents/mailerpanda/requirements');
  }

  // Execute MailerPanda agent
  async executeMailerPanda(request: MailerPandaExecuteRequest): Promise<MailerPandaResponse> {
    return this.makeRequest('/agents/mailerpanda/execute', {
      method: 'POST',
      body: JSON.stringify({
        ...request,
        ai_provider: this.aiConfig.provider,
        ai_model: this.aiConfig.model
      }),
    });
  }

  // Approve/reject MailerPanda campaign
  async approveMailerPanda(request: ApprovalRequest): Promise<MailerPandaResponse> {
    return this.makeRequest('/agents/mailerpanda/approve', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Get campaign session status
  async getCampaignSession(campaignId: string): Promise<SessionResponse> {
    return this.makeRequest(`/agents/mailerpanda/session/${campaignId}`);
  }

  // Helper method to create all required consent tokens for MailerPanda
  async createMailerPandaTokens(userId: string): Promise<Record<string, string>> {
    const scopes = [
      'vault.read.email',
      'vault.write.email', 
      'vault.read.file',
      'vault.write.file',
      'custom.temporary'
    ];

    const tokens: Record<string, string> = {};
    
    for (const scope of scopes) {
      try {
        const response = await this.createConsentToken({
          user_id: userId,
          agent_id: 'agent_mailerpanda',
          scope: scope
        });
        tokens[scope] = response.token;
      } catch (error) {
        console.error(`Failed to create token for scope ${scope}:`, error);
        throw new Error(`Failed to create consent token for ${scope}`);
      }
    }

    return tokens;
  }

  // Chat Agent Methods
  async getChatAgentStatus(): Promise<ChatAgentStatusResponse> {
    return this.makeRequest('/agents/chat/status');
  }

  // Send chat message
  async sendChatMessage(request: ChatMessageRequest): Promise<ChatMessageResponse> {
    return this.makeRequest('/agents/chat/message', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Get conversation history
  async getChatHistory(userId: string, sessionId: string): Promise<ConversationHistoryResponse> {
    return this.makeRequest(`/agents/chat/history/${sessionId}?user_id=${userId}`);
  }

  // Get user chat sessions
  async getUserChatSessions(userId: string): Promise<UserSessionsResponse> {
    return this.makeRequest(`/agents/chat/sessions/${userId}`);
  }

  // Helper method to create Chat Agent consent token
  async createChatTokens(userId: string): Promise<Record<string, string>> {
    const response = await this.createConsentToken({
      user_id: userId,
      agent_id: 'agent_chat',
      scope: 'custom.temporary'
    });

    return {
      'custom.temporary': response.token
    };
  }

  // Simplified chat method with automatic token management
  async sendChatMessageWithAutoTokens(
    userId: string, 
    message: string, 
    sessionId?: string
  ): Promise<ChatMessageResponse> {
    const tokens = await this.createChatTokens(userId);
    
    return this.sendChatMessage({
      user_id: userId,
      message: message,
      consent_tokens: tokens,
      session_id: sessionId
    });
  }

  // Email verification method
  async verifyEmails(emails: string[]): Promise<{ results: Record<string, boolean>; valid_count: number; invalid_count: number }> {
    return this.makeRequest('/agents/mailerpanda/verify-emails', {
      method: 'POST',
      body: JSON.stringify({ emails }),
    });
  }

  // Connection and status methods
  async testConnection(): Promise<{ connected: boolean; agents: any[]; status: string }> {
    try {
      const [health, agents] = await Promise.all([
        this.checkHealth(),
        this.listAgents()
      ]);

      return {
        connected: health.status === 'healthy',
        agents: agents || [],
        status: health.status
      };
    } catch (error) {
      console.error('HushMCP API connection test failed:', error);
      return {
        connected: false,
        agents: [],
        status: 'error'
      };
    }
  }

  async isAgentAvailable(agentId: string): Promise<boolean> {
    try {
      const agents = await this.listAgents();
      return agents.some((agent: any) => agent.id === agentId);
    } catch {
      return false;
    }
  }

  // ============================================================================
  // RELATIONSHIP MEMORY AGENT METHODS
  // ============================================================================

  // Execute Relationship Memory agent
  async executeRelationshipMemory(request: {
    user_id: string;
    tokens: Record<string, string>;
    user_input: string;
    vault_key?: string;
    is_startup?: boolean;
    gemini_api_key?: string;
  }) {
    return this.makeRequest('/agents/relationship_memory/execute', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Proactive relationship check
  async relationshipProactiveCheck(request: {
    user_id: string;
    tokens: Record<string, string>;
    vault_key?: string;
  }) {
    return this.makeRequest('/agents/relationship_memory/proactive', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Start chat session
  async startRelationshipChat(request: {
    user_id: string;
    tokens: Record<string, string>;
    vault_key?: string;
    session_name?: string;
    gemini_api_key?: string;
  }) {
    return this.makeRequest('/agents/relationship_memory/chat/start', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Send chat message
  async sendRelationshipChatMessage(request: {
    session_id: string;
    message: string;
  }) {
    return this.makeRequest('/agents/relationship_memory/chat/message', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Get chat history
  async getRelationshipChatHistory(sessionId: string) {
    return this.makeRequest(`/agents/relationship_memory/chat/${sessionId}/history`);
  }

  // End chat session
  async endRelationshipChat(sessionId: string) {
    return this.makeRequest(`/agents/relationship_memory/chat/${sessionId}`, {
      method: 'DELETE',
    });
  }

  // List all chat sessions
  async listRelationshipChatSessions() {
    return this.makeRequest('/agents/relationship_memory/chat/sessions');
  }

  // Helper to create Relationship Memory tokens
  async createRelationshipTokens(userId: string): Promise<Record<string, string>> {
    const scopes = [
      'vault.read.contacts',
      'vault.write.contacts',
      'vault.read.memory',
      'vault.write.memory',
      'vault.read.reminder',
      'vault.write.reminder'
    ];

    const tokens: Record<string, string> = {};
    
    for (const scope of scopes) {
      const response = await this.createConsentToken({
        user_id: userId,
        agent_id: 'agent_relationship_memory',
        scope: scope
      });
      tokens[scope] = response.token;
    }

    return tokens;
  }

  // ============================================================================
  // CHANDUFINANCE AGENT METHODS
  // ============================================================================

  // Execute ChanduFinance agent
  async executeChanduFinance(request: {
    user_id: string;
    token: string;
    command: string;
    full_name?: string;
    age?: number;
    occupation?: string;
    monthly_income?: number;
    monthly_expenses?: number;
    current_savings?: number;
    current_debt?: number;
    investment_budget?: number;
    risk_tolerance?: string;
    investment_experience?: string;
    goal_name?: string;
    target_amount?: number;
    target_date?: string;
    priority?: string;
    ticker?: string;
    topic?: string;
    complexity?: string;
    gemini_api_key?: string;
  }) {
    return this.makeRequest('/agents/chandufinance/execute', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Get ChanduFinance status
  async getChanduFinanceStatus() {
    return this.makeRequest('/agents/chandufinance/status');
  }

  // Helper to create ChanduFinance token
  async createChanduFinanceToken(userId: string): Promise<string> {
    const response = await this.createConsentToken({
      user_id: userId,
      agent_id: 'agent_chandufinance',
      scope: 'vault.read.finance'
    });
    return response.token;
  }

  // ============================================================================
  // RESEARCH AGENT METHODS
  // ============================================================================

  // Search arXiv papers
  async searchArxivPapers(request: {
    user_id: string;
    consent_tokens: Record<string, string>;
    query: string;
  }) {
    return this.makeRequest('/agents/research/search/arxiv', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Upload research paper
  async uploadResearchPaper(
    userId: string,
    consentTokens: Record<string, string>,
    file: File
  ) {
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('consent_tokens', JSON.stringify(consentTokens));
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/agents/research/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Get paper summary
  async getResearchPaperSummary(
    paperId: string,
    userId: string,
    consentTokens: Record<string, string>
  ) {
    const params = new URLSearchParams({
      user_id: userId,
      consent_tokens: JSON.stringify(consentTokens),
    });
    return this.makeRequest(`/agents/research/paper/${paperId}/summary?${params}`);
  }

  // Process text snippet
  async processResearchSnippet(request: {
    paper_id: string;
    user_id: string;
    consent_tokens: Record<string, string>;
    text: string;
    instruction: string;
  }) {
    return this.makeRequest(`/agents/research/paper/${request.paper_id}/process/snippet`, {
      method: 'POST',
      body: JSON.stringify({
        user_id: request.user_id,
        consent_tokens: request.consent_tokens,
        text: request.text,
        instruction: request.instruction,
      }),
    });
  }

  // Save research notes
  async saveResearchNotes(request: {
    user_id: string;
    consent_tokens: Record<string, string>;
    paper_id: string;
    editor_id: string;
    content: string;
  }) {
    return this.makeRequest('/agents/research/session/notes', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Helper to create Research tokens
  async createResearchTokens(userId: string): Promise<Record<string, string>> {
    const scopes = [
      'custom.temporary',
      'vault.read.file',
      'vault.write.file'
    ];

    const tokens: Record<string, string> = {};
    
    for (const scope of scopes) {
      const response = await this.createConsentToken({
        user_id: userId,
        agent_id: 'agent_research',
        scope: scope
      });
      tokens[scope] = response.token;
    }

    return tokens;
  }

  // ============================================================================
  // MAILERPANDA ENHANCEMENTS
  // ============================================================================

  // Mass email with context toggle
  async sendMassEmailWithContext(request: {
    user_id: string;
    user_input: string;
    consent_tokens: Record<string, string>;
    use_context_personalization: boolean;
    excel_file_data?: string; // Base64 encoded
    excel_file_name?: string;
    mode?: string;
    personalization_mode?: string;
    google_api_key?: string;
    mailjet_api_key?: string;
    mailjet_api_secret?: string;
  }) {
    return this.makeRequest('/agents/mailerpanda/mass-email', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Analyze Excel for personalization
  async analyzeExcelForPersonalization(excelFileData: string) {
    return this.makeRequest('/agents/mailerpanda/analyze-excel', {
      method: 'POST',
      body: JSON.stringify({ excel_file_data: excelFileData }),
    });
  }

  // Approve with feedback
  async approveMailerPandaWithFeedback(request: {
    user_id: string;
    campaign_id: string;
    action: 'approve' | 'reject' | 'modify' | 'regenerate';
    feedback?: string;
  }) {
    return this.makeRequest('/agents/mailerpanda/approve', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }
}

export const hushMcpApi = new HushMcpApiService();
