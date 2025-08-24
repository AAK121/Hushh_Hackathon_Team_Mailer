/**
 * Research Agent API Service
 * Handles communication with the backend API for paper search, chat, and analysis
 */

// Types and Interfaces
export interface Paper {
  id: string;
  title: string;
  authors: string[];
  published: string;
  categories: string[];
  arxiv_id: string;
  summary: string;
  pdf_url?: string;
}

export interface SearchResponse {
  papers: Paper[];
  total_count: number;
  status: string;
}

export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'ai' | 'system';
  timestamp: Date;
}

export interface ChatResponse {
  message: string;
  status: string;
  session_id?: string;
}

export interface NotesData {
  personal: string;
  research: string;
  summary: string;
  analysis: string;
}

export interface AnalysisRequest {
  paper_id: string;
  analysis_type: 'comprehensive' | 'section' | 'notes' | 'compare';
  section?: string;
  custom_text?: string;
}

class ResearchAgentApiService {
  private baseUrl: string;
  private sessionId: string | null = null;

  constructor() {
    this.baseUrl = 'http://localhost:8002'; // Research API server port
  }

  /**
   * Search for academic papers on arXiv
   */
  async searchPapers(query: string, maxResults: number = 20): Promise<SearchResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/research/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          max_results: maxResults
        })
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Search response:', data); // Debug log
      
      // Transform the response to match our interface
      // Handle both possible response structures
      const papers = data.results?.papers || data.papers || [];
      const transformedPapers = papers.map((paper: any, index: number) => {
        const arxivId = paper.arxiv_id || paper.id || '';
        let pdfUrl = paper.pdf_url;
        
        // Construct PDF URL if not provided but arXiv ID is available
        if (!pdfUrl && arxivId) {
          const cleanArxivId = arxivId.replace('arXiv:', '').trim();
          if (cleanArxivId) {
            pdfUrl = `https://arxiv.org/pdf/${cleanArxivId}.pdf`;
          }
        }

        return {
          id: paper.id || arxivId || `paper_${index}`,
          title: paper.title || 'Untitled',
          authors: paper.authors || [],
          published: paper.published || paper.pub_date || '',
          categories: paper.categories || [],
          arxiv_id: arxivId,
          summary: paper.summary || paper.abstract || '',
          pdf_url: pdfUrl
        };
      });

      return {
        papers: transformedPapers,
        total_count: data.results?.total_count || data.total_count || transformedPapers.length,
        status: data.status || 'success'
      };
    } catch (error) {
      console.error('Error searching papers:', error);
      throw new Error(error instanceof Error ? error.message : 'Failed to search papers');
    }
  }

  /**
   * Get paper content and details
   */
  async getPaperContent(paperId: string): Promise<Paper> {
    try {
      const response = await fetch(`${this.baseUrl}/research/paper/${paperId}/content`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to get paper content: ${response.statusText}`);
      }

      const data = await response.json();
      return data.paper;
    } catch (error) {
      console.error('Error getting paper content:', error);
      throw new Error(error instanceof Error ? error.message : 'Failed to get paper content');
    }
  }

  /**
   * Send a chat message about the selected paper
   */
  async sendChatMessage(message: string, paperId?: string): Promise<ChatResponse> {
    try {
      const requestBody: any = {
        message: message.trim(),
        user_id: 'frontend_user', // Add required user_id
        paper_id: paperId || 'general' // Provide default paper_id if none selected
      };

      // Add session_id if available
      if (this.sessionId) {
        requestBody.session_id = this.sessionId;
      }

      const response = await fetch(`${this.baseUrl}/research/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`Chat failed: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Chat response:', data); // Debug log
      
      // Store session ID if provided
      if (data.session_id && !this.sessionId) {
        this.sessionId = data.session_id;
      }

      return {
        message: data.results?.response || data.response || data.message || 'No response received',
        status: data.status || 'success',
        session_id: data.session_id
      };
    } catch (error) {
      console.error('Error sending chat message:', error);
      throw new Error(error instanceof Error ? error.message : 'Failed to send message');
    }
  }

  /**
   * Request paper analysis
   */
  async analyzePaper(request: AnalysisRequest): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/agents/research/paper/${request.paper_id}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          analysis_type: request.analysis_type,
          section: request.section,
          custom_text: request.custom_text
        })
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error analyzing paper:', error);
      throw new Error(error instanceof Error ? error.message : 'Failed to analyze paper');
    }
  }

  /**
   * Generate paper summary
   */
  async generateSummary(paperId: string): Promise<string> {
    try {
      const response = await fetch(`${this.baseUrl}/agents/research/paper/${paperId}/summary`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`Summary generation failed: ${response.statusText}`);
      }

      const data = await response.json();
      return data.results?.summary || 'Summary not available';
    } catch (error) {
      console.error('Error generating summary:', error);
      throw new Error(error instanceof Error ? error.message : 'Failed to generate summary');
    }
  }

  /**
   * Download paper PDF
   */
  async downloadPaper(paper: Paper): Promise<void> {
    try {
      let pdfUrl = paper.pdf_url;
      
      // Construct arXiv PDF URL if not available
      if (!pdfUrl && paper.arxiv_id) {
        const arxivId = paper.arxiv_id.replace('arXiv:', '').trim();
        if (arxivId) {
          pdfUrl = `https://arxiv.org/pdf/${arxivId}.pdf`;
        }
      }

      if (pdfUrl) {
        // Create a safe filename
        const safeTitle = paper.title
          .replace(/[^a-z0-9\s]/gi, '') // Remove special characters
          .replace(/\s+/g, '_') // Replace spaces with underscores
          .toLowerCase()
          .substring(0, 50); // Limit length

        const link = document.createElement('a');
        link.href = pdfUrl;
        link.download = `${safeTitle}.pdf`;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        
        // Append to body, click, and remove
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        console.log(`Download initiated for: ${pdfUrl}`);
      } else {
        throw new Error('PDF URL not available for this paper');
      }
    } catch (error) {
      console.error('Error downloading paper:', error);
      throw new Error(error instanceof Error ? error.message : 'Failed to download paper');
    }
  }

  /**
   * Save notes to backend
   */
  async saveNotes(notes: NotesData, paperId?: string, fileName?: string): Promise<void> {
    try {
      // For now, let's use a simplified approach and store notes in localStorage
      // until we implement proper consent tokens
      const notesKey = `research_notes_${paperId || 'general'}`;
      const existingNotes = localStorage.getItem(notesKey);
      const allNotes = existingNotes ? JSON.parse(existingNotes) : {};
      
      // Use provided filename or generate one if not provided
      const noteFileName = fileName || `notes_${new Date().toISOString().replace(/[:.]/g, '-')}`;
      
      allNotes[noteFileName] = notes.personal || notes.summary || 'Empty note';
      localStorage.setItem(notesKey, JSON.stringify(allNotes));
      
      console.log('Notes saved to localStorage:', allNotes);
    } catch (error) {
      console.error('Error saving notes:', error);
      throw new Error(error instanceof Error ? error.message : 'Failed to save notes');
    }
  }

  /**
   * Load notes from backend
   */
  async loadNotes(): Promise<Record<string, string>> {
    try {
      // Load from localStorage for now
      const allNotes: Record<string, string> = {};
      
      // Get all notes from localStorage
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith('research_notes_')) {
          const notes = localStorage.getItem(key);
          if (notes) {
            const parsedNotes = JSON.parse(notes);
            Object.assign(allNotes, parsedNotes);
          }
        }
      }
      
      console.log('Loaded notes from localStorage:', allNotes);
      return allNotes;
    } catch (error) {
      console.error('Error loading notes:', error);
      return {}; // Return empty object if loading fails
    }
  }

  /**
   * Get specific note by name
   */
  async getNote(noteName: string): Promise<string> {
    try {
      const allNotes = await this.loadNotes();
      return allNotes[noteName] || '';
    } catch (error) {
      console.error('Error getting note:', error);
      return '';
    }
  }

  /**
   * Update existing note
   */
  async updateNote(noteName: string, content: string): Promise<void> {
    try {
      // Find which localStorage key contains this note
      let targetKey = '';
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith('research_notes_')) {
          const notes = localStorage.getItem(key);
          if (notes) {
            const parsedNotes = JSON.parse(notes);
            if (parsedNotes[noteName]) {
              targetKey = key;
              break;
            }
          }
        }
      }
      
      // If note found, update it
      if (targetKey) {
        const notes = localStorage.getItem(targetKey);
        if (notes) {
          const parsedNotes = JSON.parse(notes);
          parsedNotes[noteName] = content;
          localStorage.setItem(targetKey, JSON.stringify(parsedNotes));
        }
      } else {
        // If note not found, create it as a new note
        const defaultKey = 'research_notes_general';
        const existingNotes = localStorage.getItem(defaultKey);
        const allNotes = existingNotes ? JSON.parse(existingNotes) : {};
        allNotes[noteName] = content;
        localStorage.setItem(defaultKey, JSON.stringify(allNotes));
      }
      
      console.log('Note updated:', noteName);
    } catch (error) {
      console.error('Error updating note:', error);
      throw new Error(error instanceof Error ? error.message : 'Failed to update note');
    }
  }

  /**
   * Delete a note
   */
  async deleteNote(noteName: string): Promise<void> {
    try {
      // Find which localStorage key contains this note
      let targetKey = '';
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith('research_notes_')) {
          const notes = localStorage.getItem(key);
          if (notes) {
            const parsedNotes = JSON.parse(notes);
            if (parsedNotes[noteName]) {
              targetKey = key;
              break;
            }
          }
        }
      }
      
      // If note found, delete it
      if (targetKey) {
        const notes = localStorage.getItem(targetKey);
        if (notes) {
          const parsedNotes = JSON.parse(notes);
          delete parsedNotes[noteName];
          localStorage.setItem(targetKey, JSON.stringify(parsedNotes));
        }
      }
      
      console.log('Note deleted:', noteName);
    } catch (error) {
      console.error('Error deleting note:', error);
      throw new Error(error instanceof Error ? error.message : 'Failed to delete note');
    }
  }

  /**
   * Test API connection
   */
  async testConnection(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      return response.ok;
    } catch (error) {
      console.error('API connection test failed:', error);
      return false;
    }
  }

  /**
   * Get current session ID
   */
  getSessionId(): string | null {
    return this.sessionId;
  }

  /**
   * Clear current session
   */
  clearSession(): void {
    this.sessionId = null;
  }

  /**
   * Utility function to escape HTML
   */
  static escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Utility function to generate unique IDs
   */
  static generateId(): string {
    return Math.random().toString(36).substr(2, 9);
  }

  /**
   * Format timestamp for display
   */
  static formatTimestamp(date: Date): string {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  /**
   * Truncate text to specified length
   */
  static truncateText(text: string, maxLength: number): string {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  }
}

// Export singleton instance
export const researchAgentApi = new ResearchAgentApiService();
export default ResearchAgentApiService;
