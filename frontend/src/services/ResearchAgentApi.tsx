/**
 * Research Agent API Service
 * Handles communication with the backend API for paper search, chat, and analysis.
 * Includes advanced formatting for mathematical content into standard LaTeX.
 */

import { hushMcpApi } from './hushMcpApi';

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
  isUploaded?: boolean; // Flag to identify uploaded vs arXiv papers
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

export interface SessionMemory {
  sessionId: string;
  userId: string;
  currentPaper?: Paper;
  chatHistory: ChatMessage[];
  lastActivity: Date;
  context: {
    selectedPapers: Paper[];
    currentTopic?: string;
    activeAnalysis?: string;
    notes: Record<string, string>;
  };
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
  private sessionMemory: SessionMemory | null = null;
  private chatHistory: ChatMessage[] = [];

  constructor() {
    this.baseUrl = 'http://localhost:8001'; // Main API server port
    this.loadSessionFromStorage();
  }

  /**
   * Load session from localStorage
   */
  private loadSessionFromStorage(): void {
    try {
      const savedSession = localStorage.getItem('research_agent_session');
      if (savedSession) {
        this.sessionMemory = JSON.parse(savedSession);
        this.sessionId = this.sessionMemory?.sessionId || null;
        this.chatHistory = this.sessionMemory?.chatHistory || [];
        console.log('🧠 Loaded session memory:', this.sessionMemory);
      }
    } catch (error) {
      console.error('Error loading session memory:', error);
      this.clearSession();
    }
  }

  /**
   * Save session to localStorage
   */
  private saveSessionToStorage(): void {
    try {
      if (this.sessionMemory) {
        this.sessionMemory.lastActivity = new Date();
        this.sessionMemory.chatHistory = this.chatHistory;
        localStorage.setItem('research_agent_session', JSON.stringify(this.sessionMemory));
        console.log('💾 Saved session memory');
      }
    } catch (error) {
      console.error('Error saving session memory:', error);
    }
  }

