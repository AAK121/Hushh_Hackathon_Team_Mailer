// HushMCP Agent API Service
export interface ConsentTokenRequest {
  user_id: string;
  agent_id: string;
  scope: string;
}

export interface ConsentTokenResponse {
  token: string;
  expires_at: number;
  scope: string;
}

export interface AddToCalendarRequest {
  user_id: string;
  email_token: string;
  calendar_token: string;
  google_access_token: string;
  action: 'comprehensive_analysis' | 'manual_event' | 'analyze_only';
  confidence_threshold?: number;
  max_emails?: number;
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
  }>;
  processing_time: number;
  trust_links?: string[];
  errors?: string[];
}

export interface MailerPandaRequest {
  user_id: string;
  user_input: string;
  mode: 'interactive' | 'headless';
  consent_tokens: Record<string, string>;
  sender_email?: string;
  recipient_emails?: string[];
  require_approval?: boolean;
  use_ai_generation?: boolean;
}

export interface MailerPandaResponse {
  status: 'success' | 'error' | 'awaiting_approval' | 'completed';
  user_id: string;
  mode: string;
  campaign_id?: string;
  email_template?: {
    subject: string;
    body: string;
  };
  requires_approval?: boolean;
  approval_status?: string;
  feedback_required?: boolean;
  processing_time: number;
  emails_sent?: number;
  recipients_processed?: number;
  errors?: string[];
}

export interface MailerPandaApprovalRequest {
  user_id: string;
  campaign_id: string;
  action: 'approve' | 'reject' | 'modify' | 'regenerate';
  feedback?: string;
}

class HushMCPAgentAPI {
  private baseURL: string;

  constructor() {
    this.baseURL = import.meta.env.VITE_HUSHMCP_API_URL || 'http://127.0.0.1:8001';
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  // Health and Status
  async getHealth(): Promise<{ status: string; timestamp: string; service: string }> {
    return this.request('/health');
  }

  async getAgents(): Promise<Array<{ id: string; name: string; version: string }>> {
    return this.request('/agents');
  }

  // Consent Token Management
  async createConsentToken(request: ConsentTokenRequest): Promise<ConsentTokenResponse> {
    return this.request('/consent/token', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async createAddToCalendarTokens(userId: string): Promise<Record<string, string>> {
    const emailToken = await this.createConsentToken({
      user_id: userId,
      agent_id: 'agent_addtocalendar',
      scope: 'vault.read.email',
    });

    const calendarToken = await this.createConsentToken({
      user_id: userId,
      agent_id: 'agent_addtocalendar',
      scope: 'vault.write.calendar',
    });

    return {
      email_token: emailToken.token,
      calendar_token: calendarToken.token,
    };
  }

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
      const token = await this.createConsentToken({
        user_id: userId,
        agent_id: 'agent_mailerpanda',
        scope: scope,
      });
      tokens[scope] = token.token;
    }

    return tokens;
  }

  // AddToCalendar Agent
  async getAddToCalendarRequirements(): Promise<any> {
    return this.request('/agents/addtocalendar/requirements');
  }

  async executeAddToCalendar(request: AddToCalendarRequest): Promise<AddToCalendarResponse> {
    return this.request('/agents/addtocalendar/execute', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // MailerPanda Agent
  async getMailerPandaRequirements(): Promise<any> {
    return this.request('/agents/mailerpanda/requirements');
  }

  async executeMailerPanda(request: MailerPandaRequest): Promise<MailerPandaResponse> {
    return this.request('/agents/mailerpanda/execute', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async approveMailerPanda(request: MailerPandaApprovalRequest): Promise<MailerPandaResponse> {
    return this.request('/agents/mailerpanda/approve', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getMailerPandaSession(campaignId: string): Promise<any> {
    return this.request(`/agents/mailerpanda/session/${campaignId}`);
  }

  // Helper Methods
  async isHealthy(): Promise<boolean> {
    try {
      const health = await this.getHealth();
      return health.status === 'healthy';
    } catch {
      return false;
    }
  }

  async testConnection(): Promise<{ connected: boolean; agents: any[] }> {
    try {
      const [health, agents] = await Promise.all([
        this.getHealth(),
        this.getAgents(),
      ]);
      
      return {
        connected: health.status === 'healthy',
        agents,
      };
    } catch (error) {
      console.error('HushMCP API connection test failed:', error);
      return {
        connected: false,
        agents: [],
      };
    }
  }
}

export const hushMCPAgentAPI = new HushMCPAgentAPI();
export default hushMCPAgentAPI;
