/**
 * User Vault API Service
 * 
 * Provides secure user-specific data storage with encryption.
 * Each user has their own encryption keys managed by the backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_HUSHMCP_API_URL || 'https://hush-backend-sepia.vercel.app';

export interface UserVaultData {
  [key: string]: any;
}

export interface VaultResponse {
  status: string;
  user_id: string;
  vault_name: string;
  operation: string;
  result?: any;
  message: string;
  processing_time: number;
  errors?: string[];
}

export interface VaultInfo {
  vault_name: string;
  description: string;
  created_at: string;
  key_count: number;
  encrypted: boolean;
  error?: string;
}

export interface UserVaultInfoResponse {
  status: string;
  user_id: string;
  operation: string;
  result: {
    vaults: VaultInfo[];
    total_vaults: number;
    encryption_enabled: boolean;
  };
  message: string;
  processing_time: number;
  errors?: string[];
}

/**
 * Create a new user vault with unique encryption keys
 */
export async function createUserVault(
  userId: string,
  vaultName: string = 'default',
  description?: string
): Promise<VaultResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/vault/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        vault_name: vaultName,
        description: description
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error creating user vault:', error);
    throw error;
  }
}

/**
 * Store encrypted data in user's vault
 */
export async function storeUserData(
  userId: string,
  key: string,
  data: UserVaultData,
  vaultName: string = 'default'
): Promise<VaultResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/vault/store`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        key: key,
        data: data,
        vault_name: vaultName
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error storing user data:', error);
    throw error;
  }
}

/**
 * Retrieve encrypted data from user's vault
 */
export async function retrieveUserData(
  userId: string,
  key: string,
  vaultName: string = 'default'
): Promise<VaultResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/vault/retrieve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        key: key,
        vault_name: vaultName
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error retrieving user data:', error);
    throw error;
  }
}

/**
 * Delete data from user's vault
 */
export async function deleteUserData(
  userId: string,
  key: string,
  vaultName: string = 'default'
): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/vault/delete?user_id=${userId}&key=${key}&vault_name=${vaultName}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error deleting user data:', error);
    throw error;
  }
}

/**
 * List all keys in user's vault
 */
export async function listUserVaultKeys(
  userId: string,
  vaultName: string = 'default'
): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/vault/list?user_id=${userId}&vault_name=${vaultName}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error listing vault keys:', error);
    throw error;
  }
}

/**
 * Get comprehensive information about user's vaults
 */
export async function getUserVaultInfo(userId: string): Promise<UserVaultInfoResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/vault/user/${userId}/info`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error getting user vault info:', error);
    throw error;
  }
}

/**
 * Utility function to safely store user preferences
 */
export async function storeUserPreferences(
  userId: string,
  preferences: Record<string, any>,
  vaultName: string = 'default'
): Promise<VaultResponse> {
  return storeUserData(userId, 'user_preferences', preferences, vaultName);
}

/**
 * Utility function to retrieve user preferences
 */
export async function getUserPreferences(
  userId: string,
  vaultName: string = 'default'
): Promise<Record<string, any> | null> {
  try {
    const response = await retrieveUserData(userId, 'user_preferences', vaultName);
    if (response.status === 'success' && response.result?.data) {
      return response.result.data;
    }
    return null;
  } catch (error) {
    console.error('Error getting user preferences:', error);
    return null;
  }
}

/**
 * Utility function to store user API keys securely
 */
export async function storeUserApiKeys(
  userId: string,
  apiKeys: Record<string, string>,
  vaultName: string = 'default'
): Promise<VaultResponse> {
  return storeUserData(userId, 'api_keys', apiKeys, vaultName);
}

/**
 * Utility function to retrieve user API keys
 */
export async function getUserApiKeys(
  userId: string,
  vaultName: string = 'default'
): Promise<Record<string, string> | null> {
  try {
    const response = await retrieveUserData(userId, 'api_keys', vaultName);
    if (response.status === 'success' && response.result?.data) {
      return response.result.data;
    }
    return null;
  } catch (error) {
    console.error('Error getting user API keys:', error);
    return null;
  }
}

/**
 * Utility function to store user agent configurations
 */
export async function storeAgentConfig(
  userId: string,
  agentId: string,
  config: Record<string, any>,
  vaultName: string = 'default'
): Promise<VaultResponse> {
  return storeUserData(userId, `agent_config_${agentId}`, config, vaultName);
}

/**
 * Utility function to retrieve user agent configurations
 */
export async function getAgentConfig(
  userId: string,
  agentId: string,
  vaultName: string = 'default'
): Promise<Record<string, any> | null> {
  try {
    const response = await retrieveUserData(userId, `agent_config_${agentId}`, vaultName);
    if (response.status === 'success' && response.result?.data) {
      return response.result.data;
    }
    return null;
  } catch (error) {
    console.error('Error getting agent config:', error);
    return null;
  }
}

/**
 * Utility function to store user session data
 */
export async function storeUserSession(
  userId: string,
  sessionId: string,
  sessionData: Record<string, any>,
  vaultName: string = 'default'
): Promise<VaultResponse> {
  return storeUserData(userId, `session_${sessionId}`, sessionData, vaultName);
}

/**
 * Utility function to retrieve user session data
 */
export async function getUserSession(
  userId: string,
  sessionId: string,
  vaultName: string = 'default'
): Promise<Record<string, any> | null> {
  try {
    const response = await retrieveUserData(userId, `session_${sessionId}`, vaultName);
    if (response.status === 'success' && response.result?.data) {
      return response.result.data;
    }
    return null;
  } catch (error) {
    console.error('Error getting user session:', error);
    return null;
  }
}

export default {
  createUserVault,
  storeUserData,
  retrieveUserData,
  deleteUserData,
  listUserVaultKeys,
  getUserVaultInfo,
  storeUserPreferences,
  getUserPreferences,
  storeUserApiKeys,
  getUserApiKeys,
  storeAgentConfig,
  getAgentConfig,
  storeUserSession,
  getUserSession
};
