// Research Agent API Service
// Handles communication with the research backend

export interface Paper {
  id: string;
  title: string;
  authors: string[];
  published: string;
  arxiv_id: string;
  categories: string[];
  summary: string;
  pdf_url: string;
  fullContent?: {
    content: string;
    pages: number;
    content_length: number;
  };
}

export interface SearchResponse {
  papers: Paper[];
  total_count: number;
  query: string;
}

export interface ChatRequest {
  message: string;
  paper_id: string;
  user_id: string;
  conversation_history?: Array<{
    role: string;
    content: string;
  }>;
  paper_content?: string;
}

export interface ChatResponse {
  response: string;
  paper_id: string;
  user_id: string;
  timestamp: string;
}

class ResearchApiService {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8001') {
    this.baseUrl = baseUrl;
  }

  /**
   * Test backend connection
   */
  async testConnection(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/docs`);
      return response.status === 200;
    } catch (error) {
      console.error('Backend connection failed:', error);
      return false;
    }
  }

  /**
   * Search for academic papers
   */
  async searchPapers(query: string, userId: string = 'demo_user'): Promise<SearchResponse> {
    const response = await fetch(`${this.baseUrl}/research/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        query: query.trim(),
        user_id: userId
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  /**
   * Get full content of a paper
   */
  async getPaperContent(paperId: string): Promise<{
    content: string;
    pages: number;
    content_length: number;
  }> {
    const encodedPaperId = encodeURIComponent(paperId);
    const response = await fetch(`${this.baseUrl}/research/paper/${encodedPaperId}/content`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  /**
   * Chat with AI about a paper
   */
  async chatWithAI(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${this.baseUrl}/research/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  /**
   * Download paper PDF
   */
  async downloadPaper(pdfUrl: string, fileName: string): Promise<void> {
    try {
      const response = await fetch(pdfUrl);
      if (!response.ok) {
        throw new Error('Failed to download PDF');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download error:', error);
      throw error;
    }
  }

  /**
   * Get health status of the research backend
   */
  async getHealthStatus(): Promise<{
    status: string;
    timestamp: string;
    version: string;
  }> {
    const response = await fetch(`${this.baseUrl}/health`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  /**
   * Get available research capabilities
   */
  async getCapabilities(): Promise<{
    search_enabled: boolean;
    chat_enabled: boolean;
    pdf_processing: boolean;
    supported_formats: string[];
  }> {
    const response = await fetch(`${this.baseUrl}/research/capabilities`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }

  /**
   * Upload PDF for processing
   */
  async uploadPDF(file: File, userId: string = 'demo_user'): Promise<{
    status: string;
    paper_id: string;
    text_length: number;
    session_id: string;
  }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    formData.append('consent_tokens', JSON.stringify({
      'vault:read:file': 'demo_token',
      'vault:write:file': 'demo_token'
    }));

    const response = await fetch(`${this.baseUrl}/agents/research/upload`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }

    const result = await response.json();
    
    if (result.status !== 'success') {
      throw new Error(result.errors?.[0] || 'Upload processing failed');
    }

    return {
      status: result.status,
      paper_id: result.results.paper_id,
      text_length: result.results.text_length,
      session_id: result.session_id
    };
  }
}

// Export singleton instance
export const researchApi = new ResearchApiService();

// Export utility functions
export const formatAuthors = (authors: string[]): string => {
  if (authors.length === 0) return 'Unknown';
  if (authors.length === 1) return authors[0];
  if (authors.length === 2) return `${authors[0]} and ${authors[1]}`;
  if (authors.length <= 5) return `${authors.slice(0, -1).join(', ')}, and ${authors[authors.length - 1]}`;
  return `${authors.slice(0, 3).join(', ')}, et al.`;
};

export const formatPublicationDate = (dateStr: string): string => {
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  } catch {
    return dateStr;
  }
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

export const generateArxivUrl = (arxivId: string): string => {
  return `https://arxiv.org/abs/${arxivId}`;
};

export const generatePdfUrl = (arxivId: string): string => {
  return `https://arxiv.org/pdf/${arxivId}.pdf`;
};

export default ResearchApiService;