  /**
   * Initialize or update session memory
   */
  private initializeSession(userId: string = 'frontend_user', paperId?: string): void {
    const now = new Date();
    
    if (!this.sessionMemory) {
      this.sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 8)}`;
      this.sessionMemory = {
        sessionId: this.sessionId,
        userId: userId,
        chatHistory: [],
        lastActivity: now,
        context: {
          selectedPapers: [],
          notes: {}
        }
      };
      console.log('🎯 Initialized new session:', this.sessionId);
    }

    if (paperId && this.sessionMemory.currentPaper?.id !== paperId) {
      const foundPaper = this.sessionMemory.context.selectedPapers.find(p => p.id === paperId);
      if (foundPaper) {
        this.sessionMemory.currentPaper = foundPaper;
        this.sessionMemory.context.currentTopic = foundPaper.title;
        console.log('📄 Updated current paper:', foundPaper.title);
      }
    }

    this.saveSessionToStorage();
  }

  /**
   * Add message to chat history and session memory
   */
  private addMessageToHistory(content: string, role: 'user' | 'ai' | 'system'): ChatMessage {
    const message: ChatMessage = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
      content,
      role,
      timestamp: new Date()
    };

    this.chatHistory.push(message);
    
    if (this.chatHistory.length > 50) {
      this.chatHistory = this.chatHistory.slice(-50);
    }

    if (this.sessionMemory) {
      this.sessionMemory.chatHistory = this.chatHistory;
      this.saveSessionToStorage();
    }

    console.log(`💬 Added ${role} message to history:`, content.substring(0, 100));
    return message;
  }

  /**
   * Add paper to session context
   */
  addPaperToSession(paper: Paper): void {
    this.initializeSession();
    
    if (this.sessionMemory) {
      const existingIndex = this.sessionMemory.context.selectedPapers.findIndex(p => p.id === paper.id);
      
      if (existingIndex >= 0) {
        this.sessionMemory.context.selectedPapers[existingIndex] = paper;
      } else {
        this.sessionMemory.context.selectedPapers.push(paper);
      }

      this.sessionMemory.currentPaper = paper;
      this.sessionMemory.context.currentTopic = paper.title;
      
      this.addMessageToHistory(
        `Selected paper: "${paper.title}" by ${paper.authors.join(', ')}`,
        'system'
      );

      this.saveSessionToStorage();
      console.log('📚 Added paper to session:', paper.title);
    }
  }

  /**
   * Get session context for API calls
   */
  private getSessionContext(): any {
    return {
      session_id: this.sessionId,
      current_paper: this.sessionMemory?.currentPaper,
      chat_history: this.chatHistory.slice(-10),
      selected_papers: this.sessionMemory?.context.selectedPapers || [],
      current_topic: this.sessionMemory?.context.currentTopic
    };
  }

  /**
   * Search for academic papers on arXiv
   */
  async searchPapers(query: string, maxResults: number = 20): Promise<SearchResponse> {
    try {
      this.initializeSession();
      this.addMessageToHistory(`Searching for: ${query}`, 'user');

      const response = await fetch(`${this.baseUrl}/research/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query.trim(),
          max_results: maxResults,
          ...this.getSessionContext()
        })
      });

      if (!response.ok) throw new Error(`Search failed: ${response.statusText}`);

      const data = await response.json();
      
      const papers = data.results?.papers || data.papers || [];
      const transformedPapers = papers.map((paper: any, index: number) => {
        const arxivId = paper.arxiv_id || paper.id || '';
        let pdfUrl = paper.pdf_url;
        
        if (!pdfUrl && arxivId) {
          const cleanArxivId = arxivId.replace('arXiv:', '').trim();
          if (cleanArxivId) pdfUrl = `https://arxiv.org/pdf/${cleanArxivId}.pdf`;
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

      this.addMessageToHistory(`Found ${transformedPapers.length} papers`, 'system');
      
      if (this.sessionMemory) {
        this.sessionMemory.context.currentTopic = query;
        this.saveSessionToStorage();
      }

      return {
        papers: transformedPapers,
        total_count: data.results?.total_count || data.total_count || transformedPapers.length,
        status: data.status || 'success'
      };
    } catch (error) {
      console.error('Error searching papers:', error);
      this.addMessageToHistory(`Search failed: ${error}`, 'system');
      throw new Error(error instanceof Error ? error.message : 'Failed to search papers');
    }
  }
  
  /**
   * Send a chat message about the selected paper
   */
  async sendChatMessage(message: string, paperId?: string, userId: string = 'frontend_user'): Promise<ChatResponse> {
    try {
      this.initializeSession(userId, paperId);
      this.addMessageToHistory(message, 'user');

      const requestBody: any = {
        message: message.trim(),
        user_id: userId,
        paper_id: paperId || 'general',
        format_math: true,
        preserve_structure: true,
        prevent_hallucination: true,
        stick_to_content: true,
        ...this.getSessionContext()
      };

      const response = await fetch(`${this.baseUrl}/research/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) throw new Error(`Chat failed: ${response.statusText}`);

      const data = await response.json();
      
      if (data.session_id && !this.sessionId) {
        this.sessionId = data.session_id;
        if (this.sessionMemory) this.sessionMemory.sessionId = data.session_id;
      }

      let aiResponse = data.results?.response || data.response || data.message || 'No response received';
      
      if (this.detectHallucination(aiResponse, message)) {
        aiResponse = `⚠️ **Warning: Potential Hallucination Detected**\n\nThe AI response may contain fabricated information not present in the actual document. Please verify any specific details mentioned.\n\n---\n\n${aiResponse}`;
      }
      
      // Enhanced formatting for mathematical content
      aiResponse = this.formatMathematicalContent(aiResponse);
      
      this.addMessageToHistory(aiResponse, 'ai');

      return {
        message: aiResponse,
        status: data.status || 'success',
        session_id: data.session_id
      };
    } catch (error) {
      console.error('Error sending chat message:', error);
      const errorMsg = error instanceof Error ? error.message : 'Failed to send message';
      this.addMessageToHistory(`Error: ${errorMsg}`, 'system');
      throw new Error(errorMsg);
    }
  }

  // --- START: MATHEMATICAL CONTENT FORMATTING ---

  // --- START: MATHEMATICAL CONTENT FORMATTING ---

  /**
   * Main function to format mathematical content for better display.
   * It runs a pipeline of formatters to clean and standardize the text into valid LaTeX.
   */
  private formatMathematicalContent(content: string): string {
    if (typeof content !== 'string') {
      console.warn('formatMathematicalContent received non-string input:', typeof content);
      return String(content || '');
    }
    try {
      // The order of operations is critical for correct parsing.
      content = this.formatCodeBlocks(content);
      content = this.formatMathematicalStatements(content);
      content = this.formatReferences(content);
      content = this.formatMatrices(content); // Must run before expressions
      content = this.formatMathExpressions(content);
      content = content.replace(/<PROTECT_REF>(.*?)<\/PROTECT_REF>/g, '$1'); // Unprotect
      return content;
    } catch (error) {
      console.error('Error formatting mathematical content:', error);
      return String(content || '');
    }
  }

  /**
   * Protects reference citations (e.g., [1]) from being misinterpreted as matrices.
   */
  private formatReferences(content: string): string {
    return content.replace(/(\[\d+\])/g, '<PROTECT_REF>$1</PROTECT_REF>');
  }

  /**
   * Converts text-based matrices into standard LaTeX `bmatrix` or `pmatrix` environments.
   */
  private formatMatrices(content: string): string {
    // This regex looks for matrices enclosed in brackets `[...]` or `(...)`
    const matrixPattern = /(\\begin{bmatrix}(?:.|\n)*?\\end{bmatrix})|\[((?:.|\n)*?)\]/g;
    
    return content.replace(matrixPattern, (match, bmatrix, bracketContent) => {
      // If it's already a bmatrix, leave it alone.
      if (bmatrix) return match;
      
      // If the match contains a protected reference, ignore it.
      if (/<PROTECT_REF>/.test(match)) return match;
      
      // Heuristic: if it's a short, single-line item, it's probably not a matrix.
      if (!bracketContent.includes('\n') && bracketContent.split(/\s+/).length < 4) {
          return match;
      }

      const latexRows = this.formatMatrixRows(bracketContent);
      // Use bmatrix for square brackets, which is standard for state-space representation.
      return `$$\n\\begin{bmatrix}\n${latexRows}\n\\end{bmatrix}\n$$`;
    });
  }

  /**
   * Helper to convert a string of matrix content into LaTeX rows.
   */
  private formatMatrixRows(matrixContent: string): string {
    if (typeof matrixContent !== 'string') return '';
    const lines = matrixContent.split('\n').filter(line => line.trim().length > 0);
    return lines.map(line => {
      const cells = line.trim().split(/\s+/).join(' & ');
      return `  ${cells} \\\\`;
    }).join('\n');
  }

  /**
   * Formats and cleans various mathematical expressions into standard LaTeX.
   */
  private formatMathExpressions(content: string): string {
    if (typeof content !== 'string') return String(content || '');

    // Pre-cleaning for common input errors
    content = content.replace(/\\dθ˙/g, '\\ddot{\\theta}'); // Fix dotted notation
    content = content.replace(/\\dψ˙/g, '\\ddot{\\psi}');
    content = content.replace(/(\w)\s*(\^|\_)\s*\{([^}]+)\}/g, '$1$2{$3}'); // Remove spaces before sup/sub
    content = content.replace(/(\\left|\()(\s*\$)/g, '$1'); // Clean up misplaced delimiters
    content = content.replace(/(\$\s*)(\\right|\))/g, '$2');

    // Remove box-drawing characters and Markdown bolding
    content = content.replace(/┌[─-]*\d+[─-]*┐/g, '');
    content = content.replace(/\*\*(.*?)\*\*/g, '$1');

    // Standardize display math `$$...$$` to be on its own lines
    content = content.replace(/(\S)\s*\$\$(.*?)\$\$\s*(\S)/g, '$1\n$$\n$2\n$$\n$3');

    // Convert common function names to proper LaTeX commands
    const functions = ['sin', 'cos', 'tan', 'ln', 'log', 'exp', 'sec'];
    functions.forEach(func => {
      const regex = new RegExp(`(?<!\\\\)${func}(?=[\\s\\(])`, 'g');
      content = content.replace(regex, `\\${func}`);
    });

    // Convert textual representations of Greek letters and symbols
    const symbols: { [key: string]: string } = {
      'alpha': '\\alpha', 'beta': '\\beta', 'gamma': '\\gamma', 'delta': '\\delta',
      'Gamma': '\\Gamma', 'Lambda': '\\Lambda', 'mu': '\\mu', 'nu': '\\nu',
      'rho': '\\rho', 'sigma': '\\sigma', 'tau': '\\tau', 'omega': '\\omega', 'theta': '\\theta',
      'psi': '\\psi', 'dot': '\\dot', 'ddot': '\\ddot', 'kappa': '\\kappa', 'lambda': '\\lambda',
      'epsilon': '\\epsilon', 'partial': '\\partial', 'int': '\\int', 'nabla': '\\nabla', 'sum': '\\sum'
    };
    for (const key in symbols) {
      const regex = new RegExp(`(?<!\\\\)${key}(?!\\w)`, 'g');
      content = content.replace(regex, symbols[key]);
    }

    // A more robust fraction formatter
    content = content.replace(/dtn\s*\n\s*dn\s*\n\s*x/g, '\\frac{d^n x}{dt^n}');
    content = content.replace(/dti\s*\n\s*d\(i-1\)\s*\n\s*x/g, '\\frac{d^{i-1} x}{dt^{i-1}}');
    content = content.replace(/([a-zA-Z0-9\._\^\{\}]+)\s*\/\s*([a-zA-Z0-9\._\^\{\}]+)/g, '\\frac{$1}{$2}');
    
    // Format subscripts and superscripts with curly braces
    content = content.replace(/_([a-zA-Z0-9]+)/g, '_{$1}');
    content = content.replace(/\^([a-zA-Z0-9]+)/g, '^{$1}');
    
    // Handle special cases like d^n x / dt^n
    content = content.replace(/d\^([a-zA-Z0-9]+)\s*([a-zA-Z])\s*\/\s*d([a-zA-Z])\^([a-zA-Z0-9]+)/g, '\\frac{d^{$1}$2}{d$3^{$4}}');
    
    // Handle summations written on multiple lines
    content = content.replace(/i=1\s*\n\s*∑\s*\n\s*n/g, '\\sum_{i=1}^{n}');

    // Clean up remaining invalid `pmatrix` environments used for simple fractions
    content = content.replace(/\\left\s*\\begin{pmatrix}(.*?)\\end{pmatrix}\s*\\right/g, '($1)');

    return content;
  }

  /**
   * Formats pre-formatted code blocks and commands.
   */
  private formatCodeBlocks(content: string): string {
    if (typeof content !== 'string') return String(content || '');
    content = content.replace(/(\.\/macek[^']*'[^']*'[^']*'[^']*')/g, '\n```bash\n$1\n```\n');
    content = content.replace(/(!(?:contract|minor|delete)[^;]*(?:;[^;]*)*)/g, '`$1`');
    return content;
  }

  /**
   * Formats mathematical statements (theorems, lemmas, etc.) using Markdown.
   */
  private formatMathematicalStatements(content: string): string {
    if (typeof content !== 'string') return String(content || '');
    const statements = ['Theorem', 'Lemma', 'Definition', 'Proposition', 'Corollary'];
    statements.forEach(statement => {
      const regex = new RegExp(`(${statement}\\s+\\d+\\.?)(.*?)(?=\\n\\n|\\n[A-Z]|\\n$)`, 'gs');
      content = content.replace(regex, '\n**$1**\n> $2\n');
    });
    return content;
  }
  
  // --- END: MATHEMATICAL CONTENT FORMATTING ---

  /**
   * Detect potential hallucination in AI responses
   */
  private detectHallucination(response: string, userQuestion: string): boolean {
    const hallucinationIndicators = [
      /(?:[\w\s-]+\n){20,}/,
      /(?:AI-(?:Powered|Enhanced|Driven|Based)\s+[\w\s]+){5,}/,
      /(?:Ultimate|Universal|Infinite|Perfect|Complete|Advanced|Next-Gen|Revolutionary|Groundbreaking)\s+[\w\s]+(?:System|Platform|Solution|Tool|Application){3,}/,
    ];

    const isListingRequest = /(?:list|tell me|show me|what are).*(?:projects?|names?|titles?)/i.test(userQuestion);
    const hasExcessiveList = /(?:^|\n)(?:[\w\s-]+\n){15,}/.test(response);

    for (const pattern of hallucinationIndicators) {
      if (pattern.test(response)) {
        console.warn('🚨 Potential hallucination detected:', pattern);
        return true;
      }
    }

    if (isListingRequest && hasExcessiveList) {
      console.warn('🚨 Excessive list detected for listing request');
      return true;
    }

    if (response.length > 10000 && isListingRequest) {
      console.warn('🚨 Response too long for typical document content');
      return true;
    }

    return false;
  }
  
  // --- All other methods from the original class are assumed to be here ---
  // --- For brevity, they are not repeated but should be included in the final file ---

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
      
      if (!pdfUrl && paper.arxiv_id) {
        const arxivId = paper.arxiv_id.replace('arXiv:', '').trim();
        if (arxivId) {
          pdfUrl = `https://arxiv.org/pdf/${arxivId}.pdf`;
        }
      }

      if (pdfUrl) {
        const safeTitle = paper.title
          .replace(/[^a-z0-9\s]/gi, '')
          .replace(/\s+/g, '_')
          .toLowerCase()
          .substring(0, 50);

        const link = document.createElement('a');
        link.href = pdfUrl;
        link.download = `${safeTitle}.pdf`;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        
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
      this.initializeSession();
      
      const noteFileName = fileName || `notes_${new Date().toISOString().replace(/[:.]/g, '-')}`;
      const noteContent = notes.personal || notes.summary || 'Empty note';
      
      const notesKey = `research_notes_${paperId || 'general'}`;
      const existingNotes = localStorage.getItem(notesKey);
      const allNotes = existingNotes ? JSON.parse(existingNotes) : {};
      allNotes[noteFileName] = noteContent;
      localStorage.setItem(notesKey, JSON.stringify(allNotes));
      
      this.updateSessionNotes(noteFileName, noteContent);
      this.addMessageToHistory(`Saved note: ${noteFileName}`, 'system');
      
      console.log('Notes saved to localStorage and session:', allNotes);
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
      const allNotes: Record<string, string> = {};
      
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith('research_notes_')) {
          const notes = localStorage.getItem(key);
          if (notes) {
            try {
              const parsedNotes = JSON.parse(notes);
              Object.assign(allNotes, parsedNotes);
            } catch (parseError) {
              console.error(`❌ Failed to parse notes from ${key}:`, parseError);
            }
          }
        }
      }
      
      const sessionNotes = this.getSessionNotes();
      Object.assign(allNotes, sessionNotes);
      
      return allNotes;
    } catch (error) {
      console.error('❌ Error loading notes:', error);
      return {};
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
      let targetKey = '';
      
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith('research_notes_')) {
          const notes = localStorage.getItem(key);
          if (notes) {
            try {
              const parsedNotes = JSON.parse(notes);
              if (parsedNotes.hasOwnProperty(noteName)) {
                targetKey = key;
                break;
              }
            } catch (parseError) {
              console.warn('Failed to parse notes from key:', key, parseError);
            }
          }
        }
      }
      
      if (!targetKey) {
        targetKey = 'research_notes_general';
      }
      
      const existingNotesData = localStorage.getItem(targetKey);
      const allNotes = existingNotesData ? JSON.parse(existingNotesData) : {};
      
      allNotes[noteName] = content;
      
      localStorage.setItem(targetKey, JSON.stringify(allNotes));
      
      this.updateSessionNotes(noteName, content);
      
    } catch (error) {
      console.error('❌ Error updating note:', error);
      throw new Error(error instanceof Error ? error.message : 'Failed to update note');
    }
  }

  /**
   * Delete a note
   */
  async deleteNote(noteName: string): Promise<void> {
    try {
      let noteDeleted = false;
      
      if (this.sessionMemory?.context.notes[noteName]) {
        delete this.sessionMemory.context.notes[noteName];
        this.saveSessionToStorage();
        noteDeleted = true;
      }
      
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith('research_notes_')) {
          const notes = localStorage.getItem(key);
          if (notes) {
            try {
              const parsedNotes = JSON.parse(notes);
              if (parsedNotes[noteName] !== undefined) {
                delete parsedNotes[noteName];
                localStorage.setItem(key, JSON.stringify(parsedNotes));
                if (Object.keys(parsedNotes).length === 0) {
                  localStorage.removeItem(key);
                }
                noteDeleted = true;
              }
            } catch (parseError) {
              console.warn('⚠️ Failed to parse notes from key:', key, parseError);
            }
          }
        }
      }
      
      if (!noteDeleted) {
        throw new Error(`Note "${noteName}" not found`);
      }
      
    } catch (error) {
      console.error('❌ Error deleting note:', error);
      throw new Error(error instanceof Error ? error.message : 'Failed to delete note');
    }
  }

  /**
   * Debug method to list all notes in storage
   */
  debugListAllNotes(): void {
    console.log('🔍 DEBUG: Listing all notes in storage');
    
    if (this.sessionMemory?.context.notes) {
      console.log('📝 Session notes:', this.sessionMemory.context.notes);
    } else {
      console.log('📝 Session notes: None');
    }
    
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('research_notes_')) {
        const notes = localStorage.getItem(key);
        if (notes) {
          try {
            console.log(`🗂️ ${key}:`, JSON.parse(notes));
          } catch (e) {
            console.warn(`⚠️ Could not parse notes from ${key}`);
          }
        }
      }
    }
  }

  /**
   * Clear all notes storage (useful for debugging)
   */
  clearAllNotesStorage(): void {
    console.log('🗑️ Clearing all notes storage');
    
    if (this.sessionMemory?.context.notes) {
      this.sessionMemory.context.notes = {};
      this.saveSessionToStorage();
    }
    
    const keysToRemove = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('research_notes_')) {
        keysToRemove.push(key);
      }
    }
    
    keysToRemove.forEach(key => localStorage.removeItem(key));
  }

  /**
   * Test API connection
   */
  async testConnection(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
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
    this.sessionMemory = null;
    this.chatHistory = [];
    localStorage.removeItem('research_agent_session');
    console.log('🗑️ Cleared session memory');
  }

  /**
   * Get chat history
   */
  getChatHistory(): ChatMessage[] {
    return [...this.chatHistory];
  }

  /**
   * Get session memory
   */
  getSessionMemory(): SessionMemory | null {
    return this.sessionMemory ? { ...this.sessionMemory } : null;
  }

  /**
   * Get current paper from session
   */
  getCurrentPaper(): Paper | null {
    return this.sessionMemory?.currentPaper || null;
  }

  /**
   * Get selected papers from session
   */
  getSelectedPapers(): Paper[] {
    return this.sessionMemory?.context.selectedPapers || [];
  }

  /**
   * Remove paper from session
   */
  removePaperFromSession(paperId: string): void {
    if (this.sessionMemory) {
      this.sessionMemory.context.selectedPapers = this.sessionMemory.context.selectedPapers.filter(
        p => p.id !== paperId
      );
      
      if (this.sessionMemory.currentPaper?.id === paperId) {
        this.sessionMemory.currentPaper = undefined;
        this.sessionMemory.context.currentTopic = undefined;
      }
      
      this.saveSessionToStorage();
    }
  }

  /**
   * Update session notes
   */
  updateSessionNotes(noteKey: string, content: string): void {
    if (this.sessionMemory) {
      this.sessionMemory.context.notes[noteKey] = content;
      this.saveSessionToStorage();
    }
  }

  /**
   * Get session notes
   */
  getSessionNotes(): Record<string, string> {
    return this.sessionMemory?.context.notes || {};
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

  /**
   * Upload PDF for processing
   */
  async uploadPDF(file: File, userId: string = 'frontend_user_research'): Promise<{
    status: string;
    paper_id: string;
    text_length: number;
    session_id: string;
  }> {
    try {
      this.initializeSession(userId);
      this.addMessageToHistory(`Uploading PDF: ${file.name}`, 'user');

      let consentTokens;
      try {
        consentTokens = await hushMcpApi.createResearchTokens(userId);
      } catch (tokenError) {
        console.error("Failed to generate consent tokens:", tokenError);
        throw new Error('Failed to generate authentication tokens. Please try again.');
      }

      const formData = new FormData();
      formData.append('file', file);

      // Add user_id and consent_tokens as query parameters
      const params = new URLSearchParams({
        user_id: userId,
        consent_tokens: JSON.stringify(consentTokens)
      });

      const response = await fetch(`${this.baseUrl}/agents/research/upload?${params.toString()}`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorText = await response.text();
        this.addMessageToHistory(`Upload failed: ${errorText}`, 'system');
        throw new Error(`Upload failed: ${response.status} ${response.statusText} - ${errorText}`);
      }

      const result = await response.json();
      
      if (result.status !== 'success') {
        const errorMsg = result.errors?.[0] || 'Upload processing failed';
        this.addMessageToHistory(`Upload processing failed: ${errorMsg}`, 'system');
        throw new Error(errorMsg);
      }

      const uploadedPaper: Paper = {
        id: result.results.paper_id,
        title: file.name.replace('.pdf', ''),
        authors: ['Uploaded Document'],
        published: new Date().toISOString(),
        categories: ['uploaded', 'local-file'],
        arxiv_id: `uploaded_${result.results.paper_id}`,
        summary: `Uploaded PDF document: ${file.name} (${result.results.text_length} characters extracted)`,
        pdf_url: '',
        isUploaded: true
      };

      this.addPaperToSession(uploadedPaper);
      this.addMessageToHistory(`Successfully uploaded and processed: ${file.name}. You can now ask questions about this document.`, 'system');

      return {
        status: result.status,
        paper_id: result.results.paper_id,
        text_length: result.results.text_length,
        session_id: result.session_id || this.sessionId || ''
      };
    } catch (error) {
      console.error('PDF Upload error:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const researchAgentApi = new ResearchAgentApiService();
export default ResearchAgentApiService;

// Expose debug methods to window object for easy debugging
if (typeof window !== 'undefined') {
  (window as any).researchAgentDebug = {
    listAllNotes: () => researchAgentApi.debugListAllNotes(),
    clearAllStorage: () => researchAgentApi.clearAllNotesStorage(),
    deleteNote: (noteName: string) => researchAgentApi.deleteNote(noteName),
    loadNotes: () => researchAgentApi.loadNotes(),
    api: researchAgentApi
  };
}