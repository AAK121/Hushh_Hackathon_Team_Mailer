// Research Agent JavaScript Application

/**
 * Research Agent Frontend Application
 * Handles paper search, display, AI chat, and note-taking functionality
 */

class ResearchAgent {
    constructor() {
        this.baseUrl = 'http://localhost:8001';
        this.selectedPaper = null;
        this.searchResults = [];
        this.chatMessages = [];
        this.notes = {
            personal: '',
            research: '',
            summary: '',
            analysis: ''
        };
        this.currentNoteTab = 'personal';
        this.lastSavedNote = '';
        this.autoSaveTimer = null;

    constructor() {
        this.initializeEventListeners();
        this.initializeNotesTabs();
        this.showWelcomeMessage();
    }

    private initializeEventListeners(): void {
        // Search functionality
        const searchBtn = document.getElementById('searchBtn') as HTMLButtonElement;
        const searchInput = document.getElementById('searchInput') as HTMLInputElement;
        
        searchBtn.addEventListener('click', () => this.performSearch());
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performSearch();
            }
        });

        // Search suggestions
        const suggestionBtns = document.querySelectorAll('.suggestion-btn');
        suggestionBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const target = e.target as HTMLElement;
                searchInput.value = target.textContent || '';
                this.performSearch();
            });
        });

        // Chat functionality
        const chatInput = document.getElementById('chatInput') as HTMLInputElement;
        const chatSendBtn = document.getElementById('chatSendBtn') as HTMLButtonElement;
        
        chatSendBtn.addEventListener('click', () => this.sendChatMessage());
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendChatMessage();
            }
        });

        // Notes functionality
        const notesEditors = document.querySelectorAll('.notes-editor') as NodeListOf<HTMLTextAreaElement>;
        notesEditors.forEach(editor => {
            editor.addEventListener('input', () => this.handleNoteChange(editor));
            editor.addEventListener('blur', () => this.saveCurrentNote());
        });

        // Panel controls
        this.initializePanelControls();
    }

    private initializePanelControls(): void {
        // Download PDF functionality
        const downloadBtn = document.getElementById('downloadPdf');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.downloadCurrentPaper());
        }

        // Clear chat functionality
        const clearChatBtn = document.getElementById('clearChat');
        if (clearChatBtn) {
            clearChatBtn.addEventListener('click', () => this.clearChat());
        }

        // Notes controls
        const saveNotesBtn = document.getElementById('saveNotes');
        const clearNotesBtn = document.getElementById('clearNotes');
        
        if (saveNotesBtn) {
            saveNotesBtn.addEventListener('click', () => this.saveAllNotes());
        }
        
        if (clearNotesBtn) {
            clearNotesBtn.addEventListener('click', () => this.clearCurrentNote());
        }
    }

    private initializeNotesTabs(): void {
        const tabBtns = document.querySelectorAll('.tab-btn');
        tabBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const target = e.target as HTMLElement;
                const tabType = target.dataset.tab;
                if (tabType) {
                    this.switchNotesTab(tabType);
                }
            });
        });
    }

    private async performSearch(): Promise<void> {
        const searchInput = document.getElementById('searchInput') as HTMLInputElement;
        const query = searchInput.value.trim();
        
        if (!query) {
            this.showError('Please enter a search query');
            return;
        }

        this.showLoading('Searching for papers...');
        
        try {
            const response = await fetch(`${this.baseUrl}/research/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    query: query,
                    user_id: 'demo_user'
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data: SearchResponse = await response.json();
            this.searchResults = data.papers;
            this.displaySearchResults(data);
            
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Failed to search papers. Please check your connection and try again.');
        } finally {
            this.hideLoading();
        }
    }

    private displaySearchResults(data: SearchResponse): void {
        const resultsContainer = document.getElementById('searchResults');
        const resultsCount = document.getElementById('resultsCount');
        
        if (!resultsContainer || !resultsCount) return;

        // Update results count
        resultsCount.textContent = `${data.papers.length} papers found`;

        // Clear previous results
        resultsContainer.innerHTML = '';

        if (data.papers.length === 0) {
            resultsContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-search fa-3x"></i>
                    <h3>No papers found</h3>
                    <p>Try different keywords or broader search terms</p>
                </div>
            `;
            return;
        }

        // Display papers
        data.papers.forEach(paper => {
            const paperElement = this.createPaperElement(paper);
            resultsContainer.appendChild(paperElement);
        });
    }

    private createPaperElement(paper: Paper): HTMLElement {
        const paperDiv = document.createElement('div');
        paperDiv.className = 'paper-item';
        paperDiv.dataset.paperId = paper.id;
        
        paperDiv.innerHTML = `
            <div class="paper-title">${this.escapeHtml(paper.title)}</div>
            <div class="paper-authors">${paper.authors.map(author => this.escapeHtml(author)).join(', ')}</div>
            <div class="paper-meta">
                <span><i class="fas fa-calendar"></i> ${paper.published}</span>
                <span><i class="fas fa-tag"></i> ${paper.categories.join(', ')}</span>
                <span><i class="fab fa-arxiv"></i> ${paper.arxiv_id}</span>
            </div>
            <div class="paper-abstract">${this.escapeHtml(paper.summary.substring(0, 300))}${paper.summary.length > 300 ? '...' : ''}</div>
        `;

        paperDiv.addEventListener('click', () => this.selectPaper(paper));
        
        return paperDiv;
    }

    private selectPaper(paper: Paper): void {
        this.selectedPaper = paper;
        
        // Update UI selection
        document.querySelectorAll('.paper-item').forEach(item => {
            item.classList.remove('selected');
        });
        
        const selectedElement = document.querySelector(`[data-paper-id="${paper.id}"]`);
        if (selectedElement) {
            selectedElement.classList.add('selected');
        }

        // Display paper details
        this.displayPaperDetails(paper);
        
        // Add to chat context
        this.addChatMessage({
            id: this.generateId(),
            content: `I've selected the paper "${paper.title}" for our discussion. You can now ask me questions about this paper.`,
            role: 'ai',
            timestamp: new Date()
        });
    }

    private displayPaperDetails(paper: Paper): void {
        const paperContent = document.getElementById('paperContent');
        if (!paperContent) return;

        paperContent.innerHTML = `
            <div class="paper-header">
                <h3 class="paper-full-title">${this.escapeHtml(paper.title)}</h3>
                <div class="paper-full-authors">${paper.authors.map(author => this.escapeHtml(author)).join(', ')}</div>
                <div class="paper-full-meta">
                    <span><i class="fas fa-calendar"></i> Published: ${paper.published}</span>
                    <span><i class="fab fa-arxiv"></i> arXiv: ${paper.arxiv_id}</span>
                    <span><i class="fas fa-tag"></i> ${paper.categories.join(', ')}</span>
                </div>
            </div>
            <div class="paper-full-abstract">
                <h4>Abstract</h4>
                <p>${this.escapeHtml(paper.summary)}</p>
            </div>
        `;

        // Enable download button
        const downloadBtn = document.getElementById('downloadPdf') as HTMLButtonElement;
        if (downloadBtn) {
            downloadBtn.disabled = false;
        }
    }

    private async sendChatMessage(): Promise<void> {
        const chatInput = document.getElementById('chatInput') as HTMLInputElement;
        const message = chatInput.value.trim();
        
        if (!message) return;
        
        if (!this.selectedPaper) {
            this.showError('Please select a paper first to start chatting');
            return;
        }

        // Add user message
        const userMessage: ChatMessage = {
            id: this.generateId(),
            content: message,
            role: 'user',
            timestamp: new Date()
        };
        
        this.addChatMessage(userMessage);
        chatInput.value = '';

        // Show AI thinking
        const thinkingId = this.generateId();
        this.addChatMessage({
            id: thinkingId,
            content: 'Thinking...',
            role: 'ai',
            timestamp: new Date()
        });

        try {
            const response = await fetch(`${this.baseUrl}/research/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    paper_id: this.selectedPaper.id,
                    user_id: 'demo_user',
                    conversation_history: this.chatMessages.slice(-10).map(msg => ({
                        role: msg.role,
                        content: msg.content
                    }))
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Remove thinking message
            this.removeChatMessage(thinkingId);
            
            // Add AI response
            this.addChatMessage({
                id: this.generateId(),
                content: data.response,
                role: 'ai',
                timestamp: new Date()
            });

        } catch (error) {
            console.error('Chat error:', error);
            this.removeChatMessage(thinkingId);
            this.addChatMessage({
                id: this.generateId(),
                content: 'Sorry, I encountered an error while processing your message. Please try again.',
                role: 'ai',
                timestamp: new Date()
            });
        }
    }

    private addChatMessage(message: ChatMessage): void {
        this.chatMessages.push(message);
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${message.role}`;
        messageDiv.dataset.messageId = message.id;
        messageDiv.innerHTML = `
            <div class="message-content">${this.escapeHtml(message.content)}</div>
            <div class="message-time">${message.timestamp.toLocaleTimeString()}</div>
        `;

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    private removeChatMessage(messageId: string): void {
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        if (messageElement) {
            messageElement.remove();
        }
        
        this.chatMessages = this.chatMessages.filter(msg => msg.id !== messageId);
    }

    private clearChat(): void {
        this.chatMessages = [];
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            chatMessages.innerHTML = '';
        }
        this.showWelcomeMessage();
    }

    private switchNotesTab(tabType: string): void {
        // Save current note before switching
        this.saveCurrentNote();
        
        this.currentNoteTab = tabType;
        
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const activeTab = document.querySelector(`[data-tab="${tabType}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
        }
        
        // Switch editor content
        document.querySelectorAll('.notes-editor').forEach(editor => {
            editor.classList.remove('active');
        });
        
        const activeEditor = document.getElementById(`notes-${tabType}`) as HTMLTextAreaElement;
        if (activeEditor) {
            activeEditor.classList.add('active');
            activeEditor.value = this.notes[tabType as keyof NotesData];
            this.updateNotesStatus();
        }
    }

    private handleNoteChange(editor: HTMLTextAreaElement): void {
        const tabType = editor.id.replace('notes-', '') as keyof NotesData;
        this.notes[tabType] = editor.value;
        this.updateNotesStatus();
        
        // Auto-save after 2 seconds of inactivity
        if (this.autoSaveTimer) {
            clearTimeout(this.autoSaveTimer);
        }
        
        this.autoSaveTimer = window.setTimeout(() => {
            this.saveCurrentNote();
        }, 2000);
    }

    private saveCurrentNote(): void {
        const currentNote = this.notes[this.currentNoteTab as keyof NotesData];
        if (currentNote !== this.lastSavedNote) {
            // Here you would typically save to backend or localStorage
            localStorage.setItem(`research_notes_${this.currentNoteTab}`, currentNote);
            this.lastSavedNote = currentNote;
            this.updateNotesStatus('saved');
        }
    }

    private saveAllNotes(): void {
        Object.keys(this.notes).forEach(noteType => {
            localStorage.setItem(`research_notes_${noteType}`, this.notes[noteType as keyof NotesData]);
        });
        this.updateNotesStatus('all_saved');
    }

    private clearCurrentNote(): void {
        if (confirm('Are you sure you want to clear this note? This action cannot be undone.')) {
            this.notes[this.currentNoteTab as keyof NotesData] = '';
            const activeEditor = document.querySelector('.notes-editor.active') as HTMLTextAreaElement;
            if (activeEditor) {
                activeEditor.value = '';
            }
            this.updateNotesStatus();
        }
    }

    private updateNotesStatus(action: string = ''): void {
        const statusElement = document.getElementById('notesStatus');
        if (!statusElement) return;
        
        const currentNote = this.notes[this.currentNoteTab as keyof NotesData];
        const wordCount = currentNote.split(/\s+/).filter(word => word.length > 0).length;
        
        let statusText = `${wordCount} words`;
        
        if (action === 'saved') {
            statusText += ' • Saved';
        } else if (action === 'all_saved') {
            statusText += ' • All notes saved';
        } else if (currentNote !== this.lastSavedNote) {
            statusText += ' • Unsaved changes';
        }
        
        statusElement.textContent = statusText;
    }

    private async downloadCurrentPaper(): Promise<void> {
        if (!this.selectedPaper) {
            this.showError('No paper selected');
            return;
        }

        try {
            this.showLoading('Downloading PDF...');
            
            const response = await fetch(this.selectedPaper.pdf_url);
            if (!response.ok) {
                throw new Error('Failed to download PDF');
            }
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${this.selectedPaper.arxiv_id}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
        } catch (error) {
            console.error('Download error:', error);
            this.showError('Failed to download PDF');
        } finally {
            this.hideLoading();
        }
    }

    private loadSavedNotes(): void {
        Object.keys(this.notes).forEach(noteType => {
            const saved = localStorage.getItem(`research_notes_${noteType}`);
            if (saved) {
                this.notes[noteType as keyof NotesData] = saved;
            }
        });
    }

    private showWelcomeMessage(): void {
        this.addChatMessage({
            id: this.generateId(),
            content: 'Welcome to the Research Agent! Search for academic papers and I\'ll help you analyze and understand them. Select a paper from the search results to start our conversation.',
            role: 'ai',
            timestamp: new Date()
        });
    }

    private showLoading(message: string = 'Loading...'): void {
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'loading-overlay';
        loadingOverlay.id = 'loadingOverlay';
        loadingOverlay.innerHTML = `
            <div class="loading-content">
                <i class="fas fa-spinner fa-spin fa-2x"></i>
                <p>${message}</p>
            </div>
        `;
        document.body.appendChild(loadingOverlay);
    }

    private hideLoading(): void {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.remove();
        }
    }

    private showError(message: string): void {
        // Create error toast or modal
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-toast';
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #ff4757;
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            z-index: 1001;
            animation: slideIn 0.3s ease;
        `;
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <span style="margin-left: 0.5rem;">${message}</span>
        `;
        
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    private generateId(): string {
        return Math.random().toString(36).substr(2, 9);
    }

    private escapeHtml(text: string): string {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Initialize the application
    public init(): void {
        this.loadSavedNotes();
        console.log('Research Agent initialized successfully');
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const app = new ResearchAgent();
    app.init();
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .error-toast {
        animation: slideIn 0.3s ease;
    }
`;
document.head.appendChild(style);
