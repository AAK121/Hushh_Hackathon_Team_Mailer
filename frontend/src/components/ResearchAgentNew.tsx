import React, { useRef, useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import './ResearchAgentNew.css';
import { researchAgentApi, Paper } from '../services/ResearchAgentApi';

// Chat message interface
interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'ai' | 'system';
  timestamp: Date;
}

const ResearchAgentNew: React.FC = () => {
  const [leftPanelWidth, setLeftPanelWidth] = useState(55); // Initial width as percentage
  const [isResizing, setIsResizing] = useState(false);
  const [activeView, setActiveView] = useState<'abstract' | 'pdf'>('abstract');
  
  // Chat-related state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [isSendingMessage, setIsSendingMessage] = useState(false);
  
  // Research-related state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Paper[]>([]);
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected'>('disconnected');
  
  // Modal and notes state
  const [showNotesModal, setShowNotesModal] = useState(false);
  const [showEditNotesModal, setShowEditNotesModal] = useState(false);
  const [showNotesListModal, setShowNotesListModal] = useState(false);
  const [notesFileName, setNotesFileName] = useState('');
  const [currentNotes, setCurrentNotes] = useState('');
  const [editingNotesName, setEditingNotesName] = useState('');
  const [editingNotesContent, setEditingNotesContent] = useState('');
  const [savedNotes, setSavedNotes] = useState<Record<string, string>>({});
  const [selectedNotesName, setSelectedNotesName] = useState<string>('current');
  const [currentNoteMessageId, setCurrentNoteMessageId] = useState<string | null>(null);
  
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing || !containerRef.current) return;

      const containerRect = containerRef.current.getBoundingClientRect();
      const newLeftWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
      
      // Constrain the width between 20% and 80%
      const constrainedWidth = Math.min(Math.max(newLeftWidth, 20), 80);
      setLeftPanelWidth(constrainedWidth);
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing]);

  const handleMouseDown = () => {
    setIsResizing(true);
  };

  const handleViewChange = (view: 'abstract' | 'pdf') => {
    setActiveView(view);
  };

  // Chat functionality
  const addChatMessage = (message: ChatMessage) => {
    setChatMessages(prev => [...prev, message]);
  };

  const generateId = () => {
    return Math.random().toString(36).substr(2, 9);
  };

  const handleSendMessage = async () => {
    const message = chatInput.trim();
    if (!message || isSendingMessage) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: generateId(),
      content: message,
      role: 'user',
      timestamp: new Date()
    };
    addChatMessage(userMessage);
    setChatInput('');
    setIsSendingMessage(true);

    try {
      // Enhanced message with paper context if available
      let enhancedMessage = message;
      if (selectedPaper) {
        enhancedMessage = `Context: I'm discussing the paper "${selectedPaper.title}" by ${selectedPaper.authors.join(', ')}. 

Paper Abstract: ${selectedPaper.summary}

ArXiv ID: ${selectedPaper.arxiv_id}
Categories: ${selectedPaper.categories.join(', ')}

User Question: ${message}`;
      }

      // Send message to research agent API
      const response = await researchAgentApi.sendChatMessage(enhancedMessage, selectedPaper?.id);
      
      const aiMessage: ChatMessage = {
        id: generateId(),
        content: response.message,
        role: 'ai',
        timestamp: new Date()
      };
      addChatMessage(aiMessage);

      // Auto-save AI response to "AI Responses" notes
      await saveAiResponseToNotes(response.message, message, selectedPaper);
      
    } catch (error) {
      console.error('Failed to send message:', error);
      
      // Display error message to user
      const errorMessage: ChatMessage = {
        id: generateId(),
        content: `Sorry, I couldn't process your request. The research agent appears to be unavailable. Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        role: 'ai',
        timestamp: new Date()
      };
      addChatMessage(errorMessage);
    } finally {
      setIsSendingMessage(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Search functionality
  const handleSearch = async () => {
    const query = searchQuery.trim();
    if (!query || isSearching) return;

    setIsSearching(true);
    
    try {
      const response = await researchAgentApi.searchPapers(query, 20);
      setSearchResults(response.papers);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: generateId(),
        content: `Search failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        role: 'system',
        timestamp: new Date()
      };
      addChatMessage(errorMessage);
    } finally {
      setIsSearching(false);
    }
  };

  const handlePaperSelect = (paper: Paper) => {
    setSelectedPaper(paper);
    
    // Remove paper selection notification - user can see it's selected in the UI
    /*
    const systemMessage: ChatMessage = {
      id: generateId(),
      content: `Selected paper: "${paper.title}" by ${paper.authors.join(', ')}. You can now ask questions about this paper.`,
      role: 'system',
      timestamp: new Date()
    };
    addChatMessage(systemMessage);
    */
  };

  // Notes functionality
  const handleNotesModalOpen = () => {
    setShowNotesModal(true);
  };

  const handleCreateNotes = async () => {
    if (!notesFileName.trim()) {
      alert('Please enter a notes file name');
      return;
    }

    const fileName = `${notesFileName}_${Date.now()}`;
    const contentToSave = currentNotes.trim() || (selectedPaper ? 
      `# Research Notes: ${selectedPaper.title}\n\n## Paper Details\n- **Authors:** ${selectedPaper.authors.join(', ')}\n- **Published:** ${selectedPaper.published}\n- **ArXiv ID:** ${selectedPaper.arxiv_id}\n\n## Abstract\n${selectedPaper.summary}\n\n## Notes\n[Add your notes here]\n\n## Key Insights\n[Add key insights here]\n\n## Questions\n[Add questions here]` :
      '# Research Notes\n\n[Add your notes here]');

    await saveNotesToVault(fileName, contentToSave);
    setCurrentNotes('');
    setNotesFileName('');
    setSelectedNotesName('current'); // Reset dropdown to current session
    setShowNotesModal(false);

    // Remove notes creation notification - user can see it in the notes counter
    /*
    const systemMessage: ChatMessage = {
      id: generateId(),
      content: `Created new notes file: "${fileName}". Notes saved to vault.`,
      role: 'system',
      timestamp: new Date()
    };
    addChatMessage(systemMessage);
    */
  };

  const handleEditNotes = async (notesName: string) => {
    try {
      setEditingNotesName(notesName);
      
      // Load the note content from the vault
      const content = await researchAgentApi.getNote(notesName);
      setEditingNotesContent(content || savedNotes[notesName] || '');
      
      setShowEditNotesModal(true);
      setShowNotesListModal(false);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: generateId(),
        content: `Failed to load note "${notesName}": ${error instanceof Error ? error.message : 'Unknown error'}`,
        role: 'system',
        timestamp: new Date()
      };
      addChatMessage(errorMessage);
    }
  };

  const handleShowNotesListForEdit = () => {
    const notesNames = Object.keys(savedNotes);
    if (notesNames.length > 0) {
      setShowNotesListModal(true);
    } else {
      const errorMessage: ChatMessage = {
        id: generateId(),
        content: 'No saved notes to edit. Please create notes first.',
        role: 'system',
        timestamp: new Date()
      };
      addChatMessage(errorMessage);
    }
  };

  const handleSaveEditedNotes = async () => {
    if (!editingNotesName.trim() || !editingNotesContent.trim()) return;
    
    try {
      // Update the note using the API
      await researchAgentApi.updateNote(editingNotesName, editingNotesContent);
      
      // Update local state
      setSavedNotes(prev => ({
        ...prev,
        [editingNotesName]: editingNotesContent
      }));

      // Reload notes from vault to ensure consistency
      await loadNotesFromVault();
      
      setShowEditNotesModal(false);
      setEditingNotesName('');
      setEditingNotesContent('');
      
      // Remove notes update success message - user can see the changes
      /*
      const successMessage: ChatMessage = {
        id: generateId(),
        content: `✅ Notes "${editingNotesName}" updated successfully!`,
        role: 'system',
        timestamp: new Date()
      };
      addChatMessage(successMessage);
      */
      
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: generateId(),
        content: `Failed to update notes: ${error instanceof Error ? error.message : 'Unknown error'}`,
        role: 'system',
        timestamp: new Date()
      };
      addChatMessage(errorMessage);
    }
  };

  // Save AI response to "AI Responses" notes
  const saveAiResponseToNotes = async (aiResponse: string, userQuestion: string, paper: Paper | null) => {
    try {
      const timestamp = new Date().toLocaleString();
      const paperContext = paper ? 
        `Paper: "${paper.title}" by ${paper.authors.join(', ')}\nArXiv ID: ${paper.arxiv_id}\n\n` : 
        '';
      
      const noteEntry = `## ${timestamp}\n\n${paperContext}**Question:** ${userQuestion}\n\n**AI Response:**\n${aiResponse}\n\n---\n\n`;
      
      // Load existing AI Responses notes
      const existingAiNotes = await researchAgentApi.getNote('AI Responses') || '';
      
      // Prepend new entry to existing notes (most recent first)
      const updatedNotes = noteEntry + existingAiNotes;
      
      // Save back to notes
      await researchAgentApi.updateNote('AI Responses', updatedNotes);
      
      // Update local saved notes state to reflect the change
      setSavedNotes(prev => ({
        ...prev,
        'AI Responses': updatedNotes
      }));
      
      console.log('AI response saved to "AI Responses" notes');
    } catch (error) {
      console.error('Failed to save AI response to notes:', error);
    }
  };

  // Load notes from vault
  const loadNotesFromVault = async () => {
    try {
      const notes = await researchAgentApi.loadNotes();
      setSavedNotes(notes);
      console.log('Loaded notes from vault:', notes);
      
      // Add a system message when notes are loaded
      if (Object.keys(notes).length > 0) {
        // Remove this message - user doesn't need to see notes loaded notification
        /*
        const systemMessage: ChatMessage = {
          id: generateId(),
          content: `📝 Loaded ${Object.keys(notes).length} saved notes from vault.`,
          role: 'system',
          timestamp: new Date()
        };
        addChatMessage(systemMessage);
        */
      }
    } catch (error) {
      console.error('Failed to load notes from vault:', error);
    }
  };

  // Handle notes dropdown selection change
  const handleNotesDropdownChange = async (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedValue = event.target.value;
    setSelectedNotesName(selectedValue);
    
    if (selectedValue === 'current') {
      // Keep current session notes as is
      return;
    } else if (selectedValue === 'clear') {
      // Remove the currently displayed note from chat
      if (currentNoteMessageId) {
        setChatMessages(prev => 
          prev.filter(msg => msg.id !== currentNoteMessageId)
        );
        setCurrentNoteMessageId(null);
      }
      setSelectedNotesName('current'); // Reset to current session
      return;
    } else {
      // Load the selected saved note and display its content in chat
      try {
        const noteContent = await researchAgentApi.getNote(selectedValue);
        setCurrentNotes(noteContent);
        
        // Display the note content in chat messages - replace previous note if exists
        if (noteContent.trim()) {
          const noteMessageId = generateId();
          const noteMessage: ChatMessage = {
            id: noteMessageId,
            content: noteContent,
            role: 'ai',
            timestamp: new Date()
          };
          
          // If there's a previous note message, replace it
          if (currentNoteMessageId) {
            setChatMessages(prev => 
              prev.map(msg => 
                msg.id === currentNoteMessageId ? noteMessage : msg
              )
            );
          } else {
            // No previous note, add as new message
            addChatMessage(noteMessage);
          }
          
          // Track this note message ID for future replacements
          setCurrentNoteMessageId(noteMessageId);
        }
      } catch (error) {
        console.error('Failed to load note:', error);
      }
    }
  };

  // Handle delete notes
  const handleDeleteNote = async (noteName: string) => {
    if (confirm(`Are you sure you want to delete the note "${noteName}"? This action cannot be undone.`)) {
      try {
        await researchAgentApi.deleteNote(noteName);
        
        // If the deleted note was currently selected, reset to current session
        if (selectedNotesName === noteName) {
          setSelectedNotesName('current');
          setCurrentNotes('');
          
          // Also remove the note from chat if it's currently displayed
          if (currentNoteMessageId) {
            setChatMessages(prev => 
              prev.filter(msg => msg.id !== currentNoteMessageId)
            );
            setCurrentNoteMessageId(null);
          }
        }
        
        // Reload notes to update the list
        await loadNotesFromVault();
      } catch (error) {
        console.error('Failed to delete note:', error);
        alert('Failed to delete note. Please try again.');
      }
    }
  };

  const saveNotesToVault = async (fileName: string, content: string) => {
    try {
      // Save notes using the API with the user-provided filename
      await researchAgentApi.saveNotes({
        personal: content,
        research: selectedPaper?.summary || '',
        summary: `Notes for ${selectedPaper?.title || 'Research'}`,
        analysis: 'User generated notes'
      }, selectedPaper?.id, fileName);

      // Update local state with the filename
      setSavedNotes(prev => ({
        ...prev,
        [fileName]: content
      }));

      // Reload notes from vault to ensure consistency
      await loadNotesFromVault();

      // Remove notes save success message - user can see it in notes counter
      /*
      const systemMessage: ChatMessage = {
        id: generateId(),
        content: `✅ Notes "${fileName}" saved to vault successfully!`,
        role: 'system',
        timestamp: new Date()
      };
      addChatMessage(systemMessage);
      */

    } catch (error) {
      console.error('Failed to save notes to vault:', error);
    }
  };

  // Test connection on component mount
  useEffect(() => {
    const testConnection = async () => {
      try {
        const isConnected = await researchAgentApi.testConnection();
        setConnectionStatus(isConnected ? 'connected' : 'disconnected');
        
        if (isConnected) {
          // Connection successful - no need for system message
        } else {
          // Connection failed - silently handle
        }
      } catch (error) {
        setConnectionStatus('disconnected');
      }
    };

    testConnection();
  }, []);

  // Load notes after connection is established
  useEffect(() => {
    if (connectionStatus === 'connected') {
      loadNotesFromVault();
      initializeAiResponsesNotes();
    }
  }, [connectionStatus]);

  // Initialize AI Responses notes if they don't exist
  const initializeAiResponsesNotes = async () => {
    try {
      const existingAiNotes = await researchAgentApi.getNote('AI Responses');
      if (!existingAiNotes) {
        // Create initial AI Responses notes file
        const initialContent = `# AI Responses\n\nThis file automatically stores all AI responses from your research conversations.\n\n---\n\n`;
        await researchAgentApi.updateNote('AI Responses', initialContent);
        
        // Update local state
        setSavedNotes(prev => ({
          ...prev,
          'AI Responses': initialContent
        }));
        
        console.log('AI Responses notes initialized');
      }
    } catch (error) {
      console.error('Failed to initialize AI Responses notes:', error);
    }
  };

  // Auto-scroll chat to bottom when new messages are added
  useEffect(() => {
    const chatContainer = document.getElementById('chatMessages');
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  }, [chatMessages]);

  // Add a test message on component mount to show chat is working
  useEffect(() => {
    // Remove the chat activation message - not needed
    /*
    const timer = setTimeout(() => {
      if (chatMessages.length === 0) {
        const systemMessage: ChatMessage = {
          id: generateId(),
          content: 'Chat functionality is now active! Try typing a message below.',
          role: 'system',
          timestamp: new Date()
        };
        addChatMessage(systemMessage);
      }
    }, 2000);

    return () => clearTimeout(timer);
    */
  }, []);

  const renderPaperContent = () => {
    switch (activeView) {
      case 'abstract':
        return (
          <div className="abstract-view">
            {selectedPaper ? (
              <div className="paper-details">
                <div className="paper-header">
                  <h3>{selectedPaper.title}</h3>
                  <div className="paper-meta">
                    <p><strong>Authors:</strong> {selectedPaper.authors.join(', ')}</p>
                    <p><strong>Published:</strong> {selectedPaper.published}</p>
                    <p><strong>Categories:</strong> {selectedPaper.categories.join(', ')}</p>
                    <p><strong>arXiv ID:</strong> {selectedPaper.arxiv_id}</p>
                  </div>
                </div>
                <div className="paper-abstract">
                  <h4>Abstract</h4>
                  <p>{selectedPaper.summary}</p>
                </div>
              </div>
            ) : (
              <div className="empty-state">
                <i className="fas fa-file-pdf fa-3x"></i>
                <h3>No Paper Selected</h3>
                <p>Search for papers and select one from the dropdown to view its abstract here</p>
              </div>
            )}
          </div>
        );
      case 'pdf':
        return (
          <div className="pdf-view">
            <div className="pdf-viewer-container">
              {selectedPaper ? (
                <div className="pdf-content">
                  {(() => {
                    // Get PDF URL
                    let pdfUrl = selectedPaper.pdf_url;
                    if (!pdfUrl && selectedPaper.arxiv_id) {
                      const arxivId = selectedPaper.arxiv_id.replace('arXiv:', '');
                      pdfUrl = `https://arxiv.org/pdf/${arxivId}.pdf`;
                    }
                    
                    return pdfUrl ? (
                      <div className="pdf-embed-container">
                        <iframe
                          src={`${pdfUrl}#toolbar=1&navpanes=1&scrollbar=1`}
                          width="100%"
                          height="100%"
                          title={`PDF: ${selectedPaper.title}`}
                          frameBorder="0"
                          className="pdf-iframe"
                        />
                      </div>
                    ) : (
                      <div className="pdf-loading">
                        <i className="fas fa-exclamation-triangle fa-2x"></i>
                        <h3>PDF Not Available</h3>
                        <p>PDF URL is not available for this paper. Try using the abstract view.</p>
                      </div>
                    );
                  })()}
                </div>
              ) : (
                <div className="pdf-loading">
                  <i className="fas fa-file-pdf fa-2x"></i>
                  <h3>PDF Viewer</h3>
                  <p>Select a paper to view its PDF document here</p>
                </div>
              )}
            </div>
          </div>
        );
      default:
        return (
          <div className="empty-state">
            <i className="fas fa-file-pdf fa-3x"></i>
            <h3>No Paper Selected</h3>
            <p>Search for papers and select one from the dropdown to view it here</p>
          </div>
        );
    }
  };
  return (
    <div className="app-container">
      {/* Header with Search and Paper Selection */}
      <header className="app-header">
        <div className="header-content">
          <h1><i className="fas fa-microscope"></i> Research Agent</h1>
          <div className="search-controls">
            <div className="search-box">
              <input 
                type="text" 
                id="searchInput" 
                placeholder="Search academic papers..."
                autoComplete="off"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleSearch();
                  }
                }}
              />
              <button 
                id="searchBtn" 
                className="search-btn"
                onClick={handleSearch}
                disabled={isSearching || !searchQuery.trim()}
              >
                <i className="fas fa-search"></i>
                {isSearching ? ' Searching...' : ''}
              </button>
            </div>
            <div className="paper-selector">
              <select 
                id="paperDropdown" 
                className="paper-dropdown"
                value={selectedPaper?.id || ''}
                onChange={(e) => {
                  const paperId = e.target.value;
                  const paper = searchResults.find(p => p.id === paperId);
                  if (paper) {
                    handlePaperSelect(paper);
                  }
                }}
                disabled={searchResults.length === 0}
              >
                <option value="">
                  {searchResults.length === 0 ? 'Search for papers first...' : 'Select a paper...'}
                </option>
                {searchResults.map((paper) => (
                  <option key={paper.id} value={paper.id}>
                    {paper.title.length > 60 ? paper.title.substring(0, 60) + '...' : paper.title}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="main-content">
        <div className="panel-container" ref={containerRef}>
          {/* Left Panel: Paper Display */}
          <section 
            className="left-panel paper-panel"
            style={{ width: `${leftPanelWidth}%` }}
          >
            <div className="panel-header">
              <h2><i className="fas fa-file-pdf"></i> Paper Viewer</h2>
              <div className="paper-controls">
                <button 
                  id="openInNewTabBtn" 
                  className="control-btn"
                  disabled={!selectedPaper}
                  onClick={() => {
                    if (selectedPaper) {
                      // Construct PDF URL if not available
                      let pdfUrl = selectedPaper.pdf_url;
                      if (!pdfUrl && selectedPaper.arxiv_id) {
                        const arxivId = selectedPaper.arxiv_id.replace('arXiv:', '');
                        pdfUrl = `https://arxiv.org/pdf/${arxivId}.pdf`;
                      }
                      
                      if (pdfUrl) {
                        window.open(pdfUrl, '_blank');
                      } else {
                        const errorMessage: ChatMessage = {
                          id: generateId(),
                          content: 'PDF URL not available for this paper.',
                          role: 'system',
                          timestamp: new Date()
                        };
                        addChatMessage(errorMessage);
                      }
                    }
                  }}
                >
                  <i className="fas fa-external-link-alt"></i> Open in New Tab
                </button>
                <button 
                  id="summaryBtn" 
                  className="control-btn"
                  disabled={!selectedPaper}
                  onClick={async () => {
                    if (selectedPaper) {
                      try {
                        const summary = await researchAgentApi.generateSummary(selectedPaper.id);
                        const summaryMessage: ChatMessage = {
                          id: generateId(),
                          content: `Summary for "${selectedPaper.title}": ${summary}`,
                          role: 'ai',
                          timestamp: new Date()
                        };
                        addChatMessage(summaryMessage);
                      } catch (error) {
                        // Summary generation failed - silently ignore
                      }
                    }
                  }}
                >
                  <i className="fas fa-magic"></i> Generate Summary
                </button>
                <div className="view-toggle">
                  <button 
                    id="abstractViewBtn" 
                    className={`toggle-btn ${activeView === 'abstract' ? 'active' : ''}`}
                    onClick={() => handleViewChange('abstract')}
                  >
                    Abstract
                  </button>
                  <button 
                    id="pdfViewBtn" 
                    className={`toggle-btn ${activeView === 'pdf' ? 'active' : ''}`}
                    onClick={() => handleViewChange('pdf')}
                  >
                    PDF View
                  </button>
                </div>
              </div>
            </div>
            <div className="panel-content">
              <div id="paperViewer" className="paper-viewer">
                {renderPaperContent()}
              </div>
            </div>
          </section>

          {/* Resizable Divider */}
          <div 
            className="panel-divider" 
            id="panelDivider"
            onMouseDown={handleMouseDown}
            style={{ cursor: isResizing ? 'col-resize' : 'col-resize' }}
          ></div>

          {/* Right Panel: AI Agent & Notes */}
          <section 
            className="right-panel agent-panel"
            style={{ width: `${100 - leftPanelWidth}%` }}
          >
            <div className="panel-header">
              <h2>
                <i className="fas fa-robot"></i> AI Research Assistant
                {selectedNotesName !== 'current' && (
                  <span className="current-note-indicator"> - {selectedNotesName}</span>
                )}
              </h2>
              <div className="agent-controls">
                <div className="notes-selector">
                  <select 
                    id="notesDropdown" 
                    className="notes-dropdown"
                    value={selectedNotesName}
                    onChange={handleNotesDropdownChange}
                  >
                    <option value="current">Current Session</option>
                    <option value="clear">Clear Displayed Notes</option>
                    {Object.keys(savedNotes).map((noteName) => (
                      <option key={noteName} value={noteName}>
                        {noteName}
                      </option>
                    ))}
                  </select>
                  <div className="notes-info">
                    <span className="notes-count">
                      <i className="fas fa-sticky-note"></i> {Object.keys(savedNotes).length} saved
                    </span>
                    <button 
                      className="btn small secondary refresh-notes-btn" 
                      onClick={loadNotesFromVault}
                      title="Refresh notes from vault"
                    >
                      <i className="fas fa-sync-alt"></i>
                    </button>
                  </div>
                  <button id="newNotesBtn" className="control-btn" onClick={handleNotesModalOpen}>
                    <i className="fas fa-plus"></i> New Notes
                  </button>
                  <button 
                    id="editNotesBtn" 
                    className="control-btn" 
                    onClick={handleShowNotesListForEdit}
                    disabled={Object.keys(savedNotes).length === 0}
                    title={Object.keys(savedNotes).length === 0 ? 'No notes to edit' : 'Edit existing notes'}
                  >
                    <i className="fas fa-edit"></i> Edit Notes
                  </button>
                  <button id="saveNotesBtn" className="control-btn" onClick={() => {
                    if (currentNotes && selectedPaper) {
                      saveNotesToVault(`notes_${selectedPaper.id}_${Date.now()}`, currentNotes);
                    }
                  }}>
                    <i className="fas fa-save"></i> Save
                  </button>
                </div>
              </div>
            </div>
            <div className="panel-content">
              {/* Chat Interface */}
              <div className="chat-section">
                <div id="chatMessages" className="chat-messages">
                  {chatMessages.length === 0 ? (
                    <div className="welcome-message">
                      <div className="agent-avatar">
                        <i className="fas fa-robot"></i>
                      </div>
                      <div className="message-content">
                        <p><strong>Welcome to Research Agent!</strong></p>
                        <p>I'm here to help you research academic papers. Here's what I can do:</p>
                        <ul>
                          <li>🔍 Search for papers using keywords</li>
                          <li>📖 Analyze and explain paper content</li>
                          <li>📝 Generate summaries and key insights</li>
                          <li>💬 Answer questions about research papers</li>
                          <li>📄 View PDFs directly in the browser</li>
                          <li>✨ Provide formatted responses with markdown support</li>
                        </ul>
                        <p>Start by searching for papers above, then select one to begin our conversation!</p>
                        <div className="feature-highlight">
                          <strong>🧠 AI Features:</strong>
                          <ul>
                            <li>Context-aware conversations about selected papers</li>
                            <li>Rich markdown responses with code blocks, lists, and formatting</li>
                            <li>Direct PDF access and download capabilities</li>
                            <li>Real-time paper analysis and insights</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  ) : (
                    chatMessages.map((message) => (
                      <div key={message.id} className={`message ${message.role}`}>
                        <div className="message-header">
                          <span className="role-indicator">
                            {message.role === 'user' && <i className="fas fa-user"></i>}
                            {message.role === 'ai' && <i className="fas fa-robot"></i>}
                            {message.role === 'system' && <i className="fas fa-info-circle"></i>}
                            {message.role === 'user' ? 'You' : message.role === 'ai' ? 'AI Assistant' : 'System'}
                          </span>
                          <span className="timestamp">
                            {message.timestamp.toLocaleTimeString()}
                          </span>
                        </div>
                        <div className="message-content">
                          <ReactMarkdown 
                            remarkPlugins={[remarkGfm]}
                            rehypePlugins={[rehypeHighlight]}
                            components={{
                              code: ({className, children, ...props}: any) => {
                                const isInline = !className?.includes('language-');
                                return isInline ? (
                                  <code className="inline-code" {...props}>
                                    {children}
                                  </code>
                                ) : (
                                  <pre className="code-block">
                                    <code className={className} {...props}>
                                      {children}
                                    </code>
                                  </pre>
                                );
                              },
                              blockquote: ({children}) => (
                                <blockquote className="markdown-blockquote">
                                  {children}
                                </blockquote>
                              ),
                              h1: ({children}) => <h1 className="markdown-h1">{children}</h1>,
                              h2: ({children}) => <h2 className="markdown-h2">{children}</h2>,
                              h3: ({children}) => <h3 className="markdown-h3">{children}</h3>,
                              ul: ({children}) => <ul className="markdown-ul">{children}</ul>,
                              ol: ({children}) => <ol className="markdown-ol">{children}</ol>,
                              li: ({children}) => <li className="markdown-li">{children}</li>,
                              a: ({href, children}) => (
                                <a 
                                  href={href} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="markdown-link"
                                >
                                  {children}
                                </a>
                              )
                            }}
                          >
                            {message.content}
                          </ReactMarkdown>
                        </div>
                      </div>
                    ))
                  )}
                  {isSendingMessage && (
                    <div className="message ai">
                      <div className="message-header">
                        <span className="role-indicator">
                          <i className="fas fa-robot"></i>
                          AI Assistant
                        </span>
                      </div>
                      <div className="message-content">
                        <div className="typing-indicator">
                          <span></span>
                          <span></span>
                          <span></span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                <div className="chat-input-container">
                  <div className="chat-input">
                    <textarea 
                      id="chatInput" 
                      placeholder="Ask me about the paper, request explanations, or ask for specific notes..."
                      rows={1}
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyPress={handleKeyPress}
                      disabled={isSendingMessage}
                    />
                    <button 
                      id="sendChatBtn" 
                      className="send-btn"
                      onClick={handleSendMessage}
                      disabled={isSendingMessage || !chatInput.trim()}
                    >
                      <i className={isSendingMessage ? "fas fa-spinner fa-spin" : "fas fa-paper-plane"}></i>
                    </button>
                  </div>
                  
                </div>
              </div>
            </div>
          </section>
        </div>
      </main>

      {/* Status Bar */}
      <footer className="status-bar">
        <div className="status-left">
          <span id="connectionStatus" className="status-item">
            <i className={`fas fa-circle ${connectionStatus === 'connected' ? 'connected' : 'disconnected'}`}></i> 
            {connectionStatus === 'connected' ? 'API Connected' : 'API Disconnected'}
          </span>
          <span id="paperStatus" className="status-item">
            <i className="fas fa-file"></i> 
            {selectedPaper ? `Selected: ${selectedPaper.title.substring(0, 30)}...` : 'No paper selected'}
          </span>
        </div>
        <div className="status-right">
          <span id="searchStatus" className="status-item">
            <i className="fas fa-search"></i> 
            {searchResults.length > 0 ? `${searchResults.length} papers found` : 'No search results'}
          </span>
          <span id="chatStatus" className="status-item">
            <i className="fas fa-comments"></i> 
            {chatMessages.length} messages
          </span>
        </div>
      </footer>

      {/* Loading Overlay */}
      <div id="loadingOverlay" className="loading-overlay hidden">
        <div className="loading-content">
          <i className="fas fa-spinner fa-spin fa-2x"></i>
          <p id="loadingText">Loading...</p>
        </div>
      </div>

      {/* Notes Modal */}
      {showNotesModal && (
        <div className="modal">
          <div className="modal-content">
            <div className="modal-header">
              <h3><i className="fas fa-sticky-note"></i> Create New Notes File</h3>
              <button className="close-btn" onClick={() => setShowNotesModal(false)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <label htmlFor="notesName">Notes File Name:</label>
              <input 
                type="text" 
                id="notesName" 
                placeholder="Enter notes file name..."
                value={notesFileName}
                onChange={(e) => setNotesFileName(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleCreateNotes();
                  }
                }}
              />
              <div className="modal-actions">
                <button className="btn primary" onClick={handleCreateNotes}>Create</button>
                <button className="btn secondary" onClick={() => setShowNotesModal(false)}>Cancel</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Notes Modal */}
      {showEditNotesModal && (
        <div className="modal">
          <div className="modal-content edit-notes-modal">
            <div className="modal-header">
              <h3><i className="fas fa-edit"></i> Edit Notes: {editingNotesName}</h3>
              <button className="close-btn" onClick={() => setShowEditNotesModal(false)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <div className="notes-editor">
                <textarea 
                  className="notes-textarea"
                  placeholder="Edit your notes here..."
                  value={editingNotesContent}
                  onChange={(e) => setEditingNotesContent(e.target.value)}
                  rows={15}
                />
              </div>
              <div className="modal-actions">
                <button className="btn primary" onClick={handleSaveEditedNotes}>
                  <i className="fas fa-save"></i> Save Changes
                </button>
                <button className="btn secondary" onClick={() => setShowEditNotesModal(false)}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Notes List Modal */}
      {showNotesListModal && (
        <div className="modal">
          <div className="modal-content">
            <div className="modal-header">
              <h3><i className="fas fa-list"></i> Select Notes to Edit</h3>
              <button className="close-btn" onClick={() => setShowNotesListModal(false)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <div className="notes-list">
                {Object.keys(savedNotes).length === 0 ? (
                  <p className="no-notes-message">No saved notes found. Create some notes first!</p>
                ) : (
                  Object.keys(savedNotes).map((notesName) => (
                    <div key={notesName} className="notes-item">
                      <span className="notes-item-name">{notesName}</span>
                      <div className="notes-item-actions">
                        <button 
                          className="btn small primary" 
                          onClick={() => handleEditNotes(notesName)}
                        >
                          <i className="fas fa-edit"></i> Edit
                        </button>
                        <button 
                          className="btn small danger" 
                          onClick={() => handleDeleteNote(notesName)}
                        >
                          <i className="fas fa-trash"></i> Delete
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
              <div className="modal-actions">
                <button className="btn secondary" onClick={() => setShowNotesListModal(false)}>
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResearchAgentNew;
