// Mass Mailing API service for MailerPanda Agent
// This service calls the actual MailerPanda backend endpoints
// Aligned with the endpoints used in MailerPandaUI component

export type MassEmailRequest = {
  user_id: string;
  user_input: string;
  excel_file_data?: string;
  excel_file_name?: string;
  mode: 'interactive' | 'headless';
  use_context_personalization: boolean;
  personalization_mode: 'smart' | 'conservative' | 'aggressive';
  google_api_key?: string;
  mailjet_api_key?: string;
  mailjet_api_secret?: string;
  consent_tokens: Record<string, string>;
};

export type MassEmailResponse = {
  status: string;
  user_id: string;
  campaign_id?: string;
  context_personalization_enabled: boolean;
  excel_analysis: {
    file_uploaded: boolean;
    total_contacts: number;
    columns_found: string[];
    description_column_exists: boolean;
    contacts_with_descriptions: number;
    context_toggle_status: string;
  };
  email_template?: {
    subject: string;
    body: string;
  };
  emails_sent?: number;
  personalized_count?: number;
  standard_count?: number;
  requires_approval?: boolean;
  approval_status?: string;
  processing_time?: number;
  errors?: string[];
};

export type ApprovalRequest = {
  user_id: string;
  campaign_id: string;
  action: 'approve' | 'reject' | 'modify';
  feedback?: string;
};

export type MassMailBatch = {
  id: string;
  sourceType: 'file' | 'sheet';
  createdAt: string;
  status: 'processing' | 'ready' | 'sending' | 'completed' | 'failed';
  total: number;
  processed: number;
};

export type DraftEmail = {
  id: string;
  to: string;
  subject: string;
  preview: string;
  body: string;
};

const BASE_URL = `${import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_HUSHMCP_API_URL || 'https://hush-backend-sepia.vercel.app'}/agents/mailerpanda`;

async function safeFetch(input: RequestInfo, init?: RequestInit) {
  try {
    const res = await fetch(input, init);
    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`HTTP ${res.status}: ${errorText}`);
    }
    return await res.json();
  } catch (err) {
    console.error('MailerPanda API error:', err);
    throw err;
  }
}

export const massMailApi = {
  // Create mass email campaign
  async createCampaign(request: MassEmailRequest): Promise<MassEmailResponse> {
    const data = await safeFetch(`${BASE_URL}/mass-email`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    return data as MassEmailResponse;
  },

  // Approve/reject/modify campaign
  async handleApproval(request: ApprovalRequest): Promise<MassEmailResponse> {
    const data = await safeFetch(`${BASE_URL}/mass-email/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    return data as MassEmailResponse;
  },

  // Convert file to base64 for backend
  fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const result = reader.result as string;
        // Remove the data URL prefix to get just the base64 data
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = error => reject(error);
    });
  },

  // Legacy methods for backward compatibility (now deprecated)
  async uploadFile(_file: File): Promise<{ batchId: string }> {
    console.warn('massMailApi.uploadFile is deprecated. Use createCampaign instead.');
    return { batchId: `legacy-batch-${Date.now()}` };
  },

  async submitSheetLink(_url: string): Promise<{ batchId: string }> {
    console.warn('massMailApi.submitSheetLink is deprecated. Use createCampaign instead.');
    return { batchId: `legacy-batch-${Date.now()}` };
  },

  async getBatch(batchId: string): Promise<MassMailBatch> {
    console.warn('massMailApi.getBatch is deprecated.');
    return {
      id: batchId,
      sourceType: 'file',
      createdAt: new Date().toISOString(),
      status: 'ready',
      total: 0,
      processed: 0,
    };
  },

  async listDrafts(_batchId: string): Promise<DraftEmail[]> {
    console.warn('massMailApi.listDrafts is deprecated.');
    return [];
  },

  async approveDraft(_draftId: string): Promise<{ ok: true }> {
    console.warn('massMailApi.approveDraft is deprecated. Use handleApproval instead.');
    return { ok: true };
  },

  async rejectDraft(_draftId: string): Promise<{ ok: true }> {
    console.warn('massMailApi.rejectDraft is deprecated. Use handleApproval instead.');
    return { ok: true };
  },
};
