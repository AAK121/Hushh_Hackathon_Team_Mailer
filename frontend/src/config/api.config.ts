/**
 * API Configuration for HushMCP Agent Platform
 * 
 * This file centralizes all API endpoints and configuration
 * to properly connect the frontend with both the existing backend
 * and the new microservices architecture
 */

// Get API base URL from environment or use default (existing backend)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_HUSHMCP_API_URL || 'https://hush-backend-khqvdh6ob-jarvis-635b16ce.vercel.app';

// Microservices URLs (can be overridden by environment variables)
const GATEWAY_URL = import.meta.env.VITE_GATEWAY_URL || 'https://hush-backend-khqvdh6ob-jarvis-635b16ce.vercel.app';
const ADDTOCALENDAR_URL = import.meta.env.VITE_ADDTOCALENDAR_URL || 'https://hush-backend-khqvdh6ob-jarvis-635b16ce.vercel.app';
const MAILERPANDA_URL = import.meta.env.VITE_MAILERPANDA_URL || 'https://hush-backend-khqvdh6ob-jarvis-635b16ce.vercel.app';
const RESEARCH_URL = import.meta.env.VITE_RESEARCH_URL || 'https://hush-backend-khqvdh6ob-jarvis-635b16ce.vercel.app';
const FINANCE_URL = import.meta.env.VITE_FINANCE_URL || 'https://hush-backend-khqvdh6ob-jarvis-635b16ce.vercel.app';
const MEMORY_URL = import.meta.env.VITE_MEMORY_URL || 'https://hush-backend-khqvdh6ob-jarvis-635b16ce.vercel.app';

// Configuration mode: 'backend' | 'microservices' | 'hybrid'
const API_MODE = import.meta.env.VITE_API_MODE || 'hybrid';

// API Configuration object
export const apiConfig = {
  mode: API_MODE,
  baseUrl: API_BASE_URL,
  gatewayUrl: GATEWAY_URL,
  
  // Health check endpoints
  health: {
    backend: `${API_BASE_URL}/health`,
    gateway: `${GATEWAY_URL}/health`,
    services: {
      addtocalendar: `${ADDTOCALENDAR_URL}/health`,
      mailerpanda: `${MAILERPANDA_URL}/health`,
      research: `${RESEARCH_URL}/health`,
      finance: `${FINANCE_URL}/health`,
      memory: `${MEMORY_URL}/health`,
    }
  },
  
  // Root endpoints
  root: {
    backend: `${API_BASE_URL}/`,
    gateway: `${GATEWAY_URL}/`,
  },
  
  // Agent listing and requirements (existing backend)
  agents: {
    list: `${API_BASE_URL}/agents`,
    requirements: (agentId: string) => `${API_BASE_URL}/agents/${agentId}/requirements`,
  },
  
  // Consent token endpoints
  consent: {
    create: `${API_BASE_URL}/consent/token`,
    validate: `${API_BASE_URL}/consent/validate`,
  },
  
  // AddToCalendar Agent endpoints (with both backend and microservice options)
  addToCalendar: {
    // Existing backend endpoints
    execute: `${API_BASE_URL}/agents/addtocalendar/execute`,
    status: `${API_BASE_URL}/agents/addtocalendar/status`,
    // New microservice endpoints
    microservice: {
      execute: `${ADDTOCALENDAR_URL}/execute`,
      add_event: `${ADDTOCALENDAR_URL}/add_event`,
      status: `${ADDTOCALENDAR_URL}/status`,
    }
  },
  
  // MailerPanda Agent endpoints (with both backend and microservice options)
  mailerPanda: {
    // Existing backend endpoints
    execute: `${API_BASE_URL}/agents/mailerpanda/execute`,
    approve: `${API_BASE_URL}/agents/mailerpanda/approve`,
    status: `${API_BASE_URL}/agents/mailerpanda/status`,
    session: (campaignId: string) => `${API_BASE_URL}/agents/mailerpanda/session/${campaignId}`,
    massEmail: `${API_BASE_URL}/agents/mailerpanda/mass-email`,
    analyzeExcel: `${API_BASE_URL}/agents/mailerpanda/analyze-excel`,
    // New microservice endpoints
    microservice: {
      execute: `${MAILERPANDA_URL}/execute`,
      upload: `${MAILERPANDA_URL}/upload`,
      process: `${MAILERPANDA_URL}/process`,
      analyze: `${MAILERPANDA_URL}/analyze`,
      status: `${MAILERPANDA_URL}/status`,
    }
  },
  
  // ChanduFinance Agent endpoints (with both backend and microservice options)
  chanduFinance: {
    // Existing backend endpoints
    execute: `${API_BASE_URL}/agents/chandufinance/execute`,
    status: `${API_BASE_URL}/agents/chandufinance/status`,
    // New microservice endpoints
    microservice: {
      execute: `${FINANCE_URL}/execute`,
      search: `${FINANCE_URL}/search`,
      upload: `${FINANCE_URL}/upload`,
      status: `${FINANCE_URL}/status`,
    }
  },
  
  // Relationship Memory Agent endpoints (with both backend and microservice options)
  relationshipMemory: {
    // Existing backend endpoints
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
    // New microservice endpoints
    microservice: {
      execute: `${MEMORY_URL}/execute`,
      proactive: `${MEMORY_URL}/proactive`,
      status: `${MEMORY_URL}/status`,
      chat: {
        start: `${MEMORY_URL}/chat/start`,
        message: `${MEMORY_URL}/chat/message`,
        history: (sessionId: string) => `${MEMORY_URL}/chat/${sessionId}/history`,
        end: (sessionId: string) => `${MEMORY_URL}/chat/${sessionId}`,
        sessions: `${MEMORY_URL}/chat/sessions`,
      }
    }
  },
  
  // Research Agent endpoints (with both backend and microservice options)
  research: {
    // Existing backend endpoints
    searchArxiv: `${API_BASE_URL}/agents/research/search/arxiv`,
    upload: `${API_BASE_URL}/agents/research/upload`,
    summary: (paperId: string) => `${API_BASE_URL}/agents/research/paper/${paperId}/summary`,
    processSnippet: (paperId: string) => `${API_BASE_URL}/agents/research/paper/${paperId}/process/snippet`,
    saveNotes: `${API_BASE_URL}/agents/research/session/notes`,
    status: `${API_BASE_URL}/agents/research/status`,
    // New microservice endpoints
    microservice: {
      searchArxiv: `${RESEARCH_URL}/search/arxiv`,
      upload: `${RESEARCH_URL}/upload`,
      summary: (paperId: string) => `${RESEARCH_URL}/paper/${paperId}/summary`,
      processSnippet: (paperId: string) => `${RESEARCH_URL}/paper/${paperId}/process/snippet`,
      saveNotes: `${RESEARCH_URL}/session/notes`,
      status: `${RESEARCH_URL}/status`,
    }
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
    const response = await fetch(apiConfig.health.backend, {
      method: 'GET',
      headers: defaultHeaders,
    });
    return response.ok;
  } catch (error) {
    console.error('Backend health check failed:', error);
    return false;
  }
}

