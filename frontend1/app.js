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

        this.initializeEventListeners();
        this.initializeNotesTabs();
        this.showWelcomeMessage();
    }

    initializeEventListeners() {
        // Search functionality
        const searchBtn = document.getElementById('searchBtn');
        const searchInput = document.getElementById('searchInput');
        
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
                const target = e.target;
                searchInput.value = target.textContent || '';
                this.performSearch();
            });
        });

        // Chat functionality
        const chatInput = document.getElementById('chatInput');
        const chatSendBtn = document.getElementById('sendChatBtn');
        
        if (chatSendBtn) {
            chatSendBtn.addEventListener('click', () => this.sendChatMessage());
        }
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendChatMessage();
                }
            });
        }

        // Notes functionality
        const notesEditors = document.querySelectorAll('.notes-editor');
        notesEditors.forEach(editor => {
            editor.addEventListener('input', () => this.handleNoteChange(editor));
            editor.addEventListener('blur', () => this.saveCurrentNote());
        });

        // Panel controls
        this.initializePanelControls();
    }

    initializePanelControls() {
        // Download PDF functionality
        const downloadBtn = document.getElementById('downloadBtn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.downloadCurrentPaper());
        }

        // Clear chat functionality
        const clearChatBtn = document.getElementById('clearChat');
        if (clearChatBtn) {
            clearChatBtn.addEventListener('click', () => this.clearChat());
        }

        // Notes controls
        const saveNotesBtn = document.getElementById('saveNotesBtn');
        const clearNotesBtn = document.getElementById('clearNotes');
        
        if (saveNotesBtn) {
            saveNotesBtn.addEventListener('click', () => this.saveAllNotes());
        }
        
        if (clearNotesBtn) {
            clearNotesBtn.addEventListener('click', () => this.clearCurrentNote());
        }
    }

    initializeNotesTabs() {
        const tabBtns = document.querySelectorAll('.tab-btn');
        tabBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const target = e.target;
                const tabType = target.dataset.tab;
                if (tabType) {
                    this.switchNotesTab(tabType);
                }
            });
        });
    }

    async performSearch() {
        const searchInput = document.getElementById('searchInput');
        const query = searchInput.value.trim();
        
        if (!query) {
            this.showError('Please enter a search query');
            return;
        }

        console.log('Starting search for:', query);
        this.showLoading('Searching for papers...');
        
        try {
            console.log('Fetching from:', `${this.baseUrl}/research/search`);
            
            // Add timeout to prevent hanging
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
            
            const response = await fetch(`${this.baseUrl}/research/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    query: query,
                    user_id: 'demo_user'
                }),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Search results received:', data);
            this.searchResults = data.papers;
            this.displaySearchResults(data);
            
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Failed to search papers. Please check your connection and try again.');
        } finally {
            console.log('Hiding loading overlay');
            this.hideLoading();
        }
    }

    displaySearchResults(data) {
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

    createPaperElement(paper) {
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

    selectPaper(paper) {
        console.log('selectPaper called with:', paper);
        this.selectedPaper = paper;
        
        // Update UI selection
        document.querySelectorAll('.paper-item').forEach(item => {
            item.classList.remove('selected');
        });
        
        const selectedElement = document.querySelector(`[data-paper-id="${paper.id}"]`);
        if (selectedElement) {
            selectedElement.classList.add('selected');
            console.log('Selected element updated');
        }

        // Display paper details and load full content
        console.log('Calling displayPaperDetails');
        this.displayPaperDetails(paper);
        console.log('Calling loadPaperContent');
        this.loadPaperContent(paper);
        
        // Add to chat context
        this.addChatMessage({
            id: this.generateId(),
            content: `I've selected the paper "${paper.title}" for our discussion. I'm loading the full content now so you can ask me detailed questions about it.`,
            role: 'ai',
            timestamp: new Date()
        });
    }

    async loadPaperContent(paper) {
        console.log('loadPaperContent called with paper ID:', paper.id);
        console.log('Base URL:', this.baseUrl);
        
        // Show loading state in paper viewer
        const paperContent = document.getElementById('paperViewer');
        if (!paperContent) {
            console.error('paperViewer element not found!');
            return;
        }
        
        console.log('Setting loading content...');
        const loadingContent = `
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
            <div class="paper-content-loading">
                <div class="loading-spinner">
                    <i class="fas fa-spinner fa-spin"></i>
                    <p>Loading full paper content...</p>
                    <small>This may take a moment as we're downloading and processing the PDF</small>
                </div>
            </div>
        `;
        
        paperContent.innerHTML = loadingContent;
        console.log('Loading content set, making API request...');
        
        try {
            const apiUrl = `${this.baseUrl}/research/paper/${paper.id}/content`;
            console.log('Fetching from:', apiUrl);
            
            // Fetch full paper content
            const response = await fetch(apiUrl, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            console.log('Response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const contentData = await response.json();
            console.log('Paper content loaded successfully:', contentData);
            
            // Display full content
            this.displayFullPaperContent(paper, contentData);
            
        } catch (error) {
            console.error('Error loading paper content:', error);
            this.displayPaperContentError(paper, error.message);
        }
    }

    displayFullPaperContent(paper, contentData) {
        const paperContent = document.getElementById('paperViewer');
        if (!paperContent) return;
        
        // Truncate content if too long for display
        let displayContent = contentData.content;
        const maxLength = 50000; // 50k characters max for display
        let truncated = false;
        
        if (displayContent.length > maxLength) {
            displayContent = displayContent.substring(0, maxLength) + '\n\n[Content truncated for display...]';
            truncated = true;
        }
        
        paperContent.innerHTML = `
            <div class="paper-header">
                <h3 class="paper-full-title">${this.escapeHtml(paper.title)}</h3>
                <div class="paper-full-authors">${paper.authors.map(author => this.escapeHtml(author)).join(', ')}</div>
                <div class="paper-full-meta">
                    <span><i class="fas fa-calendar"></i> Published: ${paper.published}</span>
                    <span><i class="fab fa-arxiv"></i> arXiv: ${paper.arxiv_id}</span>
                    <span><i class="fas fa-tag"></i> ${paper.categories.join(', ')}</span>
                    <span><i class="fas fa-file-pdf"></i> ${contentData.pages} pages</span>
                    <span><i class="fas fa-font"></i> ${contentData.content_length.toLocaleString()} characters</span>
                </div>
            </div>
            <div class="paper-full-abstract">
                <h4>Abstract</h4>
                <p>${this.escapeHtml(paper.summary)}</p>
            </div>
            <div class="paper-full-content">
                <div class="content-header">
                    <h4><i class="fas fa-file-text"></i> Full Paper Content</h4>
                    <div class="content-controls">
                        <button class="control-btn" onclick="this.parentElement.parentElement.nextElementSibling.style.fontSize='0.8em'">
                            <i class="fas fa-search-minus"></i> Smaller
                        </button>
                        <button class="control-btn" onclick="this.parentElement.parentElement.nextElementSibling.style.fontSize='0.9em'">
                            <i class="fas fa-font"></i> Normal
                        </button>
                        <button class="control-btn" onclick="this.parentElement.parentElement.nextElementSibling.style.fontSize='1.1em'">
                            <i class="fas fa-search-plus"></i> Larger
                        </button>
                    </div>
                </div>
                <div class="paper-text-content">
                    <pre>${this.escapeHtml(displayContent)}</pre>
                </div>
                ${truncated ? '<div class="truncation-notice"><i class="fas fa-info-circle"></i> Content has been truncated for display. Use the AI chat to ask about specific sections.</div>' : ''}
            </div>
        `;
        
        // Enable download button
        const downloadBtn = document.getElementById('downloadBtn');
        if (downloadBtn) {
            downloadBtn.disabled = false;
        }
        
        // Update chat context
        this.addChatMessage({
            id: this.generateId(),
            content: `I've loaded the full content of "${paper.title}" (${contentData.pages} pages, ${contentData.content_length.toLocaleString()} characters). You can now ask me detailed questions about any part of the paper!`,
            role: 'ai',
            timestamp: new Date()
        });
    }

    displayPaperContentError(paper, errorMessage) {
        const paperContent = document.getElementById('paperViewer');
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
            <div class="paper-content-error">
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h4>Unable to load full paper content</h4>
                    <p>${this.escapeHtml(errorMessage)}</p>
                    <p>You can still:</p>
                    <ul>
                        <li>Read the abstract above</li>
                        <li>Download the PDF using the button below</li>
                        <li>Ask general questions about the paper</li>
                    </ul>
                </div>
            </div>
        `;
        
        // Enable download button
        const downloadBtn = document.getElementById('downloadBtn');
        if (downloadBtn) {
            downloadBtn.disabled = false;
        }
    }

    displayPaperDetails(paper) {
        const paperContent = document.getElementById('paperViewer');
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
        const downloadBtn = document.getElementById('downloadBtn');
        if (downloadBtn) {
            downloadBtn.disabled = false;
        }
    }

    async sendChatMessage() {
        const chatInput = document.getElementById('chatInput');
        const message = chatInput.value.trim();
        
        if (!message) return;
        
        if (!this.selectedPaper) {
            this.showError('Please select a paper first to start chatting');
            return;
        }

        // Add user message
        const userMessage = {
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

    addChatMessage(message) {
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

    removeChatMessage(messageId) {
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        if (messageElement) {
            messageElement.remove();
        }
        
        this.chatMessages = this.chatMessages.filter(msg => msg.id !== messageId);
    }

    clearChat() {
        this.chatMessages = [];
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            chatMessages.innerHTML = '';
        }
        this.showWelcomeMessage();
    }

    switchNotesTab(tabType) {
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
        
        const activeEditor = document.getElementById(`notes-${tabType}`);
        if (activeEditor) {
            activeEditor.classList.add('active');
            activeEditor.value = this.notes[tabType];
            this.updateNotesStatus();
        }
    }

    handleNoteChange(editor) {
        const tabType = editor.id.replace('notes-', '');
        this.notes[tabType] = editor.value;
        this.updateNotesStatus();
        
        // Auto-save after 2 seconds of inactivity
        if (this.autoSaveTimer) {
            clearTimeout(this.autoSaveTimer);
        }
        
        this.autoSaveTimer = setTimeout(() => {
            this.saveCurrentNote();
        }, 2000);
    }

    saveCurrentNote() {
        const currentNote = this.notes[this.currentNoteTab];
        if (currentNote !== this.lastSavedNote) {
            // Save to localStorage
            localStorage.setItem(`research_notes_${this.currentNoteTab}`, currentNote);
            this.lastSavedNote = currentNote;
            this.updateNotesStatus('saved');
        }
    }

    saveAllNotes() {
        Object.keys(this.notes).forEach(noteType => {
            localStorage.setItem(`research_notes_${noteType}`, this.notes[noteType]);
        });
        this.updateNotesStatus('all_saved');
    }

    clearCurrentNote() {
        if (confirm('Are you sure you want to clear this note? This action cannot be undone.')) {
            this.notes[this.currentNoteTab] = '';
            const activeEditor = document.querySelector('.notes-editor.active');
            if (activeEditor) {
                activeEditor.value = '';
            }
            this.updateNotesStatus();
        }
    }

    updateNotesStatus(action = '') {
        const statusElement = document.getElementById('notesStatus');
        if (!statusElement) return;
        
        const currentNote = this.notes[this.currentNoteTab];
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

    async downloadCurrentPaper() {
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

    loadSavedNotes() {
        Object.keys(this.notes).forEach(noteType => {
            const saved = localStorage.getItem(`research_notes_${noteType}`);
            if (saved) {
                this.notes[noteType] = saved;
            }
        });
    }

    showWelcomeMessage() {
        this.addChatMessage({
            id: this.generateId(),
            content: 'Welcome to the Research Agent! Search for academic papers and I\'ll help you analyze and understand them. Select a paper from the search results to start our conversation.',
            role: 'ai',
            timestamp: new Date()
        });
    }

    showLoading(message = 'Loading...') {
        // Remove any existing loading overlay first
        this.hideLoading();
        
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

    hideLoading() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.remove();
        }
        
        // Also remove any loading overlays that might not have the ID
        const allLoadingOverlays = document.querySelectorAll('.loading-overlay');
        allLoadingOverlays.forEach(overlay => overlay.remove());
    }

    showError(message) {
        // Create error toast
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

    generateId() {
        return Math.random().toString(36).substr(2, 9);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Initialize the application
    init() {
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
