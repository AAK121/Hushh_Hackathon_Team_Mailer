/**
 * Research Agent Redesigned JavaScript Application
 * Features: Paper dropdown, two-panel layout, editable AI responses, note management
 */

class ResearchAgentRedesigned {
    constructor() {
        this.baseUrl = 'http://localhost:8001';
        this.selectedPaper = null;
        this.searchResults = [];
        this.chatMessages = [];
        this.notesFiles = new Map(); // Map of noteId -> {name, content, messages}
        this.currentNotesId = 'current';
        this.currentView = 'abstract'; // abstract or full
        this.autoSaveTimer = null;

        // Test backend connection
        this.testBackendConnection();

        this.initializeEventListeners();
        this.initializeNotesSystem();
        this.showWelcomeMessage();
        this.updateStatus();
    }

    async testBackendConnection() {
        try {
            console.log('Testing backend connection...');
            const response = await fetch(`${this.baseUrl}/docs`);
            console.log('Backend connection test:', response.status === 200 ? 'SUCCESS' : 'FAILED');
        } catch (error) {
            console.error('Backend connection failed:', error);
            this.showError('Backend server is not running. Please start the server first.');
        }
    }

    initializeEventListeners() {
        console.log('Initializing event listeners...');
        
        // Search functionality
        const searchBtn = document.getElementById('searchBtn');
        const searchInput = document.getElementById('searchInput');
        
        console.log('Search elements found:', { searchBtn, searchInput });
        
        if (searchBtn) {
            searchBtn.addEventListener('click', () => {
                console.log('Search button clicked!');
                window.app.performSearch();
            });
        }
        
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                console.log('Key pressed in search input:', e.key);
                if (e.key === 'Enter') {
                    console.log('Enter key detected, calling performSearch');
                    e.preventDefault(); // Prevent form submission
                    window.app.performSearch();
                }
            });
            
            // Also add keydown listener as backup
            searchInput.addEventListener('keydown', (e) => {
                console.log('Key down in search input:', e.key);
                if (e.key === 'Enter') {
                    console.log('Enter key detected on keydown, calling performSearch');
                    e.preventDefault();
                    window.app.performSearch();
                }
            });
        }

        // Paper selection
        const paperDropdown = document.getElementById('paperDropdown');
        const analyzeBtn = document.getElementById('analyzeBtn');
        
        paperDropdown.addEventListener('change', (e) => window.app.selectPaper(e.target.value));
        analyzeBtn.addEventListener('click', () => window.app.analyzePaper());

        // Paper controls
        const downloadBtn = document.getElementById('downloadBtn');
        const summaryBtn = document.getElementById('summaryBtn');
        const abstractViewBtn = document.getElementById('abstractViewBtn');
        const fullViewBtn = document.getElementById('fullViewBtn');
        const pdfViewBtn = document.getElementById('pdfViewBtn');
        
        downloadBtn.addEventListener('click', () => window.app.downloadCurrentPaper());
        summaryBtn.addEventListener('click', () => window.app.generateSummary());
        abstractViewBtn.addEventListener('click', () => window.app.switchView('abstract'));
        fullViewBtn.addEventListener('click', () => window.app.switchView('full'));
        pdfViewBtn.addEventListener('click', () => window.app.switchView('pdf'));

        // Chat functionality
        const chatInput = document.getElementById('chatInput');
        const sendChatBtn = document.getElementById('sendChatBtn');
        
        sendChatBtn.addEventListener('click', () => window.app.sendChatMessage());
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                window.app.sendChatMessage();
            }
        });

        // Quick action buttons
        const quickBtns = document.querySelectorAll('.quick-btn');
        quickBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.closest('.quick-btn').dataset.action;
                window.app.performQuickAction(action);
            });
        });

        // Notes management
        const newNotesBtn = document.getElementById('newNotesBtn');
        const saveNotesBtn = document.getElementById('saveNotesBtn');
        const notesDropdown = document.getElementById('notesDropdown');
        
        newNotesBtn.addEventListener('click', () => window.app.showCreateNotesModal());
        saveNotesBtn.addEventListener('click', () => window.app.saveCurrentNotes());
        notesDropdown.addEventListener('change', (e) => window.app.switchNotesFile(e.target.value));

        // Modal controls
        const closeModalBtn = document.getElementById('closeModalBtn');
        const cancelModalBtn = document.getElementById('cancelModalBtn');
        const createNotesBtn = document.getElementById('createNotesBtn');
        
        closeModalBtn.addEventListener('click', () => window.app.hideCreateNotesModal());
        cancelModalBtn.addEventListener('click', () => window.app.hideCreateNotesModal());
        createNotesBtn.addEventListener('click', () => window.app.createNewNotesFile());

        // Analysis menu controls
        const analysisMenuBtn = document.getElementById('analysisMenuBtn');
        const closeAnalysisModalBtn = document.getElementById('closeAnalysisModalBtn');
        const closeSectionModalBtn = document.getElementById('closeSectionModalBtn');
        const analyzeCustomBtn = document.getElementById('analyzeCustomBtn');
        
        analysisMenuBtn.addEventListener('click', () => window.app.showAnalysisMenu());
        closeAnalysisModalBtn.addEventListener('click', () => window.app.hideAnalysisMenu());
        closeSectionModalBtn.addEventListener('click', () => window.app.hideSectionMenu());
        analyzeCustomBtn.addEventListener('click', () => window.app.analyzeCustomSection());

        // Analysis card clicks
        document.addEventListener('click', (e) => {
            const analysisCard = e.target.closest('.analysis-card');
            if (analysisCard) {
                const analysisType = analysisCard.dataset.analysis;
                window.app.handleAnalysisSelection(analysisType);
            }
            
            const sectionItem = e.target.closest('.section-item');
            if (sectionItem) {
                const sectionType = sectionItem.dataset.section;
                this.handleSectionSelection(sectionType);
            }
        });

        // Panel resizing
        this.initializePanelResizing();

        // Auto-save on chat messages
        this.setupAutoSave();
    }

    initializePanelResizing() {
        const divider = document.getElementById('panelDivider');
        const leftPanel = document.querySelector('.left-panel');
        const rightPanel = document.querySelector('.right-panel');
        const container = document.querySelector('.panel-container');
        
        let isResizing = false;
        
        divider.addEventListener('mousedown', (e) => {
            isResizing = true;
            document.body.style.cursor = 'col-resize';
            document.body.style.userSelect = 'none';
        });
        
        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;
            
            const containerRect = container.getBoundingClientRect();
            const newLeftWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
            
            // Limit panel sizes (minimum 20%, maximum 80%)
            if (newLeftWidth >= 20 && newLeftWidth <= 80) {
                leftPanel.style.flex = `0 0 ${newLeftWidth}%`;
                rightPanel.style.flex = `0 0 ${100 - newLeftWidth}%`;
            }
        });
        
        document.addEventListener('mouseup', () => {
            if (isResizing) {
                isResizing = false;
                document.body.style.cursor = 'default';
                document.body.style.userSelect = 'auto';
            }
        });
    }

    initializeNotesSystem() {
        // Clear old notes from localStorage
        localStorage.removeItem('research_notes_redesigned');
        localStorage.removeItem('research_current_notes_id');
        
        // Initialize fresh default notes file
        this.notesFiles.clear();
        this.notesFiles.set('current', {
            name: 'Current Session',
            content: '',
            messages: []
        });
        
        // Update the notes dropdown
        this.updateNotesDropdown();
        
        console.log('Notes system initialized with fresh state');
    }

    async performSearch() {
        console.log('performSearch called!');
        const searchInput = document.getElementById('searchInput');
        const query = searchInput.value.trim();
        
        console.log('Search query:', query);
        
        if (!query) {
            this.showError('Please enter a search query');
            return;
        }

        console.log('Starting search for:', query);
        this.showLoading('Searching for papers...');
        
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000);
            
            console.log('Making fetch request to:', `${this.baseUrl}/research/search`);
            
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
            console.log('Number of papers:', data.papers ? data.papers.length : 'No papers property');
            console.log('First paper:', data.papers ? data.papers[0] : 'No first paper');
            this.searchResults = data.papers;
            this.populatePaperDropdown(data.papers);
            
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Failed to search papers. Please check your connection and try again.');
        } finally {
            this.hideLoading();
        }
    }

    populatePaperDropdown(papers) {
        console.log('populatePaperDropdown called with:', papers);
        const dropdown = document.getElementById('paperDropdown');
        console.log('Dropdown element:', dropdown);
        
        // Clear existing options except the first one
        dropdown.innerHTML = '<option value="">Select a paper...</option>';
        
        papers.forEach((paper, index) => {
            console.log(`Adding paper ${index}:`, paper.title);
            const option = document.createElement('option');
            option.value = index;
            option.textContent = `${paper.title.substring(0, 80)}${paper.title.length > 80 ? '...' : ''}`;
            dropdown.appendChild(option);
        });
        
        dropdown.disabled = false;
        this.updateStatus(`Found ${papers.length} papers`);
    }

    selectPaper(paperIndex) {
        console.log('selectPaper called with index:', paperIndex);
        
        if (paperIndex === '') {
            this.selectedPaper = null;
            this.clearPaperViewer();
            document.getElementById('analyzeBtn').disabled = true;
            return;
        }
        
        const paper = this.searchResults[parseInt(paperIndex)];
        console.log('Selected paper:', paper);
        if (!paper) {
            console.error('Paper not found for index:', paperIndex);
            return;
        }
        
        // Check if this is a different paper
        const isDifferentPaper = !this.selectedPaper || this.selectedPaper.id !== paper.id;
        
        this.selectedPaper = paper;
        document.getElementById('analyzeBtn').disabled = false;
        
        // Enable view buttons
        console.log('Enabling view buttons...');
        document.getElementById('abstractViewBtn').disabled = false;
        document.getElementById('fullViewBtn').disabled = false;
        document.getElementById('pdfViewBtn').disabled = false;
        
        // If it's a different paper, create a new notes session or switch to current
        if (isDifferentPaper) {
            this.startNewPaperSession(paper);
        }
        
        // Display paper in viewer - default to abstract view
        this.currentView = 'abstract';
        this.switchView('abstract'); // This will handle display and button activation
        this.updateStatus(`Selected: ${paper.title.substring(0, 50)}...`);
        
        // Remove any welcome messages and add a simple selection message
        this.removeWelcomeMessages();
        this.addChatMessage({
            id: this.generateId(),
            content: `Selected: "${paper.title}"`,
            role: 'system',
            timestamp: new Date()
        });
    }

    removeWelcomeMessages() {
        const notesFile = this.getCurrentNotesFile();
        notesFile.messages = notesFile.messages.filter(msg => !msg.isWelcome);
        
        // Update the display
        const chatMessages = document.getElementById('chatMessages');
        const welcomeElements = chatMessages.querySelectorAll('.chat-message[data-welcome="true"]');
        welcomeElements.forEach(el => el.remove());
    }

    startNewPaperSession(paper) {
        // Switch to the current session and clear it for the new paper
        this.currentNotesId = 'current';
        
        // Clear the current session for the new paper
        const currentNotesFile = this.notesFiles.get('current');
        currentNotesFile.messages = [];
        currentNotesFile.name = `Current Session - ${paper.title.substring(0, 30)}...`;
        
        // Clear the chat display
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = '';
        
        // Update the notes dropdown to reflect the new session name
        this.updateNotesDropdown();
        
        // Show welcome message for the new paper
        this.showWelcomeMessage();
        
        console.log(`Started new session for paper: ${paper.title}`);
    }

    async analyzePaper() {
        if (!this.selectedPaper) return;
        
        this.showLoading('Analyzing paper and loading full content...');
        
        try {
            // Load full paper content
            await this.loadPaperContent(this.selectedPaper);
            
            // Generate initial analysis
            const analysisPrompt = "Please provide a comprehensive analysis of this paper including: 1) Main contributions, 2) Methodology overview, 3) Key findings, 4) Significance and impact, 5) Potential limitations or areas for future work.";
            
            this.addChatMessage({
                id: this.generateId(),
                content: analysisPrompt,
                role: 'user',
                timestamp: new Date()
            });
            
            await this.sendChatMessage(analysisPrompt);
            
        } catch (error) {
            console.error('Analysis error:', error);
            this.showError('Failed to analyze paper. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    async loadPaperContent(paper) {
        try {
            // Encode the paper ID to handle special characters like /
            const encodedPaperId = encodeURIComponent(paper.id);
            const response = await fetch(`${this.baseUrl}/research/paper/${encodedPaperId}/content`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const contentData = await response.json();
            paper.fullContent = contentData;
            
            // Update paper display if in full view
            if (this.currentView === 'full') {
                this.displayFullPaperContent(paper, contentData);
            }
            
            return contentData;
            
        } catch (error) {
            console.error('Error loading paper content:', error);
            throw error;
        }
    }

    displayPaperDetails(paper) {
        console.log('displayPaperDetails called with paper:', paper);
        const paperViewer = document.getElementById('paperViewer');
        console.log('paperViewer element:', paperViewer);
        
        const content = `
            <div class="paper-header fade-in">
                <h3 class="paper-full-title">${this.escapeHtml(paper.title)}</h3>
                <div class="paper-full-authors">${paper.authors.map(author => this.escapeHtml(author)).join(', ')}</div>
                <div class="paper-full-meta">
                    <span><i class="fas fa-calendar"></i> Published: ${paper.published}</span>
                    <span><i class="fab fa-arxiv"></i> arXiv: ${paper.arxiv_id}</span>
                    <span><i class="fas fa-tag"></i> ${paper.categories.join(', ')}</span>
                </div>
            </div>
            <div class="paper-full-abstract fade-in">
                <h4>Abstract</h4>
                <p>${this.escapeHtml(paper.summary)}</p>
            </div>
        `;
        
        console.log('Setting paperViewer innerHTML with content length:', content.length);
        paperViewer.innerHTML = content;
        console.log('paperViewer innerHTML set successfully');
        
        // Enable controls
        document.getElementById('downloadBtn').disabled = false;
        document.getElementById('summaryBtn').disabled = false;
    }

    displayFullPaperContent(paper, contentData) {
        const paperViewer = document.getElementById('paperViewer');
        
        let displayContent = contentData.content;
        const maxLength = 50000;
        let truncated = false;
        
        if (displayContent.length > maxLength) {
            displayContent = displayContent.substring(0, maxLength) + '\n\n[Content truncated for display...]';
            truncated = true;
        }
        
        const content = `
            <div class="paper-header fade-in">
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
            <div class="paper-full-abstract fade-in">
                <h4>Abstract</h4>
                <p>${this.escapeHtml(paper.summary)}</p>
            </div>
            <div class="paper-full-content fade-in">
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
                ${truncated ? '<div class="truncation-notice"><i class="fas fa-info-circle"></i> Content has been truncated for display.</div>' : ''}
            </div>
        `;
        
        paperViewer.innerHTML = content;
    }

    switchView(view) {
        console.log('switchView called with view:', view);
        console.log('Current selected paper:', this.selectedPaper);
        
        this.currentView = view;
        
        // Update toggle buttons
        console.log('Updating toggle buttons for view:', view);
        document.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('active'));
        const targetBtn = document.getElementById(`${view}ViewBtn`);
        console.log('Target button:', targetBtn);
        if (targetBtn) {
            targetBtn.classList.add('active');
        }
        
        if (!this.selectedPaper) {
            console.log('No selected paper, returning');
            return;
        }
        
        if (view === 'abstract') {
            console.log('Displaying abstract view');
            this.displayPaperDetails(this.selectedPaper);
        } else if (view === 'full') {
            if (this.selectedPaper.fullContent) {
                this.displayFullPaperContent(this.selectedPaper, this.selectedPaper.fullContent);
            } else {
                this.showLoading('Loading full paper content...');
                this.loadPaperContent(this.selectedPaper)
                    .then(() => this.hideLoading())
                    .catch(() => {
                        this.hideLoading();
                        this.showError('Failed to load full content');
                    });
            }
        } else if (view === 'pdf') {
            this.displayPDFView(this.selectedPaper);
        }
    }

    displayPDFView(paper) {
        const paperViewer = document.getElementById('paperViewer');
        
        const content = `
            <div class="paper-header fade-in">
                <h3 class="paper-full-title">${this.escapeHtml(paper.title)}</h3>
                <div class="paper-full-authors">${paper.authors.map(author => this.escapeHtml(author)).join(', ')}</div>
                <div class="paper-full-meta">
                    <span><i class="fas fa-calendar"></i> Published: ${paper.published}</span>
                    <span><i class="fab fa-arxiv"></i> arXiv: ${paper.arxiv_id}</span>
                    <span><i class="fas fa-tag"></i> ${paper.categories.join(', ')}</span>
                </div>
            </div>
            <div class="pdf-viewer-container fade-in">
                <div class="pdf-loading" id="pdfLoading">
                    <i class="fas fa-spinner fa-spin"></i>
                    <p>Loading PDF...</p>
                </div>
                <iframe 
                    id="pdfIframe" 
                    class="pdf-viewer-iframe" 
                    style="display: none;"
                    title="PDF Viewer for ${this.escapeHtml(paper.title)}"
                ></iframe>
            </div>
        `;
        
        paperViewer.innerHTML = content;
        
        // Load PDF
        this.loadPDFInViewer(paper);
    }

    loadPDFInViewer(paper) {
        const iframe = document.getElementById('pdfIframe');
        const loading = document.getElementById('pdfLoading');
        
        // Try to load PDF using different methods
        const pdfUrl = paper.pdf_url;
        
        // Method 1: Try direct PDF embedding
        try {
            iframe.src = pdfUrl + '#view=FitH';
            
            iframe.onload = () => {
                loading.style.display = 'none';
                iframe.style.display = 'block';
            };
            
            iframe.onerror = () => {
                this.showPDFError(paper, pdfUrl);
            };
            
            // Fallback if PDF doesn't load within 10 seconds
            setTimeout(() => {
                if (iframe.style.display === 'none') {
                    this.showPDFError(paper, pdfUrl);
                }
            }, 10000);
            
        } catch (error) {
            this.showPDFError(paper, pdfUrl);
        }
    }

    showPDFError(paper, pdfUrl) {
        const paperViewer = document.getElementById('paperViewer');
        
        const content = `
            <div class="paper-header fade-in">
                <h3 class="paper-full-title">${this.escapeHtml(paper.title)}</h3>
                <div class="paper-full-authors">${paper.authors.map(author => this.escapeHtml(author)).join(', ')}</div>
                <div class="paper-full-meta">
                    <span><i class="fas fa-calendar"></i> Published: ${paper.published}</span>
                    <span><i class="fab fa-arxiv"></i> arXiv: ${paper.arxiv_id}</span>
                    <span><i class="fas fa-tag"></i> ${paper.categories.join(', ')}</span>
                </div>
            </div>
            <div class="pdf-error fade-in">
                <i class="fas fa-exclamation-triangle"></i>
                <h4>PDF Preview Not Available</h4>
                <p>The PDF cannot be displayed in the browser viewer.</p>
            </div>
            <div class="pdf-fallback fade-in">
                <h4><i class="fas fa-external-link-alt"></i> Open PDF Externally</h4>
                <p>Click the link below to open the PDF in a new tab or download it:</p>
                <a href="${pdfUrl}" target="_blank" rel="noopener noreferrer">
                    <i class="fas fa-file-pdf"></i> Open ${paper.arxiv_id}.pdf
                </a>
                <br><br>
                <p><small>Some PDFs may have restrictions that prevent in-browser viewing.</small></p>
            </div>
        `;
        
        paperViewer.innerHTML = content;
    }

    clearPaperViewer() {
        const paperViewer = document.getElementById('paperViewer');
        paperViewer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-file-pdf fa-3x"></i>
                <h3>No Paper Selected</h3>
                <p>Search for papers and select one from the dropdown to view it here</p>
            </div>
        `;
        
        // Disable controls
        document.getElementById('downloadBtn').disabled = true;
        document.getElementById('summaryBtn').disabled = true;
        document.getElementById('abstractViewBtn').disabled = true;
        document.getElementById('fullViewBtn').disabled = true;
        document.getElementById('pdfViewBtn').disabled = true;
        
        // Clear active view state
        document.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('active'));
    }

    async sendChatMessage(customMessage = null) {
        const chatInput = document.getElementById('chatInput');
        const message = customMessage || chatInput.value.trim();
        
        if (!message) return;
        
        if (!this.selectedPaper) {
            this.showError('Please select a paper first to start chatting');
            return;
        }

        // Clear welcome messages on first user interaction
        this.removeWelcomeMessages();

        // Add user message if not a custom message
        if (!customMessage) {
            const userMessage = {
                id: this.generateId(),
                content: message,
                role: 'user',
                timestamp: new Date()
            };
            this.addChatMessage(userMessage);
            chatInput.value = '';
        }

        // Show AI thinking with Gemini-style loader
        const thinkingId = this.generateId();
        this.addGeminiLoader(thinkingId);

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
                    conversation_history: this.getCurrentNotesFile().messages.slice(-10).map(msg => ({
                        role: msg.role,
                        content: msg.content
                    })),
                    paper_content: this.getCurrentPaperText() // Include current paper text
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Remove thinking message
            this.removeGeminiLoader(thinkingId);
            
            // Add AI response with typing animation
            const aiMessage = {
                id: this.generateId(),
                content: data.response,
                role: 'ai',
                timestamp: new Date(),
                editable: true
            };
            this.addTypingMessage(aiMessage);

        } catch (error) {
            console.error('Chat error:', error);
            this.removeGeminiLoader(thinkingId);
            this.addChatMessage({
                id: this.generateId(),
                content: 'Sorry, I encountered an error while processing your message. Please try again.',
                role: 'ai',
                timestamp: new Date()
            });
        }
    }

    addGeminiLoader(loaderId) {
        const chatMessages = document.getElementById('chatMessages');
        const loaderDiv = document.createElement('div');
        loaderDiv.className = 'loading-message';
        loaderDiv.dataset.messageId = loaderId;
        
        loaderDiv.innerHTML = `
            <div class="ai-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="gemini-loader">
                <hr/>
                <hr/>
                <hr/>
            </div>
        `;
        
        chatMessages.appendChild(loaderDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    removeGeminiLoader(loaderId) {
        const loaderElement = document.querySelector(`[data-message-id="${loaderId}"]`);
        if (loaderElement) {
            loaderElement.remove();
        }
    }

    addTypingMessage(message) {
        // Clear welcome screen first
        const chatMessages = document.getElementById('chatMessages');
        const hasWelcome = chatMessages.querySelector('.welcome-message');
        const hasSuggestions = chatMessages.querySelector('.suggestion-cards');
        
        if (hasWelcome || hasSuggestions) {
            chatMessages.innerHTML = '';
        }
        
        const notesFile = this.getCurrentNotesFile();
        notesFile.messages.push(message);
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message ai editable';
        messageDiv.dataset.messageId = message.id;
        messageDiv.addEventListener('click', () => this.makeMessageEditable(message.id));
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <div class="ai-avatar">
                    <i class="fas fa-robot"></i>
                </div>
            </div>
            <div class="message-content"></div>
            <div class="message-actions">
                <button class="message-action-btn" onclick="app.editMessage('${message.id}')">
                    <i class="fas fa-edit"></i> Edit
                </button>
                <button class="message-action-btn" onclick="app.copyMessage('${message.id}')">
                    <i class="fas fa-copy"></i> Copy
                </button>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        
        // Start typing animation
        this.typeMessage(message.id, message.content);
        
        this.updateWordCount();
        this.autoSaveNotes();
    }

    typeMessage(messageId, content) {
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        const contentElement = messageElement?.querySelector('.message-content');
        
        if (!contentElement) return;
        
        const formattedContent = this.formatAIResponse(content);
        const words = formattedContent.split(' ');
        let currentIndex = 0;
        
        const typeInterval = setInterval(() => {
            if (currentIndex < words.length) {
                const currentText = words.slice(0, currentIndex + 1).join(' ');
                contentElement.innerHTML = currentText;
                currentIndex++;
                
                // Auto-scroll to bottom
                const chatMessages = document.getElementById('chatMessages');
                chatMessages.scrollTop = chatMessages.scrollHeight;
            } else {
                clearInterval(typeInterval);
                // Show final formatted content
                contentElement.innerHTML = formattedContent;
            }
        }, 75); // Typing speed similar to Gemini
    }

    performQuickAction(action) {
        if (!this.selectedPaper) {
            this.showError('Please select a paper first');
            return;
        }

        const prompts = {
            explain: "Please provide a comprehensive explanation of this paper in simple terms, covering the main ideas, methodology, and significance.",
            methodology: "Explain the methodology used in this paper in detail. What approaches, techniques, or experiments were employed?",
            results: "Summarize the key results and findings from this paper. What are the main outcomes and their significance?",
            limitations: "What are the limitations, potential issues, or areas for future work mentioned in this paper?"
        };

        const prompt = prompts[action];
        if (prompt) {
            document.getElementById('chatInput').value = prompt;
            this.sendChatMessage();
        }
    }

    addChatMessage(message) {
        const notesFile = this.getCurrentNotesFile();
        notesFile.messages.push(message);
        
        // Clear welcome screen when first real message is added
        const chatMessages = document.getElementById('chatMessages');
        const hasWelcome = chatMessages.querySelector('.welcome-message');
        const hasSuggestions = chatMessages.querySelector('.suggestion-cards');
        
        if ((hasWelcome || hasSuggestions) && !message.isWelcome && message.role !== 'system') {
            chatMessages.innerHTML = '';
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${message.role}`;
        messageDiv.dataset.messageId = message.id;
        
        if (message.role === 'ai' && message.editable) {
            messageDiv.classList.add('editable');
            messageDiv.addEventListener('click', () => this.makeMessageEditable(message.id));
        }
        
        // Format content for different message types
        let formattedContent = message.content;
        if (message.role === 'ai') {
            formattedContent = this.formatAIResponse(message.content);
        } else if (message.role === 'system') {
            formattedContent = `<p style="font-style: italic; color: #718096;">${this.escapeHtml(message.content)}</p>`;
        }
        
        // Gemini-style message structure
        if (message.role === 'user') {
            messageDiv.innerHTML = `
                <div class="message-header">
                    <div class="user-avatar">U</div>
                </div>
                <div class="message-content">${this.escapeHtml(message.content)}</div>
                <div class="message-time">${message.timestamp.toLocaleTimeString()}</div>
            `;
        } else if (message.role === 'ai') {
            messageDiv.innerHTML = `
                <div class="message-header">
                    <div class="ai-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                </div>
                <div class="message-content">${formattedContent}</div>
                ${message.editable ? `
                    <div class="message-actions">
                        <button class="message-action-btn" onclick="app.editMessage('${message.id}')">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="message-action-btn" onclick="app.copyMessage('${message.id}')">
                            <i class="fas fa-copy"></i> Copy
                        </button>
                    </div>
                ` : ''}
            `;
        } else if (message.role === 'system') {
            messageDiv.innerHTML = `
                <div class="message-content">${formattedContent}</div>
                <div class="message-time">${message.timestamp.toLocaleTimeString()}</div>
            `;
        }

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        this.updateWordCount();
        this.autoSaveNotes();
    }

    formatAIResponse(content) {
        // Escape HTML first to prevent XSS
        const escapeHtml = (text) => {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        };
        
        // Convert markdown-like formatting to HTML while preserving natural formatting
        let formatted = content
            .replace(/\n\s*\n/g, '\n\n')
            .replace(/[ \t]+/g, ' ')
            .trim();

        // Split into paragraphs
        const paragraphs = formatted.split('\n\n').filter(p => p.trim());
        
        return paragraphs.map(paragraph => {
            let para = paragraph.trim();
            
            // Handle headers
            if (para.match(/^#{1,6}\s+(.+)$/)) {
                const headerMatch = para.match(/^(#{1,6})\s+(.+)$/);
                const level = headerMatch[1].length;
                const text = escapeHtml(headerMatch[2]);
                return `<h${Math.min(level, 3)}>${text}</h${Math.min(level, 3)}>`;
            }
            
            // Handle bullet points
            if (para.includes('\n') && para.match(/^\s*[\*\-\+]\s/m)) {
                const items = para.split('\n').map(line => line.trim()).filter(line => line);
                const listItems = items.map(item => {
                    const cleanItem = item.replace(/^\s*[\*\-\+]\s+/, '');
                    return `<li>${escapeHtml(cleanItem)}</li>`;
                }).join('');
                return `<ul>${listItems}</ul>`;
            }
            
            // Handle numbered lists
            if (para.includes('\n') && para.match(/^\s*\d+\.\s/m)) {
                const items = para.split('\n').map(line => line.trim()).filter(line => line);
                const listItems = items.map(item => {
                    const cleanItem = item.replace(/^\s*\d+\.\s+/, '');
                    return `<li>${escapeHtml(cleanItem)}</li>`;
                }).join('');
                return `<ol>${listItems}</ol>`;
            }
            
            // Clean up single-line bullets/numbers
            para = para.replace(/^\s*[\*\-\+]\s+/, '');
            para = para.replace(/^\s*\d+\.\s+/, '');
            
            // Escape the paragraph content first
            let escapedPara = escapeHtml(para);
            
            // Then apply HTML formatting
            escapedPara = escapedPara
                // Bold text
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/__(.*?)__/g, '<strong>$1</strong>')
                // Italic text  
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/_(.*?)_/g, '<em>$1</em>')
                // Code inline
                .replace(/`(.*?)`/g, '<code>$1</code>');
            
            return `<p>${escapedPara}</p>`;
        }).join('');
    }

    makeMessageEditable(messageId) {
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        const contentElement = messageElement.querySelector('.message-content');
        const currentText = contentElement.textContent;
        
        contentElement.innerHTML = `
            <textarea class="edit-textarea" style="width: 100%; min-height: 100px; border: none; background: transparent; resize: vertical; font-family: inherit; font-size: inherit;">${currentText}</textarea>
            <div class="edit-actions" style="margin-top: 10px;">
                <button class="btn primary" onclick="app.saveMessageEdit('${messageId}')">Save</button>
                <button class="btn secondary" onclick="app.cancelMessageEdit('${messageId}', '${this.escapeHtml(currentText)}')">Cancel</button>
            </div>
        `;
        
        const textarea = contentElement.querySelector('.edit-textarea');
        textarea.focus();
        textarea.select();
    }

    saveMessageEdit(messageId) {
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        const textarea = messageElement.querySelector('.edit-textarea');
        const newText = textarea.value;
        
        // Update the message in the data
        const notesFile = this.getCurrentNotesFile();
        const message = notesFile.messages.find(m => m.id === messageId);
        if (message) {
            message.content = newText;
        }
        
        // Update the display with properly formatted content
        const contentElement = messageElement.querySelector('.message-content');
        if (message && message.role === 'ai') {
            contentElement.innerHTML = this.formatAIResponse(newText);
        } else {
            contentElement.innerHTML = this.escapeHtml(newText);
        }
        
        // Remove editable class temporarily to show the change is saved
        messageElement.classList.remove('editable');
        setTimeout(() => {
            messageElement.classList.add('editable');
        }, 100);
        
        this.autoSaveNotes();
        this.showSuccessMessage('Message updated successfully');
    }

    cancelMessageEdit(messageId, originalText) {
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        const contentElement = messageElement.querySelector('.message-content');
        
        // Get the original message to restore proper formatting
        const notesFile = this.getCurrentNotesFile();
        const message = notesFile.messages.find(m => m.id === messageId);
        
        if (message && message.role === 'ai') {
            contentElement.innerHTML = this.formatAIResponse(message.content);
        } else {
            contentElement.innerHTML = this.escapeHtml(message.content);
        }
    }

    editMessage(messageId) {
        this.makeMessageEditable(messageId);
    }

    copyMessage(messageId) {
        const notesFile = this.getCurrentNotesFile();
        const message = notesFile.messages.find(m => m.id === messageId);
        if (message) {
            navigator.clipboard.writeText(message.content).then(() => {
                this.showSuccessMessage('Message copied to clipboard');
            });
        }
    }

    removeChatMessage(messageId) {
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        if (messageElement) {
            messageElement.remove();
        }
        
        const notesFile = this.getCurrentNotesFile();
        notesFile.messages = notesFile.messages.filter(msg => msg.id !== messageId);
    }

    // Notes Management
    showCreateNotesModal() {
        const modal = document.getElementById('notesModal');
        modal.classList.remove('hidden');
        document.getElementById('notesName').focus();
    }

    hideCreateNotesModal() {
        const modal = document.getElementById('notesModal');
        modal.classList.add('hidden');
        document.getElementById('notesName').value = '';
    }

    createNewNotesFile() {
        const nameInput = document.getElementById('notesName');
        const name = nameInput.value.trim();
        
        if (!name) {
            this.showError('Please enter a name for the notes file');
            return;
        }
        
        const noteId = this.generateId();
        this.notesFiles.set(noteId, {
            name: name,
            content: '',
            messages: []
        });
        
        this.switchNotesFile(noteId);
        this.updateNotesDropdown();
        this.hideCreateNotesModal();
        this.showSuccessMessage(`Created new notes file: ${name}`);
    }

    switchNotesFile(noteId) {
        this.currentNotesId = noteId;
        
        // Clear current chat and load new messages
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = '';
        
        const notesFile = this.getCurrentNotesFile();
        notesFile.messages.forEach(message => {
            this.displayExistingMessage(message);
        });
        
        if (notesFile.messages.length === 0) {
            this.showWelcomeMessage();
        }
        
        this.updateWordCount();
        this.updateNotesDropdown();
    }

    displayExistingMessage(message) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${message.role}`;
        messageDiv.dataset.messageId = message.id;
        
        if (message.role === 'ai' && message.editable) {
            messageDiv.classList.add('editable');
        }
        
        // Format content for AI messages
        let formattedContent = message.content;
        if (message.role === 'ai') {
            formattedContent = this.formatAIResponse(message.content);
        }
        
        messageDiv.innerHTML = `
            <div class="message-content">${message.role === 'ai' ? formattedContent : this.escapeHtml(message.content)}</div>
            <div class="message-time">${message.timestamp.toLocaleTimeString()}</div>
            ${message.role === 'ai' && message.editable ? `
                <div class="message-actions">
                    <button class="message-action-btn" onclick="app.editMessage('${message.id}')">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="message-action-btn" onclick="app.copyMessage('${message.id}')">
                        <i class="fas fa-copy"></i> Copy
                    </button>
                </div>
            ` : ''}
        `;

        chatMessages.appendChild(messageDiv);
    }

    updateNotesDropdown() {
        const dropdown = document.getElementById('notesDropdown');
        dropdown.innerHTML = '';
        
        this.notesFiles.forEach((notesFile, noteId) => {
            const option = document.createElement('option');
            option.value = noteId;
            option.textContent = notesFile.name;
            option.selected = noteId === this.currentNotesId;
            dropdown.appendChild(option);
        });
    }

    getCurrentNotesFile() {
        return this.notesFiles.get(this.currentNotesId);
    }

    saveCurrentNotes() {
        this.saveNotesToStorage();
        this.showSuccessMessage('Notes saved successfully');
    }

    autoSaveNotes() {
        if (this.autoSaveTimer) {
            clearTimeout(this.autoSaveTimer);
        }
        
        this.autoSaveTimer = setTimeout(() => {
            this.saveNotesToStorage();
        }, 2000);
    }

    saveNotesToStorage() {
        const notesData = {};
        this.notesFiles.forEach((notesFile, noteId) => {
            notesData[noteId] = notesFile;
        });
        
        localStorage.setItem('research_notes_redesigned', JSON.stringify(notesData));
        localStorage.setItem('research_current_notes_id', this.currentNotesId);
    }

    loadSavedNotes() {
        try {
            const saved = localStorage.getItem('research_notes_redesigned');
            const currentId = localStorage.getItem('research_current_notes_id');
            
            if (saved) {
                const notesData = JSON.parse(saved);
                this.notesFiles.clear();
                
                Object.entries(notesData).forEach(([noteId, notesFile]) => {
                    this.notesFiles.set(noteId, {
                        ...notesFile,
                        messages: notesFile.messages.map(msg => ({
                            ...msg,
                            timestamp: new Date(msg.timestamp)
                        }))
                    });
                });
                
                if (currentId && this.notesFiles.has(currentId)) {
                    this.currentNotesId = currentId;
                }
            }
        } catch (error) {
            console.error('Error loading saved notes:', error);
        }
    }

    setupAutoSave() {
        // Auto-save every 30 seconds
        setInterval(() => {
            this.saveNotesToStorage();
        }, 30000);
    }

    // Helper to get the full text of the selected paper
    getCurrentPaperText() {
        if (this.selectedPaper && this.selectedPaper.fullContent && this.selectedPaper.fullContent.content) {
            return this.selectedPaper.fullContent.content;
        }
        return '';
    }

    // Analysis Menu Functions
    showAnalysisMenu() {
        if (!this.selectedPaper) {
            this.showError('Please select a paper first to access analysis features');
            return;
        }
        
        const modal = document.getElementById('analysisModal');
        modal.classList.remove('hidden');
    }

    hideAnalysisMenu() {
        const modal = document.getElementById('analysisModal');
        modal.classList.add('hidden');
    }

    hideSectionMenu() {
        const modal = document.getElementById('sectionModal');
        modal.classList.add('hidden');
        
        // Hide custom input if visible
        const customInput = document.getElementById('customSectionInput');
        customInput.classList.add('hidden');
        document.getElementById('customSectionText').value = '';
    }

    handleAnalysisSelection(analysisType) {
        this.hideAnalysisMenu();
        
        switch(analysisType) {
            case 'comprehensive':
                this.performComprehensiveAnalysis();
                break;
            case 'section':
                this.showSectionSelector();
                break;
            case 'notes':
                this.generateSmartNotes();
                break;
            case 'compare':
                this.performCriticalEvaluation();
                break;
        }
    }

    showSectionSelector() {
        const modal = document.getElementById('sectionModal');
        modal.classList.remove('hidden');
    }

    handleSectionSelection(sectionType) {
        if (sectionType === 'custom') {
            const customInput = document.getElementById('customSectionInput');
            customInput.classList.remove('hidden');
            document.getElementById('customSectionText').focus();
        } else {
            this.hideSectionMenu();
            this.analyzePaperSection(sectionType);
        }
    }

    analyzeCustomSection() {
        const customText = document.getElementById('customSectionText').value.trim();
        if (!customText) {
            this.showError('Please enter some text to analyze');
            return;
        }
        
        this.hideSectionMenu();
        this.analyzeCustomText(customText);
    }

    performComprehensiveAnalysis() {
        const paperText = this.getCurrentPaperText();
        const comprehensivePrompt = `Please provide a comprehensive analysis of this paper using the following structured format:

## Main Problem & Motivation
- What problem does this paper aim to solve?
- Why is this problem important in the field?
- What gap in existing research does it fill?

## Core Contribution (Big Idea)
- What is the key innovation or contribution of the paper?
- Explain in one simple sentence, then in more technical detail.

## Methodology (How it Works)
- Describe the approach in simple terms
- Include analogies or examples where helpful
- Highlight what makes this method different from previous ones

## Experiments & Results
- What experiments were run? On which datasets?
- How well did the approach perform compared to baselines?
- Key findings and statistical results

## Significance & Applications
- Why do these results matter?
- Real-world applications or future research opportunities
- How it moves the field forward

## Limitations & Open Questions
- Challenges or weaknesses acknowledged by authors
- Unanswered questions for future work

## Critical Evaluation
- Strengths: What this paper does very well
- Weaknesses: What could be improved or is missing
- Overall importance in its research domain

## Simplified Summary
- Summarize in 5-6 beginner-friendly sentences
- Provide a 1-line TL;DR for quick recall

---
Here is the full text of the paper for your analysis:
"""
${paperText}
"""
`;
        this.addChatMessage({
            id: this.generateId(),
            content: comprehensivePrompt,
            role: 'user',
            timestamp: new Date()
        });
        this.sendChatMessage(comprehensivePrompt);
    }

    analyzePaperSection(sectionType) {
        const sectionPrompts = {
            abstract: "Please analyze the abstract of this paper. Explain what the authors claim to have achieved, the key methodology, and the main results. How well does the abstract represent the full paper?",
            introduction: "Analyze the introduction section. What background context do the authors provide? How do they motivate the problem? What is their main research question or hypothesis?",
            methodology: "Provide a detailed analysis of the methodology section. Explain the approach in simple terms, what makes it novel, and how it differs from existing methods. Include any important technical details.",
            results: "Analyze the results section. What are the key findings? How do they compare to baselines or previous work? What do the numbers and experiments actually show?",
            discussion: "Examine the discussion section. How do the authors interpret their results? What implications do they draw? What limitations do they acknowledge?",
            conclusion: "Analyze the conclusion. What are the main takeaways? What future work do they suggest? How significant are the contributions claimed?"
        };
        const paperText = this.getCurrentPaperText();
        const prompt = sectionPrompts[sectionType];
        if (prompt) {
            const sectionPrompt = `${prompt}
\n---\nHere is the full text of the paper for your analysis:\n"""\n${paperText}\n"""\n`;
            this.addChatMessage({
                id: this.generateId(),
                content: sectionPrompt,
                role: 'user',
                timestamp: new Date()
            });
            this.sendChatMessage(sectionPrompt);
        }
    }

    generateSmartNotes() {
        const paperText = this.getCurrentPaperText();
        const notesPrompt = `Please create comprehensive study notes for this paper in a structured format that would be useful for:
- Students learning about this topic
- Researchers in related fields
- Anyone preparing for exams or presentations

Include:
- Key concepts and definitions
- Important equations or algorithms (if any)
- Main arguments and evidence
- Connections to other work in the field
- Practical implications
- Questions for further investigation

Format the notes in a clear, organized way with headers and bullet points.

---
Here is the full text of the paper for your notes:
"""
${paperText}
"""
`;
        this.addChatMessage({
            id: this.generateId(),
            content: notesPrompt,
            role: 'user',
            timestamp: new Date()
        });
        this.sendChatMessage(notesPrompt);
    }

    performCriticalEvaluation() {
        const paperText = this.getCurrentPaperText();
        const evaluationPrompt = `Please provide a critical evaluation of this paper. Analyze:

## Strengths
- What does this paper do exceptionally well?
- Novel contributions and innovations
- Methodological rigor
- Clarity of presentation

## Weaknesses
- What could be improved?
- Missing comparisons or baselines
- Limitations in methodology or evaluation
- Unclear or problematic claims

## Significance
- How important is this work in its field?
- Will it likely be influential? Why or why not?
- Does it open new research directions?

## Technical Assessment
- Are the methods sound?
- Are the experiments comprehensive?
- Are the conclusions well-supported?

## Overall Verdict
- Rate the paper's contribution (major/moderate/minor)
- Who would find this work most valuable?
- What are the key takeaways for the field?

Please be balanced but honest in your assessment.

---
Here is the full text of the paper for your evaluation:
"""
${paperText}
"""
`;
        this.addChatMessage({
            id: this.generateId(),
            content: evaluationPrompt,
            role: 'user',
            timestamp: new Date()
        });
        this.sendChatMessage(evaluationPrompt);
    }

    async generateSummary() {
        if (!this.selectedPaper) return;
        
        const prompt = "Please provide a detailed summary of this paper including: 1) Abstract summary, 2) Main objectives, 3) Key methodology, 4) Primary results, 5) Conclusions and implications.";
        document.getElementById('chatInput').value = prompt;
        await this.sendChatMessage();
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
            
            this.showSuccessMessage('PDF downloaded successfully');
            
        } catch (error) {
            console.error('Download error:', error);
            this.showError('Failed to download PDF');
        } finally {
            this.hideLoading();
        }
    }

    updateStatus(message = null) {
        const paperStatus = document.getElementById('paperStatus');
        const notesStatus = document.getElementById('notesStatus');
        
        if (message) {
            paperStatus.innerHTML = `<i class="fas fa-file"></i> ${message}`;
        }
        
        const notesFile = this.getCurrentNotesFile();
        const notesCount = notesFile.messages.filter(m => m.role === 'ai').length;
        notesStatus.innerHTML = `<i class="fas fa-sticky-note"></i> ${notesCount} notes`;
    }

    updateWordCount() {
        const wordCount = document.getElementById('wordCount');
        const notesFile = this.getCurrentNotesFile();
        const totalWords = notesFile.messages
            .map(m => m.content.split(/\s+/).filter(word => word.length > 0).length)
            .reduce((sum, count) => sum + count, 0);
        
        wordCount.innerHTML = `<i class="fas fa-font"></i> ${totalWords} words`;
    }

    showWelcomeMessage() {
        // Only show welcome if no paper is selected and no previous messages
        const notesFile = this.getCurrentNotesFile();
        if (notesFile.messages.length > 0) {
            return; // Don't show welcome if there are already messages
        }
        
        const chatMessages = document.getElementById('chatMessages');
        
        if (this.selectedPaper) {
            // Show Gemini-style suggestions for the selected paper
            chatMessages.innerHTML = `
                <div class="welcome-message">
                    <i class="fas fa-robot"></i>
                    <h2><span>Hello, Researcher</span></h2>
                    <p>I can help you analyze "${this.selectedPaper.title.substring(0, 50)}..."</p>
                </div>
                <div class="suggestion-cards">
                    <button class="suggestion-card" onclick="app.performComprehensiveAnalysis()">
                        <p>Comprehensive structured analysis covering all aspects of the paper</p>
                        <i class="fas fa-microscope"></i>
                    </button>
                    <button class="suggestion-card" onclick="app.showSectionSelector()">
                        <p>Analyze specific sections like methodology, results, or conclusions</p>
                        <i class="fas fa-search"></i>
                    </button>
                    <button class="suggestion-card" onclick="app.generateSmartNotes()">
                        <p>Generate structured study notes and key takeaways</p>
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="suggestion-card" onclick="app.performCriticalEvaluation()">
                        <p>Critical evaluation of strengths, weaknesses, and significance</p>
                        <i class="fas fa-balance-scale"></i>
                    </button>
                </div>
            `;
        } else {
            // Show general welcome message
            chatMessages.innerHTML = `
                <div class="welcome-message">
                    <i class="fas fa-robot"></i>
                    <h2><span>Hello, Researcher</span></h2>
                    <p>How can I help you with academic paper analysis today?</p>
                </div>
                <div class="suggestion-cards">
                    <button class="suggestion-card" onclick="document.getElementById('searchInput').focus()">
                        <p>Search for academic papers on any research topic</p>
                        <i class="fas fa-search"></i>
                    </button>
                    <button class="suggestion-card" onclick="app.showExample('quantum computing')">
                        <p>Show me papers about quantum computing</p>
                        <i class="fas fa-atom"></i>
                    </button>
                    <button class="suggestion-card" onclick="app.showExample('machine learning')">
                        <p>Find recent machine learning research</p>
                        <i class="fas fa-brain"></i>
                    </button>
                    <button class="suggestion-card" onclick="app.showExample('climate change')">
                        <p>Explore climate change studies</p>
                        <i class="fas fa-leaf"></i>
                    </button>
                </div>
            `;
        }
    }

    showExample(query) {
        document.getElementById('searchInput').value = query;
        this.performSearch();
    }

    showLoading(message = 'Loading...') {
        console.log('showLoading called with message:', message);
        this.updateStatus(message);
        // You can add more loading UI here if needed
    }

    hideLoading() {
        console.log('hideLoading called');
        // You can add more loading UI cleanup here if needed
    }

    showError(message) {
        console.error('Error:', message);
        this.updateStatus(`Error: ${message}`);
        // You can add more error UI here if needed
    }

    showSuccessMessage(message) {
        console.log('Success:', message);
        this.updateStatus(message);
        // You can add more success UI here if needed
    }
}

// Initialize the application
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new ResearchAgentRedesigned();
    window.app = app;
    console.log('Research Agent Redesigned initialized successfully');
});

// Export for global access
window.app = app;
