import axios, { AxiosResponse, AxiosError } from 'axios';
import {
  ArxivSearchRequest,
  ArxivSearchResponse,
  PaperUploadResponse,
  PaperSummaryResponse,
  SnippetProcessRequest,
  SnippetProcessResponse,
  SaveNotesRequest,
  SaveNotesResponse,
  ApiError,
} from '../types';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    const apiError: ApiError = {
      detail: error.response?.data?.detail || error.message || 'An unexpected error occurred',
      status_code: error.response?.status || 500,
    };
    throw apiError;
  }
);

// API Client Class
export class ResearchAgentAPI {
  /**
   * Search arXiv for papers based on query
   */
  static async searchArxiv(searchRequest: ArxivSearchRequest): Promise<ArxivSearchResponse> {
    try {
      const response = await api.post<ArxivSearchResponse>('/paper/search/arxiv', searchRequest);
      return response.data;
    } catch (error) {
      console.error('ArXiv search failed:', error);
      throw error;
    }
  }

  /**
   * Upload a PDF file
   */
  static async uploadPaper(file: File): Promise<PaperUploadResponse> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post<PaperUploadResponse>('/paper/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Paper upload failed:', error);
      throw error;
    }
  }

  /**
   * Get paper summary by paper ID
   */
  static async getPaperSummary(paperId: string): Promise<PaperSummaryResponse> {
    try {
      const response = await api.get<PaperSummaryResponse>(`/paper/${paperId}/summary`);
      return response.data;
    } catch (error) {
      console.error('Failed to get paper summary:', error);
      throw error;
    }
  }

  /**
   * Process a text snippet with user instruction
   */
  static async processSnippet(
    paperId: string,
    snippetRequest: SnippetProcessRequest
  ): Promise<SnippetProcessResponse> {
    try {
      const response = await api.post<SnippetProcessResponse>(
        `/paper/${paperId}/process/snippet`,
        snippetRequest
      );
      return response.data;
    } catch (error) {
      console.error('Snippet processing failed:', error);
      throw error;
    }
  }

  /**
   * Save user notes to the vault
   */
  static async saveNotes(notesRequest: SaveNotesRequest): Promise<SaveNotesResponse> {
    try {
      const response = await api.post<SaveNotesResponse>('/session/notes', notesRequest);
      return response.data;
    } catch (error) {
      console.error('Failed to save notes:', error);
      throw error;
    }
  }

  /**
   * Get paper PDF URL for viewing
   */
  static getPaperPdfUrl(paperId: string): string {
    return `${api.defaults.baseURL}/paper/${paperId}/pdf`;
  }

  /**
   * Check if the API server is healthy
   */
  static async healthCheck(): Promise<{ status: string; timestamp: string }> {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }
}

export default ResearchAgentAPI;
