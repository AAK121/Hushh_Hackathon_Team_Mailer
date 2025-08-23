// Mass Mailing API service
// This service calls backend endpoints for mass mailing workflows.
// If the backend isn't available, it falls back to mocked data so the UI works.

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

const BASE_URL = '/api/mass-mail';

async function safeFetch(input: RequestInfo, init?: RequestInit) {
  try {
    const res = await fetch(input, init);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('MassMail API unreachable, using mock data. Error:', err);
    return null;
  }
}

export const massMailApi = {
  async uploadFile(file: File): Promise<{ batchId: string }> {
    const form = new FormData();
    form.append('file', file);

    const data = await safeFetch(`${BASE_URL}/upload`, {
      method: 'POST',
      body: form,
    });

    if (data) return { batchId: data.batchId };

    // Mock fallback
    return new Promise((resolve) =>
      setTimeout(() => resolve({ batchId: `mock-batch-${Date.now()}` }), 500)
    );
  },

  async submitSheetLink(url: string): Promise<{ batchId: string }> {
    const data = await safeFetch(`${BASE_URL}/sheet-link`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });

    if (data) return { batchId: data.batchId };

    return { batchId: `mock-batch-${Date.now()}` };
  },

  async getBatch(batchId: string): Promise<MassMailBatch> {
    const data = await safeFetch(`${BASE_URL}/batches/${batchId}`);
    if (data) return data as MassMailBatch;

    // Mock
    return {
      id: batchId,
      sourceType: 'file',
      createdAt: new Date().toISOString(),
      status: 'ready',
      total: 5,
      processed: 5,
    };
  },

  async listDrafts(batchId: string): Promise<DraftEmail[]> {
    const data = await safeFetch(`${BASE_URL}/batches/${batchId}/drafts`);
    if (data) return data as DraftEmail[];

    // Mock drafts
    return Array.from({ length: 5 }).map((_, i) => ({
      id: `${batchId}-draft-${i + 1}`,
      to: `user${i + 1}@example.com`,
      subject: `Welcome Offer ${i + 1}`,
      preview: 'Hi there, we are excited to share a special offer with you...',
      body: `Hello User ${i + 1},\n\nWe are thrilled to have you...\n\nBest,\nTeam`,
    }));
  },

  async approveDraft(draftId: string): Promise<{ ok: true }> {
    const data = await safeFetch(`${BASE_URL}/drafts/${draftId}/approve`, {
      method: 'POST',
    });
    if (data) return { ok: true };
    return { ok: true };
  },

  async rejectDraft(draftId: string): Promise<{ ok: true }> {
    const data = await safeFetch(`${BASE_URL}/drafts/${draftId}/reject`, {
      method: 'POST',
    });
    if (data) return { ok: true };
    return { ok: true };
  },
};
