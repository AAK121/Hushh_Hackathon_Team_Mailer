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

const BASE_URL = 'http://127.0.0.1:8001/agents/mailerpanda';

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

  // Get default consent tokens (for demo purposes)
  getDefaultConsentTokens(): Record<string, string> {
    return {
      'vault.read.email': 'HCT:ZnJvbnRlbmRfdXNlcl8xMjN8bWFpbGVycGFuZGF8dmF1bHQucmVhZC5lbWFpbHwxNzU1OTQ2MzA5NjU0fDE3NTYwMzI3MDk2NTQ=.e98cb6fe90a9d4a6ded5bf2a37b25028d1ea82a7e5dde4223552a312dba75b36',
      'vault.write.email': 'HCT:ZnJvbnRlbmRfdXNlcl8xMjN8bWFpbGVycGFuZGF8dmF1bHQud3JpdGUuZW1haWx8MTc1NTk0NjMwOTY1NHwxNzU2MDMyNzA5NjU0.107cf985c5c82413b218a436e8206856b1f982e37a70d6c5ab2fabd97c0ef60e',
      'vault.read.file': 'HCT:ZnJvbnRlbmRfdXNlcl8xMjN8bWFpbGVycGFuZGF8dmF1bHQucmVhZC5maWxlfDE3NTU5NDYzMDk2NTR8MTc1NjAzMjcwOTY1NA==.5549616fd68e1a507ff89e18692134c8301d40ec077df18e62b803059ca17642',
      'vault.write.file': 'HCT:ZnJvbnRlbmRfdXNlcl8xMjN8bWFpbGVycGFuZGF8dmF1bHQud3JpdGUuZmlsZXwxNzU1OTQ2MzA5NjU1fDE3NTYwMzI3MDk2NTU=.42fe283d1d7e27c05b31ad2b1370aac464e9b15c1a7b4740de335e349b5ee817',
      'custom.temporary': 'HCT:ZnJvbnRlbmRfdXNlcl8xMjN8bWFpbGVycGFuZGF8Y3VzdG9tLnRlbXBvcmFyeXwxNzU1OTQ2MzA5NjU1fDE3NTYwMzI3MDk2NTU=.2c80196d5ae2f4709ee0c4b08531cacd15221bbee1c4a441a7f2b754e291e4d2'
    };
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