// Helper function to check microservices health
export async function checkMicroservicesHealth(): Promise<{[key: string]: boolean}> {
  const healthResults: {[key: string]: boolean} = {};
  
  // Check gateway health
  try {
    const response = await fetch(apiConfig.health.gateway, {
      method: 'GET',
      headers: defaultHeaders,
    });
    healthResults.gateway = response.ok;
  } catch (error) {
    console.error('Gateway health check failed:', error);
    healthResults.gateway = false;
  }
  
  // Check individual services
  for (const [serviceName, url] of Object.entries(apiConfig.health.services)) {
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: defaultHeaders,
      });
      healthResults[serviceName] = response.ok;
    } catch (error) {
      console.error(`${serviceName} health check failed:`, error);
      healthResults[serviceName] = false;
    }
  }
  
  return healthResults;
}

// Helper function to get the appropriate endpoint based on mode
export function getEndpoint(agentName: string, endpointName: string, ...args: any[]): string {
  const agent = (apiConfig as any)[agentName];
  
  if (!agent) {
    throw new Error(`Agent ${agentName} not found in configuration`);
  }
  
  // If mode is microservices and microservice endpoint exists, use it
  if (API_MODE === 'microservices' && agent.microservice && agent.microservice[endpointName]) {
    const endpoint = agent.microservice[endpointName];
    return typeof endpoint === 'function' ? endpoint(...args) : endpoint;
  }
  
  // If mode is backend or fallback, use backend endpoint
  const endpoint = agent[endpointName];
  if (endpoint) {
    return typeof endpoint === 'function' ? endpoint(...args) : endpoint;
  }
  
  // If mode is hybrid, try microservice first, then backend
  if (API_MODE === 'hybrid') {
    if (agent.microservice && agent.microservice[endpointName]) {
      const microEndpoint = agent.microservice[endpointName];
      return typeof microEndpoint === 'function' ? microEndpoint(...args) : microEndpoint;
    }
    if (agent[endpointName]) {
      const backendEndpoint = agent[endpointName];
      return typeof backendEndpoint === 'function' ? backendEndpoint(...args) : backendEndpoint;
    }
  }
  
  throw new Error(`Endpoint ${endpointName} not found for agent ${agentName}`);
}

// Helper function to get all available services
export function getAvailableServices(): string[] {
  const services = ['backend'];
  
  if (API_MODE === 'microservices' || API_MODE === 'hybrid') {
    services.push('gateway', 'addtocalendar', 'mailerpanda', 'research', 'finance', 'memory');
  }
  
  return services;
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
