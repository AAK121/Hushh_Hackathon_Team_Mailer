/**
 * API Configuration for HushMCP Agent Platform
 * 
 * This file centralizes all API endpoints and configuration
 * to properly connect the frontend with the pda_mailer backend
 */

// Get API base URL from environment or use default
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001';

// API Configuration object
export const apiConfig = {
  baseUrl: API_BASE_URL,
  
  // Health check endpoint
  health: `${API_BASE_URL}/health`,
  
  // Root endpoint
  root: `${API_BASE_URL}/`,
  
  // Agent listing and requirements
  agents: {
    list: `${API_BASE_URL}/agents`,
    requirements: (agentId: string) => `${API_BASE_URL}/agents/${agentId}/requirements`,
  },
  
  // Consent token endpoints
  consent: {
    create: `${API_BASE_URL}/consent/token`,
    validate: `${API_BASE_URL}/consent/validate`,
  },
  
  // AddToCalendar Agent endpoints
  addToCalendar: {
    execute: `${API_BASE_URL}/agents/addtocalendar/execute`,
    status: `${API_BASE_URL}/agents/addtocalendar/status`,
  },
  
  // MailerPanda Agent endpoints
  mailerPanda: {
    execute: `${API_BASE_URL}/agents/mailerpanda/execute`,
    approve: `${API_BASE_URL}/agents/mailerpanda/approve`,
    status: `${API_BASE_URL}/agents/mailerpanda/status`,
    session: (campaignId: string) => `${API_BASE_URL}/agents/mailerpanda/session/${campaignId}`,
    massEmail: `${API_BASE_URL}/agents/mailerpanda/mass-email`,
    analyzeExcel: `${API_BASE_URL}/agents/mailerpanda/analyze-excel`,
  },
  
  // ChanduFinance Agent endpoints
  chanduFinance: {
    execute: `${API_BASE_URL}/agents/chandufinance/execute`,
    status: `${API_BASE_URL}/agents/chandufinance/status`,
  },
  
  // Relationship Memory Agent endpoints
  relationshipMemory: {
    execute: `${API_BASE_URL}/agents/relationship_memory/execute`,
    proactive: `${API_BASE_URL}/agents/relationship_memory/proactive`,
    status: `${API_BASE_URL}/agents/relationship_memory/status`,
    chat: {
      start: `${API_BASE_URL}/agents/relationship_memory/chat/start`,
      message: `${API_BASE_URL}/agents/relationship_memory/chat/message`,
      history: (sessionId: string) => `${API_BASE_URL}/agents/relationship_memory/chat/${sessionId}/history`,
      end: (sessionId: string) => `${API_BASE_URL}/agents/relationship_memory/chat/${sessionId}`,
      sessions: `${API_BASE_URL}/agents/relationship_memory/chat/sessions`,
    },
  },
  
  // Research Agent endpoints
  research: {
    searchArxiv: `${API_BASE_URL}/agents/research/search/arxiv`,
    upload: `${API_BASE_URL}/agents/research/upload`,
    summary: (paperId: string) => `${API_BASE_URL}/agents/research/paper/${paperId}/summary`,
    processSnippet: (paperId: string) => `${API_BASE_URL}/agents/research/paper/${paperId}/process/snippet`,
    saveNotes: `${API_BASE_URL}/agents/research/session/notes`,
    status: `${API_BASE_URL}/agents/research/status`,
  },
};

// Default headers for API requests
export const defaultHeaders = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
};

// Helper function to check if backend is available
export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(apiConfig.health, {
      method: 'GET',
      headers: defaultHeaders,
    });
    return response.ok;
  } catch (error) {
    console.error('Backend health check failed:', error);
    return false;
  }
}

// Helper function to make API requests with error handling
export async function apiRequest<T = any>(
  url: string,
  options: RequestInit = {}
): Promise<{ success: boolean; data?: T; error?: string }> {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API request failed: ${response.status} - ${errorText}`);
    }
    
    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    console.error('API request error:', error);
    return { 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error occurred' 
    };
  }
}

// Export default for convenience
export default apiConfig;
