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
    this.baseUrl = 'http://localhost:8001'; // Main API server port (integrated research endpoints)
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

    // Update current paper if provided
    if (paperId && this.sessionMemory.currentPaper?.id !== paperId) {
      // Find paper in selected papers or search history
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
    
    // Keep only last 50 messages to prevent storage bloat
    if (this.chatHistory.length > 50) {
      this.chatHistory = this.chatHistory.slice(-50);
    }

    // Update session memory
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
      // Check if paper already exists
      const existingIndex = this.sessionMemory.context.selectedPapers.findIndex(p => p.id === paper.id);
      
      if (existingIndex >= 0) {
        // Update existing paper
        this.sessionMemory.context.selectedPapers[existingIndex] = paper;
      } else {
        // Add new paper
        this.sessionMemory.context.selectedPapers.push(paper);
      }

      // Set as current paper
      this.sessionMemory.currentPaper = paper;
      this.sessionMemory.context.currentTopic = paper.title;
      
      // Add system message about paper selection
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
      chat_history: this.chatHistory.slice(-10), // Last 10 messages for context
      selected_papers: this.sessionMemory?.context.selectedPapers || [],
      current_topic: this.sessionMemory?.context.currentTopic
    };
  }

  /**
   * Search for academic papers on arXiv
   */
  async searchPapers(query: string, maxResults: number = 20): Promise<SearchResponse> {
    try {
      // Initialize session and add search query to context
      this.initializeSession();
      this.addMessageToHistory(`Searching for: ${query}`, 'user');

      const response = await fetch(`${this.baseUrl}/research/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          max_results: maxResults,
          ...this.getSessionContext()
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

      // Add search results to session memory
      this.addMessageToHistory(`Found ${transformedPapers.length} papers`, 'system');
      
      // Update session context with search topic
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
      // Initialize session if needed
      this.initializeSession('frontend_user', paperId);
      
      // Add user message to history
      this.addMessageToHistory(message, 'user');

      const requestBody: any = {
        message: message.trim(),
        user_id: 'frontend_user',
        paper_id: paperId || 'general',
        format_math: true, // Request mathematical formatting
        preserve_structure: true, // Preserve matrix and table structures
        prevent_hallucination: true, // Prevent AI from making up information
        stick_to_content: true, // Only use information from the actual paper
        ...this.getSessionContext()
      };

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
        if (this.sessionMemory) {
          this.sessionMemory.sessionId = data.session_id;
        }
      }

      let aiResponse = data.results?.response || data.response || data.message || 'No response received';
      
      // Check for hallucination indicators and warn user
      if (this.detectHallucination(aiResponse, message)) {
        aiResponse = `⚠️ **Warning: Potential Hallucination Detected**\n\nThe AI response may contain fabricated information not present in the actual document. Please verify any specific details mentioned.\n\n---\n\n${aiResponse}`;
      }
      
      // Enhanced formatting for mathematical content
      aiResponse = this.formatMathematicalContent(aiResponse);
      
      // Add AI response to history
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
      // Initialize session if needed
      this.initializeSession();
      
      // Use provided filename or generate one if not provided
      const noteFileName = fileName || `notes_${new Date().toISOString().replace(/[:.]/g, '-')}`;
      const noteContent = notes.personal || notes.summary || 'Empty note';
      
      // Store in localStorage (for backward compatibility)
      const notesKey = `research_notes_${paperId || 'general'}`;
      const existingNotes = localStorage.getItem(notesKey);
      const allNotes = existingNotes ? JSON.parse(existingNotes) : {};
      allNotes[noteFileName] = noteContent;
      localStorage.setItem(notesKey, JSON.stringify(allNotes));
      
      // Also store in session memory
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
      console.log('🔄 loadNotes() called');
      // Load from localStorage
      const allNotes: Record<string, string> = {};
      
      // Get all notes from localStorage
      console.log('📂 Scanning localStorage for notes...');
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith('research_notes_')) {
          console.log(`🔑 Found notes key: ${key}`);
          const notes = localStorage.getItem(key);
          if (notes) {
            try {
              const parsedNotes = JSON.parse(notes);
              console.log(`📝 Parsed notes from ${key}:`, parsedNotes);
              Object.assign(allNotes, parsedNotes);
            } catch (parseError) {
              console.error(`❌ Failed to parse notes from ${key}:`, parseError);
            }
          }
        }
      }
      
      // Also merge session notes
      const sessionNotes = this.getSessionNotes();
      console.log('🧠 Session notes:', sessionNotes);
      Object.assign(allNotes, sessionNotes);
      
      console.log('📋 Final combined notes:', allNotes);
      return allNotes;
    } catch (error) {
      console.error('❌ Error loading notes:', error);
      return {}; // Return empty object if loading fails
    }
  }

  /**
   * Get specific note by name
   */
  async getNote(noteName: string): Promise<string> {
    try {
      console.log(`🔍 Getting note: "${noteName}"`);
      const allNotes = await this.loadNotes();
      const noteContent = allNotes[noteName] || '';
      console.log(`📄 Note "${noteName}" content:`, {
        found: !!allNotes[noteName],
        contentLength: noteContent.length,
        isEmpty: noteContent.trim() === '',
        preview: noteContent.length > 100 ? noteContent.substring(0, 100) + '...' : noteContent
      });
      return noteContent;
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
      console.log('updateNote called with:', { 
        noteName, 
        contentLength: content.length,
        isEmpty: content.trim() === '',
        content: content.length < 100 ? content : content.substring(0, 100) + '...'
      });
      
      // First, find which localStorage key contains this note (if it exists)
      let targetKey = '';
      let foundNote = false;
      
      console.log('🔍 Searching for existing note in localStorage...');
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith('research_notes_')) {
          const notes = localStorage.getItem(key);
          if (notes) {
            try {
              const parsedNotes = JSON.parse(notes);
              if (parsedNotes.hasOwnProperty(noteName)) {
                targetKey = key;
                foundNote = true;
                console.log('✅ Found existing note in key:', targetKey);
                break;
              }
            } catch (parseError) {
              console.warn('Failed to parse notes from key:', key, parseError);
            }
          }
        }
      }
      
      // Determine which key to use
      if (!targetKey) {
        // If note doesn't exist, use default key or create a new one
        targetKey = 'research_notes_general';
        console.log('📝 Note not found, will create in key:', targetKey);
      }
      
      // Get existing notes from the target key
      const existingNotesData = localStorage.getItem(targetKey);
      const allNotes = existingNotesData ? JSON.parse(existingNotesData) : {};
      
      // Update or create the note
      const oldContent = allNotes[noteName];
      allNotes[noteName] = content; // Save as-is, even if empty
      
      // Save back to localStorage
      localStorage.setItem(targetKey, JSON.stringify(allNotes));
      
      console.log('✅ Note updated successfully:', {
        noteName,
        targetKey,
        wasExisting: foundNote,
        oldContentLength: oldContent?.length || 0,
        newContentLength: content.length,
        wasCleared: content.trim() === ''
      });
      
      // Also update session memory if available
      this.updateSessionNotes(noteName, content);
      
      // Verify the save worked by reading it back
      const verification = await this.getNote(noteName);
      if (verification === content) {
        console.log('✅ Note save verified successfully');
      } else {
        console.warn('⚠️ Note save verification failed', {
          expected: content.length,
          actual: verification.length,
          expectedEmpty: content.trim() === '',
          actualEmpty: verification.trim() === ''
        });
        throw new Error('Note verification failed - content mismatch');
      }
      
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
      console.log('🗑️ deleteNote called for:', noteName);
      let noteDeleted = false;
      
      // First try to delete from session memory
      if (this.sessionMemory && this.sessionMemory.context.notes && this.sessionMemory.context.notes[noteName]) {
        console.log('🧠 Deleting from session memory:', noteName);
        delete this.sessionMemory.context.notes[noteName];
        noteDeleted = true;
      }
      
      // Then find and delete from localStorage
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith('research_notes_')) {
          const notes = localStorage.getItem(key);
          if (notes) {
            try {
              const parsedNotes = JSON.parse(notes);
              
              // Check if this note exists in this storage location
              if (parsedNotes[noteName] !== undefined) {
                console.log('🗂️ Found note in localStorage key:', key);
                delete parsedNotes[noteName];
                localStorage.setItem(key, JSON.stringify(parsedNotes));
                console.log('✅ Note deleted from localStorage:', noteName);
                noteDeleted = true;
                
                // If the localStorage object is now empty, remove the entire key
                if (Object.keys(parsedNotes).length === 0) {
                  console.log('🗄️ Removing empty localStorage key:', key);
                  localStorage.removeItem(key);
                }
                break; // Note found and deleted, exit loop
              }
            } catch (parseError) {
              console.warn('⚠️ Failed to parse notes from key:', key, parseError);
            }
          }
        }
      }
      
      if (!noteDeleted) {
        console.warn('⚠️ Note not found for deletion:', noteName);
        throw new Error(`Note "${noteName}" not found`);
      }
      
      console.log('✅ Note deleted successfully:', noteName);
    } catch (error) {
      console.error('❌ Error deleting note:', error);
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
      
      // Clear current paper if it was removed
      if (this.sessionMemory.currentPaper?.id === paperId) {
        this.sessionMemory.currentPaper = undefined;
        this.sessionMemory.context.currentTopic = undefined;
      }
      
      this.saveSessionToStorage();
      console.log('🗑️ Removed paper from session:', paperId);
    }
  }

  /**
   * Update session notes
   */
  updateSessionNotes(noteKey: string, content: string): void {
    if (this.sessionMemory) {
      this.sessionMemory.context.notes[noteKey] = content;
      this.saveSessionToStorage();
      console.log('📝 Updated session note:', noteKey);
    }
  }

  /**
   * Get session notes
   */
  getSessionNotes(): Record<string, string> {
    return this.sessionMemory?.context.notes || {};
  }

  /**
   * Format mathematical content for better display
   */
  private formatMathematicalContent(content: string): string {
    try {
      // Enhanced matrix formatting
      content = this.formatMatrices(content);
      
      // Format mathematical expressions
      content = this.formatMathExpressions(content);
      
      // Format code blocks and commands
      content = this.formatCodeBlocks(content);
      
      // Format theorem and lemma references
      content = this.formatMathematicalStatements(content);
      
      return content;
    } catch (error) {
      console.error('Error formatting mathematical content:', error);
      return content; // Return original content if formatting fails
    }
  }

  /**
   * Format matrices for better display
   */
  private formatMatrices(content: string): string {
    // Enhanced matrix pattern matching
    const matrixPatterns = [
      // Pattern for matrices like g23 = [matrix content]
      /([a-zA-Z]\d+\s*=\s*)((?:\s*[sr]\d+.*?\n)+)/gm,
      
      // Pattern for explicit matrix brackets
      /(\[[\s\S]*?\])/g,
      
      // Pattern for table-like structures with headers (s1, s2, etc.)
      /((?:s\d+\s*)+\n(?:(?:r\d+.*?\n)+))/gm
    ];

    matrixPatterns.forEach(pattern => {
      content = content.replace(pattern, (match, ...groups) => {
        if (groups.length >= 2) {
          // For named matrices like g23 = 
          const matrixName = groups[0];
          const matrixContent = groups[1];
          return `\n**${matrixName.trim()}**\n\`\`\`\n${this.formatMatrixRows(matrixContent)}\n\`\`\`\n`;
        } else {
          // For bracket matrices or table structures
          return `\n\`\`\`\n${this.formatMatrixRows(match)}\n\`\`\`\n`;
        }
      });
    });

    return content;
  }

  /**
   * Format matrix rows for better alignment
   */
  private formatMatrixRows(matrixContent: string): string {
    const lines = matrixContent.split('\n').filter(line => line.trim());
    
    // Find the maximum width needed for each column
    const rows = lines.map(line => {
      // Split on multiple spaces or tabs, preserving single spaces within cells
      return line.trim().split(/\s{2,}|\t/).map(cell => cell.trim());
    });

    if (rows.length === 0) return matrixContent;

    // Calculate column widths
    const maxCols = Math.max(...rows.map(row => row.length));
    const colWidths: number[] = [];
    
    for (let col = 0; col < maxCols; col++) {
      const maxWidth = Math.max(
        ...rows.map(row => (row[col] || '').length),
        3 // Minimum column width
      );
      colWidths[col] = maxWidth;
    }

    // Format each row with proper spacing
    const formattedRows = rows.map(row => {
      const paddedCells = row.map((cell, colIndex) => {
        const width = colWidths[colIndex] || 3;
        return cell.padEnd(width);
      });
      return '│ ' + paddedCells.join(' │ ') + ' │';
    });

    // Add header and footer borders
    const borderWidth = formattedRows[0]?.length || 0;
    const topBorder = '┌' + '─'.repeat(borderWidth - 2) + '┐';
    const bottomBorder = '└' + '─'.repeat(borderWidth - 2) + '┘';
    
    // Add separator after header if it looks like a matrix with column headers
    let result = [topBorder, ...formattedRows, bottomBorder];
    
    if (formattedRows.length > 1 && 
        (formattedRows[0].includes('s1') || formattedRows[0].includes('r1'))) {
      const separator = '├' + '─'.repeat(borderWidth - 2) + '┤';
      result = [topBorder, formattedRows[0], separator, ...formattedRows.slice(1), bottomBorder];
    }

    return result.join('\n');
  }

  /**
   * Format mathematical expressions
   */
  private formatMathExpressions(content: string): string {
    // Format inline math expressions
    content = content.replace(/\$([^$]+)\$/g, '`$1`');
    
    // Format display math expressions
    content = content.replace(/\$\$([^$]+)\$\$/g, '\n```math\n$1\n```\n');
    
    // Format M(G) notation
    content = content.replace(/M\(([^)]+)\)/g, '**M($1)**');
    
    // Format M*(G) notation (dual matroids)
    content = content.replace(/M\*\(([^)]+)\)/g, '**M*($1)**');
    
    // Format subscripts and superscripts in text
    content = content.replace(/([A-Za-z])\*(\d+)/g, '$1*$2');
    content = content.replace(/([A-Za-z])(\d+)/g, '$1₂');
    
    return content;
  }

  /**
   * Format code blocks and commands
   */
  private formatCodeBlocks(content: string): string {
    // Format MACEK commands
    content = content.replace(
      /(\.\/macek[^']*'[^']*'[^']*'[^']*')/g,
      '\n```bash\n$1\n```\n'
    );
    
    // Format other command-like structures
    content = content.replace(
      /(!(?:contract|minor|delete)[^;]*(?:;[^;]*)*)/g,
      '`$1`'
    );
    
    return content;
  }

  /**
   * Format mathematical statements (theorems, lemmas, etc.)
   */
  private formatMathematicalStatements(content: string): string {
    // Format theorem statements
    content = content.replace(
      /(Theorem\s+\d+\.?)(.*?)(?=\n\n|\n[A-Z]|\n$)/gs,
      '\n**$1**\n> $2\n'
    );
    
    // Format lemma statements
    content = content.replace(
      /(Lemma\s+\d+\.?)(.*?)(?=\n\n|\n[A-Z]|\n$)/gs,
      '\n**$1**\n> $2\n'
    );
    
    // Format definition statements
    content = content.replace(
      /(Definition\s+\d+\.?)(.*?)(?=\n\n|\n[A-Z]|\n$)/gs,
      '\n**$1**\n> $2\n'
    );
    
    return content;
  }

  /**
   * Detect potential hallucination in AI responses
   */
  private detectHallucination(response: string, userQuestion: string): boolean {
    // Patterns that suggest hallucination
    const hallucinationIndicators = [
      // Excessive lists (like 100+ project names)
      /(?:[\w\s-]+\n){20,}/,
      
      // Repetitive patterns suggesting generated content
      /(?:AI-(?:Powered|Enhanced|Driven|Based)\s+[\w\s]+){5,}/,
      
      // Generic project names that sound too perfect
      /(?:Ultimate|Universal|Infinite|Perfect|Complete|Advanced|Next-Gen|Revolutionary|Groundbreaking)\s+[\w\s]+(?:System|Platform|Solution|Tool|Application){3,}/,
      
      // Very long lists of similar items
      /(?:Detection|Prediction|Recognition|Analysis|Management|Optimization|Classification|Generation)\s*(?:System|Application|Tool|Platform)[\s\S]*?(?:Detection|Prediction|Recognition|Analysis|Management|Optimization|Classification|Generation)\s*(?:System|Application|Tool|Platform)[\s\S]*?(?:Detection|Prediction|Recognition|Analysis|Management|Optimization|Classification|Generation)\s*(?:System|Application|Tool|Platform)/,
      
      // Unrealistic number of items when asked for specific content
      /^[\w\s-]+(?:\n[\w\s-]+){50,}$/
    ];

    // Check for excessive specificity when document might not contain such details
    const isListingRequest = /(?:list|tell me|show me|what are).*(?:projects?|names?|titles?)/i.test(userQuestion);
    const hasExcessiveList = /(?:^|\n)(?:[\w\s-]+\n){15,}/.test(response);
    
    // Check patterns
    for (const pattern of hallucinationIndicators) {
      if (pattern.test(response)) {
        console.warn('🚨 Potential hallucination detected:', pattern);
        return true;
      }
    }

    // Special check for listing requests that produce unrealistic amounts of content
    if (isListingRequest && hasExcessiveList) {
      console.warn('🚨 Excessive list detected for listing request');
      return true;
    }

    // Check response length vs. typical document content
    if (response.length > 10000 && isListingRequest) {
      console.warn('🚨 Response too long for typical document content');
      return true;
    }

    return false;
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
      // Initialize session
      this.initializeSession(userId);
      this.addMessageToHistory(`Uploading PDF: ${file.name}`, 'user');

      // Prepare consent tokens - using demo tokens for testing
      const consentTokens = JSON.stringify({
        'vault.read.file': 'demo_token',
        'vault.write.file': 'demo_token'
      });

      // Create form data with the file and other parameters
      const formData = new FormData();
      formData.append('file', file);
      formData.append('user_id', userId);
      formData.append('consent_tokens', consentTokens);

      console.log('Uploading to:', `${this.baseUrl}/agents/research/upload`);
      console.log('File details:', {
        fileName: file.name,
        fileSize: file.size,
        userId: userId,
        consentTokens: consentTokens
      });

      const response = await fetch(`${this.baseUrl}/agents/research/upload`, {
        method: 'POST',
        body: formData
      });

      console.log('Upload response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Upload error response:', errorText);
        this.addMessageToHistory(`Upload failed: ${errorText}`, 'system');
        throw new Error(`Upload failed: ${response.status} ${response.statusText} - ${errorText}`);
      }

      const result = await response.json();
      console.log('Upload result:', result);
      
      if (result.status !== 'success') {
        const errorMsg = result.errors?.[0] || 'Upload processing failed';
        this.addMessageToHistory(`Upload processing failed: ${errorMsg}`, 'system');
        throw new Error(errorMsg);
      }

      // Create paper object from upload result and add to session
      const uploadedPaper: Paper = {
        id: result.results.paper_id,
        title: file.name.replace('.pdf', ''),
        authors: ['Uploaded Document'],
        published: new Date().toISOString(),
        categories: ['uploaded', 'local-file'],
        arxiv_id: `uploaded_${result.results.paper_id}`, // Mark as uploaded, not arXiv
        summary: `Uploaded PDF document: ${file.name} (${result.results.text_length} characters extracted)`,
        pdf_url: '', // Uploaded file, no external URL
        isUploaded: true // Custom flag to identify uploaded papers
      };

      // Add to session context
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
