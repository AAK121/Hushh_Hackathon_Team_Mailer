import React, { useState, useEffect, useRef, useCallback } from 'react';
import styled from 'styled-components';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css';
import { researchApi, ChatRequest } from '../services/researchApi';

interface ResearchAgentProps {
  onSendToHITL?: (message: string, context?: any) => void;
}

interface Paper {
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

interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'ai' | 'system';
  timestamp: Date;
  editable?: boolean;
  isWelcome?: boolean;
}

const ResearchAgent: React.FC<ResearchAgentProps> = () => {
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null);
  const [searchResults, setSearchResults] = useState<Paper[]>([]);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [currentView, setCurrentView] = useState<'abstract' | 'full' | 'pdf'>('abstract');
  const [searchQuery, setSearchQuery] = useState('');
  const [chatInput, setChatInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [loadingText, setLoadingText] = useState('Loading...');
  const [showAnalysisModal, setShowAnalysisModal] = useState(false);
  const [showSectionModal, setShowSectionModal] = useState(false);
  const [customSectionText, setCustomSectionText] = useState('');
  const [showCustomSection, setShowCustomSection] = useState(false);
  const [statusMessage, setStatusMessage] = useState('No paper selected');
  const [isNearBottom, setIsNearBottom] = useState(true);
  const [userHasScrolled, setUserHasScrolled] = useState(false);
  const [showNotesModal, setShowNotesModal] = useState(false);
  const [notes, setNotes] = useState<Array<{id: string, content: string, timestamp: Date, title: string}>>([]);
  const [noteTitle, setNoteTitle] = useState('');
  const [editingNoteId, setEditingNoteId] = useState<string | null>(null);
  const [editingNoteContent, setEditingNoteContent] = useState('');
  const [editingNoteTitle, setEditingNoteTitle] = useState('');
  const [showAddNoteForm, setShowAddNoteForm] = useState(false);
  const [newNoteContent, setNewNoteContent] = useState('');
  const [newNoteTitle, setNewNoteTitle] = useState('');
  const [discussedPapers, setDiscussedPapers] = useState<Set<string>>(new Set());
  const [shouldStopStreaming, setShouldStopStreaming] = useState(false);
  const [currentNote, setCurrentNote] = useState('');
  const [editingResponse, setEditingResponse] = useState(false);
  const [editableResponse, setEditableResponse] = useState('');
  
  const chatMessagesRef = useRef<HTMLDivElement>(null);
  const lastScrollTop = useRef<number>(0);
  const scrollTimeout = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    showWelcomeMessage();
    testBackendConnection();
    
    // Cleanup function
    return () => {
      if (scrollTimeout.current) {
        clearTimeout(scrollTimeout.current);
      }
    };
  }, []);

  useEffect(() => {
    // Only scroll when new messages are added AND not during streaming
    // During streaming, let the manual scroll logic handle it
    if (!isStreaming && chatMessages.length > 0 && chatMessagesRef.current) {
      // Add a small delay to ensure DOM is updated
      setTimeout(() => {
        if (chatMessagesRef.current) {
          chatMessagesRef.current.scrollTo({
            top: chatMessagesRef.current.scrollHeight,
            behavior: 'smooth'
          });
        }
      }, 100);
    }
  }, [chatMessages, isStreaming]);

  // Create default note when paper is selected
  useEffect(() => {
    if (selectedPaper && !notes.some(note => note.id === `default-${selectedPaper.id}`)) {
      const defaultNote = {
        id: `default-${selectedPaper.id}`,
        title: `First Note - ${selectedPaper.title}`,
        content: `# ${selectedPaper.title}\n\n**Authors:** ${selectedPaper.authors.join(', ')}\n\n**Published:** ${selectedPaper.published}\n\n**Abstract:**\n${selectedPaper.summary}\n\n## My Notes:\n\n*Add your research notes here...*`,
        timestamp: new Date()
      };
      setNotes(prev => [defaultNote, ...prev]);
    }
  }, [selectedPaper, notes]);

  // Function to smoothly scroll to bottom during streaming
  const scrollToBottom = useCallback((smooth: boolean = true) => {
    if (chatMessagesRef.current) {
      if (smooth) {
        chatMessagesRef.current.scrollTo({
          top: chatMessagesRef.current.scrollHeight,
          behavior: 'smooth'
        });
      } else {
        // Instant scroll without animation to avoid jarring user experience
        chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
      }
    }
  }, []);

  // Check if user is near the bottom of chat and track manual scrolling
  const handleScroll = useCallback(() => {
    // Throttle scroll events for better performance
    if (scrollTimeout.current) {
      clearTimeout(scrollTimeout.current);
    }
    
    scrollTimeout.current = setTimeout(() => {
      if (chatMessagesRef.current) {
        const { scrollTop, scrollHeight, clientHeight } = chatMessagesRef.current;
        const threshold = 30; // Very close to bottom (reduced further)
        const nearBottom = scrollTop + clientHeight >= scrollHeight - threshold;
        
        // Detect if user manually scrolled (vs auto-scroll) - extremely sensitive
        const userInitiatedScroll = Math.abs(scrollTop - lastScrollTop.current) > 1;
        if (userInitiatedScroll && isStreaming && !nearBottom) {
          setUserHasScrolled(true);
        }
        
        // Reset userHasScrolled if user scrolls back to bottom
        if (nearBottom && userHasScrolled) {
          setUserHasScrolled(false);
        }
        
        setIsNearBottom(nearBottom);
        lastScrollTop.current = scrollTop;
      }
    }, 16); // ~60fps throttling
  }, [isStreaming]);

  // Enhanced scrolling that respects user scroll position
  const conditionalScrollToBottom = useCallback((force: boolean = false) => {
    // Don't auto-scroll if user has manually scrolled during streaming
    if (force || (isNearBottom && !userHasScrolled)) {
      scrollToBottom(true);
    }
  }, [isNearBottom, userHasScrolled, scrollToBottom]);

  const testBackendConnection = async () => {
    try {
      const isConnected = await researchApi.testConnection();
      if (isConnected) {
        console.log('Backend connection: SUCCESS');
      } else {
        setStatusMessage('Backend server is not running');
      }
    } catch (error) {
      console.error('Backend connection failed:', error);
      setStatusMessage('Backend server is not running');
    }
  };

  const showWelcomeMessage = () => {
    const welcomeMessage: ChatMessage = {
      id: generateId(),
      content: `Welcome to Research Agent! 🔬

I can help you:
• Analyze and summarize research papers
• Answer questions about paper content
• Compare multiple papers in the same conversation
• Create and manage research notes

**Note:** Your chat history and notes persist when switching between papers, allowing you to maintain context across multiple research documents.`,
      role: 'system',
      timestamp: new Date(),
      isWelcome: true
    };
    setChatMessages([welcomeMessage]);
  };

  const generateId = () => {
    return Math.random().toString(36).substr(2, 9);
  };

  const performSearch = async () => {
    if (!searchQuery.trim()) {
      alert('Please enter a search query');
      return;
    }

    setIsLoading(true);
    setLoadingText('Searching for papers...');

    try {
      const data = await researchApi.searchPapers(searchQuery);
      setSearchResults(data.papers);
      setStatusMessage(`Found ${data.papers.length} papers`);
    } catch (error) {
      console.error('Search error:', error);
      alert('Failed to search papers. Please check your connection and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const selectPaper = async (paperIndex: number) => {
    if (paperIndex < 0 || paperIndex >= searchResults.length) return;
    
    const paper = searchResults[paperIndex];
    setSelectedPaper(paper);
    setCurrentView('abstract');
    setStatusMessage(`Selected: ${paper.title.substring(0, 50)}...`);
    
    // Track this paper as discussed
    setDiscussedPapers(prev => new Set([...prev, paper.id]));
    
    // Add selection message to existing chat history (don't clear previous messages)
    const isFirstPaper = discussedPapers.size === 0;
    const selectionMessage: ChatMessage = {
      id: generateId(),
      content: isFirstPaper 
        ? `**📄 Paper Selected:** "${paper.title}"  
*Ask me anything about this paper - analysis, summaries, questions, or comparisons!*`
        : `**📄 New Paper Added to Discussion:** "${paper.title}"  
*I now have access to ${discussedPapers.size + 1} papers in our conversation. You can ask me to compare papers, analyze differences, or discuss any of them.*`,
      role: 'system',
      timestamp: new Date()
    };
    setChatMessages(prev => [...prev, selectionMessage]);

    // Automatically load full content for chat agent access
    if (!paper.fullContent) {
      setIsLoading(true);
      setLoadingText('Loading paper content for analysis...');
      try {
        const contentData = await researchApi.getPaperContent(paper.id);
        setSelectedPaper(prev => prev ? { ...prev, fullContent: contentData } : null);
        
        // Add a system message to indicate full content is now available
        const contentLoadedMessage: ChatMessage = {
          id: generateId(),
          content: `✅ Full paper content loaded (${contentData.pages} pages, ${Math.round(contentData.content_length / 1000)}k characters). Chat agent now has complete access to the paper for detailed analysis.`,
          role: 'system',
          timestamp: new Date()
        };
        setChatMessages(prev => [...prev, contentLoadedMessage]);
        
      } catch (error) {
        console.error('Error loading paper content:', error);
        setStatusMessage('Failed to load full content - chat may be limited');
        
        // Add a system message about limited access
        const errorMessage: ChatMessage = {
          id: generateId(),
          content: `⚠️ Could not load full paper content. Chat agent has access to title, authors, abstract, and metadata only.`,
          role: 'system',
          timestamp: new Date()
        };
        setChatMessages(prev => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    } else {
      // Content already available
      const availableMessage: ChatMessage = {
        id: generateId(),
        content: `✅ Full paper content available. Chat agent has complete access for detailed analysis.`,
        role: 'system',
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, availableMessage]);
    }
  };

  const stopStreaming = () => {
    setShouldStopStreaming(true);
    setIsStreaming(false);
  };

  const sendChatMessage = async () => {
    if (!chatInput.trim() || !selectedPaper || isStreaming) return;

    const userMessage: ChatMessage = {
      id: generateId(),
      content: chatInput,
      role: 'user',
      timestamp: new Date()
    };

    setChatMessages(prev => [...prev, userMessage]);
    const messageContent = chatInput;
    setChatInput('');
    setIsStreaming(true);
    setShouldStopStreaming(false); // Reset stop flag
    setUserHasScrolled(false); // Reset scroll tracking for new stream

    // Add AI message placeholder for streaming
    const aiMessageId = generateId();
    const aiMessage: ChatMessage = {
      id: aiMessageId,
      content: '',
      role: 'ai',
      timestamp: new Date(),
      editable: true
    };
    
    setChatMessages(prev => [...prev, aiMessage]);

    try {
      const request: ChatRequest = {
        message: messageContent,
        paper_id: selectedPaper.id,
        user_id: 'demo_user',
        conversation_history: chatMessages.slice(-10).map(msg => ({
          role: msg.role,
          content: msg.content
        })),
        paper_content: selectedPaper.fullContent?.content || 
          `Paper Title: ${selectedPaper.title}
Authors: ${selectedPaper.authors.join(', ')}
Published: ${selectedPaper.published}
arXiv ID: ${selectedPaper.arxiv_id}
Categories: ${selectedPaper.categories.join(', ')}

Abstract:
${selectedPaper.summary}

Note: Full paper content is ${selectedPaper.fullContent ? 'available' : 'being loaded'}. Currently viewing in ${currentView} mode.`
      };

      const data = await researchApi.chatWithAI(request);
      
      // Simulate streaming response with character-by-character typing
      const fullResponse = data.response;
      const chars = fullResponse.split('');
      let currentContent = '';
      
      for (let i = 0; i < chars.length; i++) {
        // Check if streaming should stop
        if (shouldStopStreaming) {
          break;
        }
        
        currentContent += chars[i];
        
        setChatMessages(prev => 
          prev.map(msg => 
            msg.id === aiMessageId 
              ? { ...msg, content: currentContent }
              : msg
          )
        );
        
        // Only scroll if user is actively at the bottom and hasn't scrolled away
        // Even more restrictive - almost never auto-scroll during streaming
        if (i % 20 === 0 && !userHasScrolled) { // Very infrequent
          setTimeout(() => {
            if (chatMessagesRef.current && !userHasScrolled) {
              const { scrollTop, scrollHeight, clientHeight } = chatMessagesRef.current;
              const distanceFromBottom = scrollHeight - (scrollTop + clientHeight);
              // Only auto-scroll if user is exactly at bottom (0px tolerance)
              if (distanceFromBottom <= 5) {
                chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
              }
            }
          }, 0);
        }
        
        // Variable delay based on character type for more natural feel
        let delay = 20; // Base delay
        if (chars[i] === ' ') delay = 40; // Pause at spaces
        else if (chars[i] === '.' || chars[i] === '!' || chars[i] === '?') delay = 150; // Pause at sentence endings
        else if (chars[i] === ',' || chars[i] === ';') delay = 80; // Pause at commas
        else if (chars[i] === '\n') delay = 100; // Pause at line breaks
        
        await new Promise(resolve => setTimeout(resolve, delay));
      }

      // Final scroll to ensure we're at the bottom when streaming completes
      setTimeout(() => scrollToBottom(true), 100);

      // Add the complete response to current note
      setCurrentNote(prev => {
        const baseNote = prev ? prev + '\n\n' : '';
        return baseNote + `**AI Response:** ${fullResponse}`;
      });

    } catch (error) {
      console.error('Chat error:', error);
      setChatMessages(prev => 
        prev.map(msg => 
          msg.id === aiMessageId 
            ? { ...msg, content: 'Sorry, I encountered an error while processing your message. Please try again.' }
            : msg
        )
      );
    } finally {
      setIsStreaming(false);
    }
  };

  const switchView = async (view: 'abstract' | 'full' | 'pdf') => {
    setCurrentView(view);
    
    if ((view === 'full' || view === 'pdf') && selectedPaper && !selectedPaper.fullContent) {
      const success = await loadPaperContent();
      
      // Add system message when content is loaded for chat access
      if (success) {
        const contentMessage: ChatMessage = {
          id: generateId(),
          content: `✅ Full paper content now available for chat analysis while viewing in ${view} mode.`,
          role: 'system',
          timestamp: new Date()
        };
        setChatMessages(prev => [...prev, contentMessage]);
      }
    }
  };

  const loadPaperContent = async (): Promise<boolean> => {
    if (!selectedPaper) return false;

    setIsLoading(true);
    setLoadingText('Loading full paper content...');

    try {
      const contentData = await researchApi.getPaperContent(selectedPaper.id);
      setSelectedPaper(prev => prev ? { ...prev, fullContent: contentData } : null);
      return true;
    } catch (error) {
      console.error('Error loading paper content:', error);
      alert('Failed to load full content');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalysisSelection = (analysisType: string) => {
    setShowAnalysisModal(false);
    
    const prompts = {
      comprehensive: `Please provide a comprehensive analysis of this paper using the following structured format:

## Main Problem & Motivation
- What problem does this paper aim to solve?
- Why is this problem important in the field?

## Core Contribution
- What is the key innovation or contribution of the paper?

## Methodology
- Describe the approach in simple terms
- What makes this method different from previous ones

## Experiments & Results
- Key findings and statistical results

## Significance & Applications
- Why do these results matter?
- Real-world applications or future research opportunities

## Limitations & Open Questions
- Challenges or weaknesses acknowledged by authors

## Critical Evaluation
- Strengths and weaknesses
- Overall importance in its research domain`,
      
      section: '',
      notes: `Please create comprehensive study notes for this paper in a structured format suitable for students and researchers.`,
      compare: `Please provide a critical evaluation of this paper analyzing strengths, weaknesses, significance, and technical assessment.`
    };

    if (analysisType === 'section') {
      setShowSectionModal(true);
    } else {
      const prompt = prompts[analysisType as keyof typeof prompts];
      if (prompt) {
        setChatInput(prompt);
        // Auto-send the message with streaming
        setTimeout(() => sendChatMessage(), 100);
      }
    }
  };

  const handleSectionSelection = (sectionType: string) => {
    if (sectionType === 'custom') {
      setShowCustomSection(true);
      return;
    }
    
    setShowSectionModal(false);
    
    const sectionPrompts = {
      abstract: "Please analyze the abstract of this paper. Explain what the authors claim to have achieved, the key methodology, and the main results.",
      introduction: "Analyze the introduction section. What background context do the authors provide? How do they motivate the problem?",
      methodology: "Provide a detailed analysis of the methodology section. Explain the approach in simple terms and what makes it novel.",
      results: "Analyze the results section. What are the key findings? How do they compare to baselines?",
      discussion: "Examine the discussion section. How do the authors interpret their results? What implications do they draw?",
      conclusion: "Analyze the conclusion. What are the main takeaways? What future work do they suggest?"
    };
    
    const prompt = sectionPrompts[sectionType as keyof typeof sectionPrompts];
    if (prompt) {
      setChatInput(prompt);
      setTimeout(() => sendChatMessage(), 100);
    }
  };

  const analyzeCustomSection = () => {
    if (!customSectionText.trim()) {
      alert('Please enter some text to analyze');
      return;
    }
    
    setShowSectionModal(false);
    setShowCustomSection(false);
    
    const prompt = `Please analyze the following text section from the paper:\n\n"${customSectionText}"\n\nProvide insights about its significance, methodology, findings, or relevance.`;
    setChatInput(prompt);
    setCustomSectionText('');
    setTimeout(() => sendChatMessage(), 100);
  };

  // Enhanced Notes functionality
  const addToNotes = (content: string, customTitle?: string) => {
    const newNote = {
      id: Date.now().toString(),
      content: content,
      timestamp: new Date(),
      title: customTitle || `Note from ${new Date().toLocaleString()}`
    };
    setNotes(prev => [...prev, newNote]);
  };

  const createNewNote = () => {
    if (newNoteTitle.trim() && newNoteContent.trim()) {
      const newNote = {
        id: Date.now().toString(),
        content: newNoteContent,
        timestamp: new Date(),
        title: newNoteTitle
      };
      setNotes(prev => [...prev, newNote]);
      setNewNoteTitle('');
      setNewNoteContent('');
      setShowAddNoteForm(false);
    }
  };

  const startEditingNote = (note: {id: string, content: string, title: string}) => {
    setEditingNoteId(note.id);
    setEditingNoteContent(note.content);
    setEditingNoteTitle(note.title);
  };

  const saveEditedNote = () => {
    if (editingNoteId && editingNoteTitle.trim() && editingNoteContent.trim()) {
      setNotes(prev => prev.map(note => 
        note.id === editingNoteId 
          ? { ...note, title: editingNoteTitle, content: editingNoteContent }
          : note
      ));
      setEditingNoteId(null);
      setEditingNoteContent('');
      setEditingNoteTitle('');
    }
  };

  const cancelEditingNote = () => {
    setEditingNoteId(null);
    setEditingNoteContent('');
    setEditingNoteTitle('');
  };

  const deleteNote = (noteId: string) => {
    setNotes(prev => prev.filter(note => note.id !== noteId));
  };

  const startEditingResponse = (response: string) => {
    setEditableResponse(response);
    setEditingResponse(true);
  };

  const saveEditedResponse = () => {
    if (editableResponse.trim()) {
      setCurrentNote(prev => prev + '\n\n' + editableResponse);
      setEditingResponse(false);
      setEditableResponse('');
    }
  };

  const cancelEditingResponse = () => {
    setEditingResponse(false);
    setEditableResponse('');
  };

  const addCurrentNoteToCollection = () => {
    if (currentNote.trim() && selectedPaper) {
      const newNote = {
        id: Date.now().toString(),
        title: `Notes for ${selectedPaper.title}`,
        content: currentNote,
        timestamp: new Date()
      };
      setNotes(prev => [...prev, newNote]);
      setCurrentNote('');
    }
  };

  const clearCurrentNote = () => {
    setCurrentNote('');
  };

  const MarkdownContent: React.FC<{ content: string; className?: string }> = ({ content, className }) => {
    return (
      <div className={className}>
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeHighlight]}
          components={{
            // Custom components for better styling
            h1: ({ children }) => <h1 className="markdown-h1">{children}</h1>,
            h2: ({ children }) => <h2 className="markdown-h2">{children}</h2>,
            h3: ({ children }) => <h3 className="markdown-h3">{children}</h3>,
            h4: ({ children }) => <h4 className="markdown-h4">{children}</h4>,
            h5: ({ children }) => <h5 className="markdown-h5">{children}</h5>,
            h6: ({ children }) => <h6 className="markdown-h6">{children}</h6>,
            p: ({ children }) => <p className="markdown-p">{children}</p>,
            ul: ({ children }) => <ul className="markdown-ul">{children}</ul>,
            ol: ({ children }) => <ol className="markdown-ol">{children}</ol>,
            li: ({ children }) => <li className="markdown-li">{children}</li>,
            blockquote: ({ children }) => <blockquote className="markdown-blockquote">{children}</blockquote>,
            code: ({ children, className }) => 
              className ? (
                <code className={`markdown-code-block ${className}`}>{children}</code>
              ) : (
                <code className="markdown-code-inline">{children}</code>
              ),
            pre: ({ children }) => <pre className="markdown-pre">{children}</pre>,
            table: ({ children }) => <table className="markdown-table">{children}</table>,
            thead: ({ children }) => <thead className="markdown-thead">{children}</thead>,
            tbody: ({ children }) => <tbody className="markdown-tbody">{children}</tbody>,
            tr: ({ children }) => <tr className="markdown-tr">{children}</tr>,
            th: ({ children }) => <th className="markdown-th">{children}</th>,
            td: ({ children }) => <td className="markdown-td">{children}</td>,
            a: ({ href, children }) => (
              <a href={href} className="markdown-link" target="_blank" rel="noopener noreferrer">
                {children}
              </a>
            ),
            strong: ({ children }) => <strong className="markdown-strong">{children}</strong>,
            em: ({ children }) => <em className="markdown-em">{children}</em>,
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    );
  };

  const renderPaperContent = () => {
    if (!selectedPaper) {
      return (
        <div className="empty-state">
          <i className="fas fa-file-pdf fa-3x"></i>
          <h3>No Paper Selected</h3>
          <p>Search for papers and select one from the dropdown to view it here</p>
        </div>
      );
    }

    if (currentView === 'abstract') {
      return (
        <div className="paper-details">
          <div className="paper-header">
            <h3>{selectedPaper.title}</h3>
            <div className="paper-authors">{selectedPaper.authors.join(', ')}</div>
            <div className="paper-meta">
              <span>Published: {selectedPaper.published}</span>
              <span>arXiv: {selectedPaper.arxiv_id}</span>
              <span>{selectedPaper.categories.join(', ')}</span>
            </div>
          </div>
          <div className="paper-abstract">
            <h4>Abstract</h4>
            <MarkdownContent 
              content={selectedPaper.summary} 
              className="paper-markdown-content"
            />
          </div>
        </div>
      );
    }

    if (currentView === 'full' && selectedPaper.fullContent) {
      return (
        <div className="paper-details">
          <div className="paper-header">
            <h3>{selectedPaper.title}</h3>
            <div className="paper-authors">{selectedPaper.authors.join(', ')}</div>
            <div className="paper-meta">
              <span>Published: {selectedPaper.published}</span>
              <span>arXiv: {selectedPaper.arxiv_id}</span>
              <span>{selectedPaper.categories.join(', ')}</span>
              <span>{selectedPaper.fullContent.pages} pages</span>
            </div>
          </div>
          <div className="paper-full-content">
            <h4>Full Paper Content</h4>
            <div className="content-text">
              <MarkdownContent 
                content={selectedPaper.fullContent.content.substring(0, 50000)} 
                className="paper-markdown-content full-content"
              />
              {selectedPaper.fullContent.content.length > 50000 && (
                <div className="truncation-notice">Content truncated for display...</div>
              )}
            </div>
          </div>
        </div>
      );
    }

    if (currentView === 'pdf') {
      return (
        <div className="pdf-viewer">
          <div className="pdf-container">
            <iframe 
              src={selectedPaper.pdf_url + '#view=FitH'} 
              title="PDF Viewer"
              className="pdf-iframe"
            />
            <div className="pdf-fallback">
              <p>If the PDF doesn't load, <a href={selectedPaper.pdf_url} target="_blank" rel="noopener noreferrer">click here to open it in a new tab</a>.</p>
            </div>
          </div>
        </div>
      );
    }

    return null;
  };

  return (
    <StyledWrapper>
      
      <div className="app-container">
        {/* Header */}
        <header className="app-header">
          <div className="header-content">
            <div className="search-controls">
              <div className="search-box">
                <input 
                  type="text" 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search academic papers..."
                  onKeyPress={(e) => e.key === 'Enter' && performSearch()}
                />
                <button onClick={performSearch} className="search-btn">
                  <i className="fas fa-search"></i>
                </button>
              </div>
              <div className="paper-selector">
                <select 
                  onChange={(e) => {
                    const index = parseInt(e.target.value);
                    if (!isNaN(index)) {
                      selectPaper(index);
                    }
                  }}
                  disabled={searchResults.length === 0}
                  value={selectedPaper ? searchResults.findIndex(p => p.id === selectedPaper.id) : ''}
                >
                  <option value="">Select a paper...</option>
                  {searchResults.map((paper, index) => (
                    <option key={paper.id} value={index}>
                      {paper.title.substring(0, 80)}...
                    </option>
                  ))}
                </select>
                <button 
                  onClick={() => setShowAnalysisModal(true)}
                  disabled={!selectedPaper}
                  className="analyze-btn"
                >
                  <i className="fas fa-brain"></i> Analyze Paper
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="main-content">
          <div className="panel-container">
            {/* Left Panel: Paper Display */}
            <section className="left-panel">
              <div className="panel-header">
                <div className="paper-controls">
                  <div className="view-toggle">
                    <button 
                      className={`toggle-btn ${currentView === 'abstract' ? 'active' : ''}`}
                      onClick={() => switchView('abstract')}
                      disabled={!selectedPaper}
                    >
                      Abstract
                    </button>
                    <button 
                      className={`toggle-btn ${currentView === 'full' ? 'active' : ''}`}
                      onClick={() => switchView('full')}
                      disabled={!selectedPaper}
                    >
                      Full Text
                    </button>
                    <button 
                      className={`toggle-btn ${currentView === 'pdf' ? 'active' : ''}`}
                      onClick={() => switchView('pdf')}
                      disabled={!selectedPaper}
                    >
                      PDF View
                    </button>
                  </div>
                </div>
              </div>
              <div className="panel-content">
                <div className="paper-viewer">
                  {renderPaperContent()}
                </div>
              </div>
            </section>

            {/* Right Panel: AI Agent & Chat */}
            <section className="right-panel">
              <div className="panel-header">
                <h2>
                  <i className="fas fa-robot"></i> AI Research Assistant
                  {isStreaming && (
                    <span className="streaming-indicator">
                      <i className="fas fa-circle streaming-dot"></i>
                      <span>Responding...</span>
                    </span>
                  )}
                </h2>
                <div className="agent-controls">
                  <button 
                    onClick={() => setShowAnalysisModal(true)}
                    disabled={!selectedPaper}
                    className="control-btn analysis-menu-btn"
                  >
                    <i className="fas fa-brain"></i> Analysis Menu
                  </button>
                  <button 
                    onClick={() => setShowNotesModal(true)}
                    className="control-btn notes-btn"
                  >
                    <i className="fas fa-sticky-note"></i> Notes
                  </button>
                </div>
              </div>
              <div className="panel-content">
                <div className="chat-section">
                  <div className="chat-messages" ref={chatMessagesRef} onScroll={handleScroll}>
                    {chatMessages.length === 0 ? (
                      <div className="welcome-message">
                        <i className="fas fa-robot"></i>
                        <h2><span>Hello, Researcher</span></h2>
                        <p>How can I help you with academic paper analysis today?</p>
                      </div>
                    ) : (
                      chatMessages.map((message) => (
                        <div key={message.id} className={`chat-message ${message.role}`}>
                          {message.role === 'ai' && (
                            <div className="message-header">
                              <div className="ai-avatar">
                                <i className="fas fa-robot"></i>
                              </div>
                            </div>
                          )}
                          {message.role === 'user' && (
                            <div className="message-header">
                              <div className="user-avatar">U</div>
                            </div>
                          )}
                          <div className="message-content">
                            <MarkdownContent 
                              content={message.content} 
                              className="markdown-message"
                            />
                            {isStreaming && message.role === 'ai' && message.content && (
                              <span className="typing-cursor">|</span>
                            )}
                          </div>
                          {message.role === 'ai' && !isStreaming && (
                            <div className="message-actions">
                              <button 
                                onClick={() => startEditingResponse(message.content)}
                                className="edit-response-btn"
                                title="Edit Response"
                              >
                                <i className="fas fa-pen"></i> Edit
                              </button>
                              <button 
                                onClick={() => addToNotes(message.content)}
                                className="add-to-notes-btn"
                                title="Add to Notes"
                              >
                                <i className="fas fa-plus"></i> Add to Notes
                              </button>
                            </div>
                          )}
                          <div className="message-time">
                            {message.timestamp.toLocaleTimeString()}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                  
                  {/* Scroll to bottom button - shown when user scrolls up during streaming */}
                  {isStreaming && (userHasScrolled || !isNearBottom) && (
                    <div className="scroll-to-bottom">
                      <button 
                        onClick={() => {
                          setUserHasScrolled(false);
                          conditionalScrollToBottom(true);
                        }} 
                        className="scroll-btn"
                        title="Scroll to bottom to see latest AI response"
                      >
                        <i className="fas fa-chevron-down"></i>
                        <span>New message</span>
                      </button>
                    </div>
                  )}
                  
                  <div className="chat-input-container">
                    <div className="chat-input">
                      <textarea 
                        value={chatInput}
                        onChange={(e) => setChatInput(e.target.value)}
                        placeholder={isStreaming ? "AI is responding..." : "Ask me about the paper, request explanations, or ask for specific notes..."}
                        disabled={isStreaming}
                        rows={1}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey && !isStreaming) {
                            e.preventDefault();
                            sendChatMessage();
                          }
                        }}
                      />
                      {isStreaming ? (
                        <button onClick={stopStreaming} className="stop-btn" title="Stop Generation">
                          <i className="fas fa-stop"></i>
                        </button>
                      ) : (
                        <button onClick={sendChatMessage} className="send-btn" disabled={isStreaming}>
                          <i className={`fas ${isStreaming ? 'fa-spinner fa-spin' : 'fa-paper-plane'}`}></i>
                        </button>
                      )}
                    </div>
                    <p className="chat-bottom-info">
                      {selectedPaper ? (
                        selectedPaper.fullContent ? 
                        `✅ AI has full access to "${selectedPaper.title.substring(0, 40)}..." (${selectedPaper.fullContent.pages} pages)` :
                        `⚠️ AI has limited access (title, abstract, metadata only) - Switch to Full Text or PDF view to load complete content`
                      ) : (
                        "Select a paper to enable AI chat analysis"
                      )}
                      <br />
                      Research Agent may display inaccurate info about papers, so double-check its responses.
                    </p>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </main>

        {/* Status Bar */}
        <footer className="status-bar">
          <div className="status-left">
            <span className="status-item">
              <i className="fas fa-circle connected"></i> Connected
            </span>
            <span className="status-item">
              <i className="fas fa-file"></i> {statusMessage}
            </span>
          </div>
          <div className="status-right">
            <span className="status-item">
              <i className="fas fa-sticky-note"></i> {chatMessages.filter(m => m.role === 'ai').length} notes
            </span>
            <span className="status-item">
              <i className="fas fa-font"></i> {chatMessages.reduce((sum, msg) => sum + msg.content.split(' ').length, 0)} words
            </span>
          </div>
        </footer>
      </div>

      {/* Loading Overlay */}
      {isLoading && (
        <div className="loading-overlay">
          <div className="loading-content">
            <i className="fas fa-spinner fa-spin fa-2x"></i>
            <p>{loadingText}</p>
          </div>
        </div>
      )}

      {/* Analysis Menu Modal */}
      {showAnalysisModal && (
        <div className="modal">
          <div className="modal-content analysis-modal">
            <div className="modal-header">
              <h3><i className="fas fa-brain"></i> Paper Analysis Menu</h3>
              <button onClick={() => setShowAnalysisModal(false)} className="close-btn">
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <div className="analysis-grid">
                <button 
                  className="analysis-card" 
                  onClick={() => handleAnalysisSelection('comprehensive')}
                >
                  <div className="analysis-icon">
                    <i className="fas fa-microscope"></i>
                  </div>
                  <h4>Comprehensive Analysis</h4>
                  <p>Complete structured analysis covering all aspects of the paper</p>
                </button>
                
                <button 
                  className="analysis-card" 
                  onClick={() => handleAnalysisSelection('section')}
                >
                  <div className="analysis-icon">
                    <i className="fas fa-search"></i>
                  </div>
                  <h4>Section Analysis</h4>
                  <p>Select and analyze specific sections of the paper</p>
                </button>
                
                <button 
                  className="analysis-card" 
                  onClick={() => handleAnalysisSelection('notes')}
                >
                  <div className="analysis-icon">
                    <i className="fas fa-edit"></i>
                  </div>
                  <h4>Smart Note Taking</h4>
                  <p>Generate structured notes and summaries</p>
                </button>
                
                <button 
                  className="analysis-card" 
                  onClick={() => handleAnalysisSelection('compare')}
                >
                  <div className="analysis-icon">
                    <i className="fas fa-balance-scale"></i>
                  </div>
                  <h4>Critical Evaluation</h4>
                  <p>Analyze strengths, weaknesses, and significance</p>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Section Selector Modal */}
      {showSectionModal && (
        <div className="modal">
          <div className="modal-content section-modal">
            <div className="modal-header">
              <h3><i className="fas fa-list"></i> Select Paper Section</h3>
              <button onClick={() => setShowSectionModal(false)} className="close-btn">
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <p>Choose a section of the paper to analyze in detail:</p>
              <div className="section-list">
                {[
                  { id: 'abstract', icon: 'fas fa-file-text', label: 'Abstract' },
                  { id: 'introduction', icon: 'fas fa-play', label: 'Introduction' },
                  { id: 'methodology', icon: 'fas fa-cogs', label: 'Methodology' },
                  { id: 'results', icon: 'fas fa-chart-bar', label: 'Results' },
                  { id: 'discussion', icon: 'fas fa-comments', label: 'Discussion' },
                  { id: 'conclusion', icon: 'fas fa-flag-checkered', label: 'Conclusion' },
                  { id: 'custom', icon: 'fas fa-pencil-alt', label: 'Custom Selection' }
                ].map((section) => (
                  <button 
                    key={section.id}
                    className="section-item" 
                    onClick={() => handleSectionSelection(section.id)}
                  >
                    <i className={section.icon}></i>
                    <span>{section.label}</span>
                  </button>
                ))}
              </div>
              {showCustomSection && (
                <div className="custom-section-input">
                  <label htmlFor="customSectionText">Paste or type the section text:</label>
                  <textarea 
                    id="customSectionText" 
                    value={customSectionText}
                    onChange={(e) => setCustomSectionText(e.target.value)}
                    placeholder="Paste the text you want to analyze..." 
                    rows={6}
                  />
                  <button onClick={analyzeCustomSection} className="btn primary">
                    Analyze Custom Text
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Notes Modal */}
      {showNotesModal && (
        <div className="modal">
          <div className="modal-content notes-modal">
            <div className="modal-header">
              <div className="modal-header-content">
                <h3><i className="fas fa-sticky-note"></i> Research Notes Collection</h3>
                <p className="storage-info">
                  <i className="fas fa-info-circle"></i> 
                  Notes are stored locally in your browser. Export important notes to save permanently.
                </p>
              </div>
              <div className="modal-header-actions">
                <button 
                  onClick={() => setShowAddNoteForm(!showAddNoteForm)}
                  className="add-note-btn"
                  title="Add New Note"
                >
                  <i className="fas fa-plus"></i> Add Note
                </button>
                <button onClick={() => setShowNotesModal(false)} className="close-btn">
                  <i className="fas fa-times"></i>
                </button>
              </div>
            </div>
            <div className="modal-body">
              {/* Current Note Section */}
              {currentNote && (
                <div className="current-note-section">
                  <div className="current-note-header">
                    <h4><i className="fas fa-edit"></i> Current Note (Auto-Generated)</h4>
                    <div className="current-note-actions">
                      <button 
                        onClick={addCurrentNoteToCollection}
                        className="save-current-note-btn"
                        title="Add to Notes Collection"
                      >
                        <i className="fas fa-save"></i> Save to Collection
                      </button>
                      <button 
                        onClick={clearCurrentNote}
                        className="clear-current-note-btn"
                        title="Clear Current Note"
                      >
                        <i className="fas fa-trash"></i> Clear
                      </button>
                    </div>
                  </div>
                  <div className="current-note-content">
                    <MarkdownContent 
                      content={currentNote} 
                      className="current-note-markdown"
                    />
                  </div>
                </div>
              )}

              {/* Add New Note Form */}
              {showAddNoteForm && (
                <div className="add-note-form">
                  <h4><i className="fas fa-edit"></i> Create New Note</h4>
                  <input
                    type="text"
                    placeholder="Note title..."
                    value={newNoteTitle}
                    onChange={(e) => setNewNoteTitle(e.target.value)}
                    className="note-title-input"
                  />
                  <textarea
                    placeholder="Write your note content here... (Markdown supported)"
                    value={newNoteContent}
                    onChange={(e) => setNewNoteContent(e.target.value)}
                    className="note-content-input"
                    rows={6}
                  />
                  <div className="form-actions">
                    <button 
                      onClick={createNewNote}
                      className="save-note-btn"
                      disabled={!newNoteTitle.trim() || !newNoteContent.trim()}
                    >
                      <i className="fas fa-save"></i> Save Note
                    </button>
                    <button 
                      onClick={() => {
                        setShowAddNoteForm(false);
                        setNewNoteTitle('');
                        setNewNoteContent('');
                      }}
                      className="cancel-note-btn"
                    >
                      <i className="fas fa-times"></i> Cancel
                    </button>
                  </div>
                </div>
              )}

              <div className="notes-container">
                {notes.length === 0 ? (
                  <div className="empty-notes">
                    <i className="fas fa-sticky-note"></i>
                    <p>No notes yet. Select a paper to get started with a default note, or create your own notes.</p>
                  </div>
                ) : (
                  <div className="notes-list">
                    <div className="notes-header">
                      <h4><i className="fas fa-folder-open"></i> Notes Collection ({notes.length} notes)</h4>
                    </div>
                    {notes.map((note) => (
                      <div key={note.id} className="note-item">
                        <div className="note-header">
                          <div className="note-title">
                            <i className="fas fa-note-sticky"></i>
                            {editingNoteId === note.id ? (
                              <input
                                type="text"
                                value={editingNoteTitle}
                                onChange={(e) => setEditingNoteTitle(e.target.value)}
                                className="edit-title-input"
                              />
                            ) : (
                              <span>{note.title}</span>
                            )}
                          </div>
                          <div className="note-actions">
                            <span className="note-date">
                              {note.timestamp.toLocaleDateString()} {note.timestamp.toLocaleTimeString()}
                            </span>
                            {editingNoteId === note.id ? (
                              <>
                                <button 
                                  onClick={saveEditedNote}
                                  className="save-edit-btn"
                                  title="Save Changes"
                                  disabled={!editingNoteTitle.trim() || !editingNoteContent.trim()}
                                >
                                  <i className="fas fa-check"></i>
                                </button>
                                <button 
                                  onClick={cancelEditingNote}
                                  className="cancel-edit-btn"
                                  title="Cancel Editing"
                                >
                                  <i className="fas fa-times"></i>
                                </button>
                              </>
                            ) : (
                              <>
                                <button 
                                  onClick={() => startEditingNote(note)}
                                  className="edit-note-btn"
                                  title="Edit Note"
                                >
                                  <i className="fas fa-edit"></i>
                                </button>
                                <button 
                                  onClick={() => deleteNote(note.id)}
                                  className="delete-note-btn"
                                  title="Delete Note"
                                >
                                  <i className="fas fa-trash"></i>
                                </button>
                              </>
                            )}
                          </div>
                        </div>
                        <div className="note-content">
                          {editingNoteId === note.id ? (
                            <textarea
                              value={editingNoteContent}
                              onChange={(e) => setEditingNoteContent(e.target.value)}
                              className="edit-content-textarea"
                              rows={8}
                            />
                          ) : (
                            <MarkdownContent 
                              content={note.content} 
                              className="note-markdown"
                            />
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Response Editing Modal */}
      {editingResponse && (
        <div className="modal">
          <div className="modal-content response-edit-modal">
            <div className="modal-header">
              <h3><i className="fas fa-pen"></i> Edit AI Response</h3>
              <button onClick={cancelEditingResponse} className="close-btn">
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <div className="response-edit-form">
                <div className="response-title-section">
                  <label htmlFor="response-title">Note Title:</label>
                  <input
                    id="response-title"
                    type="text"
                    value={editableResponse.split('\n')[0] || 'AI Response Note'}
                    onChange={(e) => {
                      const lines = editableResponse.split('\n');
                      lines[0] = e.target.value;
                      setEditableResponse(lines.join('\n'));
                    }}
                    className="response-title-input"
                    placeholder="Enter note title..."
                  />
                </div>
                <div className="response-content-section">
                  <label htmlFor="response-content">Note Content:</label>
                  <textarea
                    id="response-content"
                    value={editableResponse}
                    onChange={(e) => setEditableResponse(e.target.value)}
                    className="response-edit-textarea"
                    rows={16}
                    placeholder="Edit the AI response before adding to your notes..."
                  />
                </div>
              </div>
              <div className="edit-response-actions">
                <button 
                  onClick={saveEditedResponse}
                  className="save-response-btn"
                  disabled={!editableResponse.trim()}
                >
                  <i className="fas fa-save"></i> Add to Current Note
                </button>
                <button 
                  onClick={cancelEditingResponse}
                  className="cancel-response-btn"
                >
                  <i className="fas fa-times"></i> Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </StyledWrapper>
  );
};

const StyledWrapper = styled.div`
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
  @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
  
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  font-family: 'Outfit', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: #f8f9fa;
  color: #333;

  .app-container {
    display: flex;
    flex-direction: column;
    height: calc(100vh - 110px); /* Adjust height to account for increased top margin */
    background: white;
    margin: 15vh 10px 10px 10px; /* Increased top margin further for better clearance */
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  }

  /* Page Title Styles */
  .page-title {
    background: transparent;
    padding: 16px 20px;
    position: fixed;
    top: 32px; /* Align with menu button position (2rem = 32px) */
    left: 50%;
    transform: translateX(-50%); /* Center horizontally */
    z-index: 1000;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .page-title h2 {
    color: #2c3e50;
    font-size: 1.3rem;
    font-weight: 600;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .page-title i {
    color: #3498db;
  }

  /* Header Styles */
  .app-header {
    background: linear-gradient(135deg, #2c3e50, #34495e);
    color: white;
    padding: 8px 16px;
    border-bottom: 2px solid #3498db;
  }

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    flex-wrap: wrap;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .header-content h1 {
    font-size: 1.2rem;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .search-controls {
    display: flex;
    gap: 15px;
    align-items: center;
    flex-wrap: wrap;
  }

  .search-box {
    display: flex;
    gap: 10px;
    min-width: 300px;
  }

  .search-box input {
    flex: 1;
    padding: 10px 14px;
    border: none;
    border-radius: 6px;
    font-size: 0.95rem;
    background: rgba(255, 255, 255, 0.1);
    color: white;
    backdrop-filter: blur(10px);
  }

  .search-box input::placeholder {
    color: rgba(255, 255, 255, 0.7);
  }

  .search-box input:focus {
    outline: none;
    background: rgba(255, 255, 255, 0.2);
    box-shadow: 0 0 0 2px #3498db;
  }

  .search-btn, .analyze-btn {
    padding: 10px 16px;
    background: #3498db;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.95rem;
    transition: all 0.3s ease;
  }

  .search-btn:hover {
    background: #2980b9;
    transform: translateY(-2px);
  }

  .paper-selector {
    display: flex;
    gap: 10px;
    align-items: center;
  }

  .paper-selector select {
    min-width: 300px;
    padding: 10px 14px;
    border: none;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.1);
    color: white;
    font-size: 0.95rem;
    backdrop-filter: blur(10px);
  }

  .paper-selector select:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .paper-selector select option {
    background: #2c3e50;
    color: white;
  }

  .analyze-btn {
    background: #e74c3c;
    white-space: nowrap;
  }

  .analyze-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .analyze-btn:hover:not(:disabled) {
    background: #c0392b;
    transform: translateY(-2px);
  }

  /* Main Content */
  .main-content {
    display: flex;
    flex: 1;
    overflow: hidden;
  }

  .panel-container {
    display: flex;
    width: 100%;
    height: 100%;
  }

  /* Panel Styles */
  .left-panel, .right-panel {
    display: flex;
    flex-direction: column;
    background: white;
    overflow: hidden;
  }

  .left-panel {
    flex: 0 0 55%;
    border-right: 1px solid #ecf0f1;
  }

  .right-panel {
    flex: 0 0 45%;
  }

  .panel-header {
    padding: 12px 16px;
    background: #f8f9fa;
    border-bottom: 1px solid #dee2e6;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    min-height: 48px;
    margin-top: 0; /* Removed margin since app-container now handles menu clearance */
  }

  .panel-header h2 {
    color: #2c3e50;
    font-size: 1.1rem;
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
  }

  .streaming-indicator {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-left: 12px;
    font-size: 0.8rem;
    color: #4b90ff;
    font-weight: 400;
    animation: fadeIn 0.3s ease-in;
  }

  .streaming-dot {
    font-size: 0.5rem;
    color: #4b90ff;
    animation: pulse 1.5s infinite;
  }

  @keyframes pulse {
    0%, 100% {
      opacity: 0.4;
      transform: scale(1);
    }
    50% {
      opacity: 1;
      transform: scale(1.2);
    }
  }

  .paper-controls, .agent-controls {
    display: flex;
    gap: 10px;
    align-items: center;
    flex-wrap: wrap;
  }

  .control-btn {
    padding: 8px 16px;
    background: #3498db;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 5px;
  }

  .control-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .control-btn:hover:not(:disabled) {
    background: #2980b9;
    transform: translateY(-1px);
  }

  .view-toggle {
    display: flex;
    background: #ecf0f1;
    border-radius: 6px;
    overflow: hidden;
  }

  .toggle-btn {
    padding: 8px 16px;
    background: transparent;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 0.9rem;
  }

  .toggle-btn.active {
    background: #3498db;
    color: white;
  }

  .toggle-btn:hover:not(.active):not(:disabled) {
    background: #bdc3c7;
  }

  .toggle-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .analysis-menu-btn {
    background: linear-gradient(135deg, #4b90ff, #ff5546) !important;
    color: white !important;
  }

  .analysis-menu-btn:hover:not(:disabled) {
    background: linear-gradient(135deg, #ff5546, #4b90ff) !important;
    transform: translateY(-1px);
  }

  /* Panel Content */
  .panel-content {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  /* Paper Viewer */
  .paper-viewer {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #7f8c8d;
    text-align: center;
  }

  .empty-state i {
    margin-bottom: 20px;
    color: #bdc3c7;
  }

  .empty-state h3 {
    margin-bottom: 10px;
    font-size: 1.5rem;
  }

  .paper-details {
    max-height: 100%;
    overflow-y: auto;
  }

  .paper-header {
    margin-bottom: 30px;
    padding: 30px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    border-left: 4px solid #667eea;
  }

  .paper-header h3 {
    font-size: 1.8rem;
    color: #1a202c;
    margin-bottom: 20px;
    line-height: 1.3;
    font-weight: 600;
    text-align: center;
    font-family: 'Times New Roman', serif;
  }

  .paper-authors {
    font-size: 1.1rem;
    color: #4a5568;
    margin-bottom: 20px;
    text-align: center;
    font-style: italic;
    font-family: 'Times New Roman', serif;
  }

  .paper-meta {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 20px;
    font-size: 0.9rem;
    color: #718096;
    padding: 15px;
    background: #f7fafc;
    border-radius: 6px;
    font-family: 'Times New Roman', serif;
  }

  .paper-meta span {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 8px;
    background: white;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
  }

  .paper-abstract {
    margin: 30px 0;
    padding: 25px;
    background: #f8faff;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
  }

  .paper-abstract h4 {
    color: #2d3748;
    margin-bottom: 15px;
    font-size: 1.2rem;
    font-weight: 600;
    text-align: center;
    font-family: 'Times New Roman', serif;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .paper-abstract p {
    line-height: 1.7;
    color: #2d3748;
    text-align: justify;
    font-family: 'Times New Roman', serif;
    font-size: 1rem;
    text-indent: 20px;
  }

  .paper-full-content {
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    margin-top: 30px;
  }

  .paper-full-content h4 {
    padding: 12px 20px;
    background: #667eea;
    color: white;
    font-family: 'Times New Roman', serif;
    font-weight: 600;
    font-size: 1rem;
    margin: 0;
  }

  .content-text {
    overflow-y: auto;
    padding: 30px;
    background: white;
  }

  .content-text pre {
    white-space: pre-wrap;
    word-wrap: break-word;
    font-family: 'Times New Roman', serif;
    line-height: 1.8;
    color: #2d3748;
    font-size: 1rem;
    text-align: justify;
    margin: 0;
    background: none;
    border: none;
    padding: 0;
  }

  .truncation-notice {
    padding: 15px 25px;
    background: #fff5f5;
    color: #e53e3e;
    border-top: 1px solid #fed7d7;
    font-style: italic;
    text-align: center;
  }

  .pdf-viewer {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .pdf-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    position: relative;
  }

  .pdf-iframe {
    flex: 1;
    width: 100%;
    border: none;
    background: white;
  }

  .pdf-fallback {
    padding: 20px;
    text-align: center;
    background: #f0f9ff;
    border: 1px solid #bfdbfe;
    border-radius: 8px;
    margin: 20px;
  }

  .pdf-fallback a {
    color: #667eea;
    text-decoration: none;
    font-weight: 600;
  }

  .pdf-fallback a:hover {
    text-decoration: underline;
  }

  /* Chat Interface */
  .chat-section {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: #ffffff;
    position: relative;
  }

  .chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    background: linear-gradient(to bottom, #ffffff 0%, #fafbfc 100%);
    line-height: 1.6;
    max-height: 70vh;
    scroll-behavior: smooth;
  }

  .chat-messages::-webkit-scrollbar {
    width: 8px;
  }

  .chat-messages::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
  }

  .chat-messages::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 4px;
    transition: background 0.3s ease;
  }

  .chat-messages::-webkit-scrollbar-thumb:hover {
    background: #a1a1a1;
  }

  /* Welcome Message */
  .welcome-message {
    text-align: center;
    padding: 40px 20px;
    margin-bottom: 30px;
  }

  .welcome-message i {
    font-size: 3rem;
    background: linear-gradient(135deg, #4b90ff, #ff5546);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 20px;
    display: block;
  }

  .welcome-message h2 {
    font-size: 3rem;
    color: #c4c7c5;
    font-weight: 500;
    margin-bottom: 10px;
  }

  .welcome-message h2 span {
    background: linear-gradient(135deg, #4b90ff, #ff5546);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .welcome-message p {
    font-size: 1.1rem;
    color: #585858;
    font-weight: 300;
  }

  /* Chat Messages */
  .chat-message {
    margin-bottom: 30px;
    max-width: 100%;
    word-wrap: break-word;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .chat-message.user {
    align-items: flex-end;
  }

  .chat-message.ai {
    align-items: flex-start;
  }

  .chat-message.system {
    align-items: center;
    margin: 15px 0;
  }

  .chat-message .message-header {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 10px;
  }

  .chat-message.user .message-header {
    justify-content: flex-end;
  }

  .user-avatar, .ai-avatar {
    width: 35px;
    height: 35px;
    border-radius: 50%;
    background: linear-gradient(135deg, #4b90ff, #ff5546);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
    flex-shrink: 0;
  }

  .user-avatar {
    order: 2;
  }

  .ai-avatar {
    font-size: 18px;
  }

  .chat-message .message-content {
    background: transparent;
    color: #282828;
    border: none;
    padding: 0;
    font-size: 17px;
    line-height: 1.8;
    font-weight: 300;
    max-width: 100%;
    margin-bottom: 20px;
  }

  .chat-message.user .message-content {
    color: #585858;
    font-size: 1rem;
    max-width: 85%;
    text-align: right;
  }

  .chat-message.system .message-content {
    background: #f0f4f9;
    border: 1px solid #e2e8f0;
    border-radius: 25px;
    padding: 8px 16px;
    font-size: 0.9rem;
    max-width: 70%;
    color: #718096;
    font-style: italic;
    font-weight: 300;
  }

  .message-content strong {
    font-weight: 600;
    color: #282828;
  }

  .message-content em {
    font-style: italic;
  }

  .message-content code {
    background: #f0f4f9;
    padding: 3px 6px;
    border-radius: 4px;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.9em;
    color: #d63384;
  }

  .typing-cursor {
    color: #4b90ff;
    animation: blink 1s infinite;
    font-weight: bold;
  }

  @keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
  }

  .message-time {
    font-size: 0.75rem;
    opacity: 0.6;
    margin-top: 8px;
    color: #6b7280;
    font-weight: 300;
  }

  /* Scroll to bottom button */
  .scroll-to-bottom {
    position: absolute;
    bottom: 120px;
    right: 20px;
    z-index: 100;
    animation: slideUp 0.3s ease-out;
  }

  .scroll-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 16px;
    background: linear-gradient(135deg, #4b90ff, #3182ce);
    color: white;
    border: none;
    border-radius: 25px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    box-shadow: 0 4px 12px rgba(75, 144, 255, 0.3);
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
  }

  .scroll-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(75, 144, 255, 0.4);
    background: linear-gradient(135deg, #3182ce, #2c5aa0);
  }

  .scroll-btn i {
    font-size: 0.8rem;
    animation: bounce 1s infinite;
  }

  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes bounce {
    0%, 20%, 50%, 80%, 100% {
      transform: translateY(0);
    }
    40% {
      transform: translateY(-3px);
    }
    60% {
      transform: translateY(-1px);
    }
  }

  .chat-input-container {
    position: relative;
    background: white;
    border-top: none;
    padding: 20px;
    box-shadow: 0 -20px 50px rgba(255, 255, 255, 0.9);
  }

  .chat-input {
    display: flex;
    align-items: flex-end;
    gap: 15px;
    background: #f0f4f9;
    padding: 12px 20px;
    border-radius: 50px;
    border: 1px solid #e5e7eb;
    transition: all 0.3s ease;
  }

  .chat-input:focus-within {
    border-color: #4b90ff;
    box-shadow: 0 0 0 3px rgba(75, 144, 255, 0.1);
  }

  .chat-input textarea {
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    padding: 12px 8px;
    font-size: 16px;
    font-family: 'Outfit', sans-serif;
    font-weight: 400;
    resize: none;
    color: #282828;
    line-height: 1.4;
    min-height: 20px;
  }

  .chat-input textarea:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .chat-input textarea::placeholder {
    color: #9ca3af;
    font-weight: 300;
  }

  .send-btn {
    padding: 12px;
    background: none;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    flex-shrink: 0;
  }

  .send-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .send-btn:hover:not(:disabled) {
    background: #e8eaed;
  }

  .send-btn i {
    color: #4b90ff;
    font-size: 18px;
  }

  .stop-btn {
    padding: 12px;
    background: #ff5547;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    flex-shrink: 0;
    box-shadow: 0 2px 4px rgba(255, 85, 71, 0.3);
  }

  .stop-btn:hover {
    background: #e74c3c;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(255, 85, 71, 0.4);
  }

  .stop-btn i {
    color: white;
    font-size: 14px;
  }

  .chat-bottom-info {
    font-size: 13px;
    margin: 15px auto 0;
    text-align: center;
    font-weight: 300;
    color: #6b7280;
    max-width: 600px;
    line-height: 1.4;
  }

  /* Status Bar */
  .status-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 20px;
    background: #2c3e50;
    color: white;
    font-size: 0.9rem;
  }

  .status-left, .status-right {
    display: flex;
    gap: 20px;
  }

  .status-item {
    display: flex;
    align-items: center;
    gap: 5px;
  }

  .status-item i.connected {
    color: #27ae60;
  }

  /* Loading Overlay */
  .loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(4px);
  }

  .loading-content {
    background: white;
    padding: 40px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  }

  .loading-content i {
    color: #3498db;
    margin-bottom: 20px;
  }

  .loading-content p {
    color: #333;
    font-size: 1.1rem;
  }

  /* Modal Styles */
  .modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1001;
  }

  .modal-content {
    background: white;
    border-radius: 12px;
    min-width: 400px;
    max-width: 800px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  }

  .modal-content.analysis-modal,
  .modal-content.section-modal {
    min-width: 600px;
    max-width: 800px;
  }

  .modal-header {
    padding: 20px;
    border-bottom: 1px solid #dee2e6;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }

  .modal-header h3 {
    color: #2c3e50;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .close-btn {
    background: none;
    border: none;
    font-size: 1.2rem;
    cursor: pointer;
    color: #7f8c8d;
    padding: 5px;
    border-radius: 4px;
  }

  .close-btn:hover {
    background: #ecf0f1;
    color: #e74c3c;
  }

  .modal-body {
    padding: 20px;
  }

  /* Analysis Grid */
  .analysis-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
    margin-top: 20px;
  }

  .analysis-card {
    padding: 20px;
    background: #f8f9fa;
    border: 2px solid #e9ecef;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    text-align: center;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .analysis-card:hover {
    border-color: #4b90ff;
    background: #f0f8ff;
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(75, 144, 255, 0.15);
  }

  .analysis-icon {
    font-size: 2rem;
    color: #4b90ff;
    margin-bottom: 10px;
  }

  .analysis-card h4 {
    color: #2c3e50;
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
  }

  .analysis-card p {
    color: #6c757d;
    margin: 0;
    font-size: 0.9rem;
    line-height: 1.4;
  }

  /* Section List */
  .section-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 15px;
  }

  .section-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 15px;
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    text-align: left;
    font-size: 1rem;
  }

  .section-item:hover {
    background: #e3f2fd;
    border-color: #4b90ff;
    transform: translateX(5px);
  }

  .section-item i {
    color: #4b90ff;
    width: 20px;
    text-align: center;
  }

  .section-item span {
    color: #2c3e50;
    font-weight: 500;
  }

  /* Custom Section Input */
  .custom-section-input {
    margin-top: 20px;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
    border: 1px solid #e9ecef;
  }

  .custom-section-input label {
    display: block;
    margin-bottom: 10px;
    color: #2c3e50;
    font-weight: 500;
  }

  .custom-section-input textarea {
    width: 100%;
    padding: 12px;
    border: 2px solid #e9ecef;
    border-radius: 6px;
    font-size: 0.95rem;
    font-family: inherit;
    resize: vertical;
    margin-bottom: 15px;
  }

  .custom-section-input textarea:focus {
    outline: none;
    border-color: #4b90ff;
    box-shadow: 0 0 0 3px rgba(75, 144, 255, 0.1);
  }

  .btn {
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 1rem;
    transition: all 0.3s ease;
  }

  .btn.primary {
    background: linear-gradient(135deg, #4b90ff, #ff5546);
    color: white;
  }

  .btn.primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(75, 144, 255, 0.3);
  }

  /* Notes Modal Styles */
  .modal-content.notes-modal {
    min-width: 700px;
    max-width: 950px;
    max-height: 85vh;
  }

  .modal-header-actions {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .modal-header-content {
    flex: 1;
  }

  .storage-info {
    margin: 8px 0 0 0;
    font-size: 0.8rem;
    color: #7f8c8d;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .storage-info i {
    color: #3498db;
  }

  .add-note-btn {
    background: #27ae60;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.3s ease;
  }

  .add-note-btn:hover {
    background: #229954;
    transform: translateY(-1px);
  }

  .add-note-form {
    background: #f8f9fa;
    border: 2px solid #27ae60;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
  }

  .add-note-form h4 {
    color: #27ae60;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .note-title-input, .note-content-input {
    width: 100%;
    padding: 12px;
    border: 2px solid #e9ecef;
    border-radius: 6px;
    font-size: 0.95rem;
    font-family: inherit;
    margin-bottom: 15px;
  }

  .note-title-input:focus, .note-content-input:focus {
    outline: none;
    border-color: #27ae60;
    box-shadow: 0 0 0 2px rgba(39, 174, 96, 0.2);
  }

  .note-content-input {
    resize: vertical;
    font-family: 'JetBrains Mono', 'Courier New', monospace;
  }

  .form-actions {
    display: flex;
    gap: 10px;
  }

  .save-note-btn {
    background: #27ae60;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 16px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.3s ease;
  }

  .save-note-btn:hover:not(:disabled) {
    background: #229954;
    transform: translateY(-1px);
  }

  .save-note-btn:disabled {
    background: #bdc3c7;
    cursor: not-allowed;
  }

  .cancel-note-btn {
    background: #95a5a6;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 16px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.3s ease;
  }

  .cancel-note-btn:hover {
    background: #7f8c8d;
  }

  .notes-container {
    max-height: 65vh;
    overflow-y: auto;
    padding-right: 5px;
  }

  .notes-header {
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid #e9ecef;
  }

  .notes-header h4 {
    color: #2c3e50;
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 0;
  }

  .empty-notes {
    text-align: center;
    padding: 40px 20px;
    color: #7f8c8d;
  }

  .empty-notes i {
    font-size: 3rem;
    margin-bottom: 15px;
    color: #bdc3c7;
  }

  .notes-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }

  .note-item {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    padding: 15px;
    transition: all 0.3s ease;
  }

  .note-item:hover {
    border-color: #3498db;
    box-shadow: 0 2px 8px rgba(52, 152, 219, 0.1);
  }

  .note-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    flex-wrap: wrap;
    gap: 10px;
  }

  .note-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    color: #2c3e50;
    flex: 1;
  }

  .note-title i {
    color: #f39c12;
  }

  .edit-title-input {
    flex: 1;
    padding: 8px;
    border: 2px solid #3498db;
    border-radius: 4px;
    font-size: 0.95rem;
    font-weight: 600;
  }

  .edit-title-input:focus {
    outline: none;
    border-color: #2980b9;
  }

  .note-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }

  .note-date {
    font-size: 0.85rem;
    color: #7f8c8d;
  }

  .edit-note-btn, .delete-note-btn, .save-edit-btn, .cancel-edit-btn {
    background: none;
    border: none;
    cursor: pointer;
    padding: 6px 8px;
    border-radius: 4px;
    font-size: 0.9rem;
    transition: all 0.3s ease;
  }

  .edit-note-btn {
    color: #3498db;
  }

  .edit-note-btn:hover {
    background: #ebf3fd;
    color: #2980b9;
  }

  .delete-note-btn {
    color: #e74c3c;
  }

  .delete-note-btn:hover {
    background: #ffebee;
    color: #c0392b;
  }

  .save-edit-btn {
    color: #27ae60;
  }

  .save-edit-btn:hover:not(:disabled) {
    background: #eafaf1;
    color: #229954;
  }

  .save-edit-btn:disabled {
    color: #bdc3c7;
    cursor: not-allowed;
  }

  .cancel-edit-btn {
    color: #95a5a6;
  }

  .cancel-edit-btn:hover {
    background: #f4f6f7;
    color: #7f8c8d;
  }

  .note-content {
    background: white;
    border-radius: 6px;
    padding: 15px;
  }

  .edit-content-textarea {
    width: 100%;
    padding: 12px;
    border: 2px solid #3498db;
    border-radius: 6px;
    font-size: 0.9rem;
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    resize: vertical;
    background: white;
  }

  .edit-content-textarea:focus {
    outline: none;
    border-color: #2980b9;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
  }

  .note-markdown {
    font-size: 0.9rem;
  }

  /* Message Actions */
  .message-actions {
    margin-top: 10px;
    padding: 8px 0;
  }

  .add-to-notes-btn {
    background: #f39c12;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .add-to-notes-btn:hover {
    background: #e67e22;
    transform: translateY(-1px);
  }

  .notes-btn {
    background: #f39c12;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 16px;
    cursor: pointer;
    font-size: 0.95rem;
    transition: all 0.3s ease;
    margin-left: 10px;
  }

  .notes-btn:hover {
    background: #e67e22;
    transform: translateY(-2px);
  }

  /* Markdown Styles */
  .markdown-message {
    width: 100%;
  }

  .markdown-h1 {
    font-size: 1.8rem;
    font-weight: 700;
    color: #1a202c;
    margin: 1.5rem 0 1rem 0;
    line-height: 1.2;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 0.5rem;
  }

  .markdown-h2 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #2d3748;
    margin: 1.25rem 0 0.75rem 0;
    line-height: 1.3;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 0.3rem;
  }

  .markdown-h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #2d3748;
    margin: 1rem 0 0.5rem 0;
    line-height: 1.3;
  }

  .markdown-h4 {
    font-size: 1.1rem;
    font-weight: 600;
    color: #4a5568;
    margin: 0.875rem 0 0.5rem 0;
    line-height: 1.3;
  }

  .markdown-h5 {
    font-size: 1rem;
    font-weight: 600;
    color: #4a5568;
    margin: 0.75rem 0 0.5rem 0;
    line-height: 1.3;
  }

  .markdown-h6 {
    font-size: 0.9rem;
    font-weight: 600;
    color: #718096;
    margin: 0.75rem 0 0.5rem 0;
    line-height: 1.3;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .markdown-p {
    margin: 0.75rem 0;
    line-height: 1.6;
    color: #2d3748;
  }

  .markdown-ul, .markdown-ol {
    margin: 0.75rem 0;
    padding-left: 1.5rem;
    line-height: 1.6;
  }

  .markdown-li {
    margin: 0.25rem 0;
    color: #2d3748;
  }

  .markdown-ul .markdown-li {
    list-style-type: disc;
  }

  .markdown-ol .markdown-li {
    list-style-type: decimal;
  }

  .markdown-blockquote {
    margin: 1rem 0;
    padding: 0.75rem 1rem;
    border-left: 4px solid #4b90ff;
    background: #f7fafc;
    border-radius: 0 4px 4px 0;
    font-style: italic;
    color: #4a5568;
  }

  .markdown-blockquote .markdown-p {
    margin: 0.5rem 0;
  }

  .markdown-code-inline {
    background: #f1f5f9;
    color: #e53e3e;
    padding: 0.125rem 0.375rem;
    border-radius: 0.25rem;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.875em;
    border: 1px solid #e2e8f0;
  }

  .markdown-pre {
    background: #1a202c;
    color: #e2e8f0;
    padding: 1rem;
    border-radius: 0.5rem;
    overflow-x: auto;
    margin: 1rem 0;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.875rem;
    line-height: 1.5;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .markdown-code-block {
    background: transparent;
    color: inherit;
    padding: 0;
    border-radius: 0;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.875rem;
  }

  .markdown-table {
    border-collapse: collapse;
    width: 100%;
    margin: 1rem 0;
    border: 1px solid #e2e8f0;
    border-radius: 0.5rem;
    overflow: hidden;
  }

  .markdown-thead {
    background: #f7fafc;
  }

  .markdown-th {
    padding: 0.75rem;
    text-align: left;
    font-weight: 600;
    color: #2d3748;
    border-bottom: 2px solid #e2e8f0;
    border-right: 1px solid #e2e8f0;
  }

  .markdown-th:last-child {
    border-right: none;
  }

  .markdown-td {
    padding: 0.75rem;
    color: #4a5568;
    border-bottom: 1px solid #e2e8f0;
    border-right: 1px solid #e2e8f0;
  }

  .markdown-td:last-child {
    border-right: none;
  }

  .markdown-tr:last-child .markdown-td {
    border-bottom: none;
  }

  .markdown-link {
    color: #4b90ff;
    text-decoration: none;
    border-bottom: 1px solid transparent;
    transition: all 0.2s ease;
  }

  .markdown-link:hover {
    color: #3182ce;
    border-bottom-color: #3182ce;
  }

  .markdown-strong {
    font-weight: 700;
    color: #1a202c;
  }

  .markdown-em {
    font-style: italic;
    color: #4a5568;
  }

  /* Code syntax highlighting */
  .markdown-pre .hljs {
    background: transparent;
    color: inherit;
  }

  .hljs-keyword,
  .hljs-selector-tag,
  .hljs-literal,
  .hljs-doctag,
  .hljs-title,
  .hljs-section,
  .hljs-type,
  .hljs-name,
  .hljs-strong {
    color: #f687b3;
  }

  .hljs-comment,
  .hljs-quote {
    color: #a0aec0;
    font-style: italic;
  }

  .hljs-string,
  .hljs-attribute,
  .hljs-symbol,
  .hljs-bullet,
  .hljs-addition {
    color: #68d391;
  }

  .hljs-number,
  .hljs-regexp,
  .hljs-link {
    color: #90cdf4;
  }

  .hljs-built_in,
  .hljs-builtin-name {
    color: #fbb6ce;
  }

  .hljs-variable,
  .hljs-template-variable,
  .hljs-attr {
    color: #fbd38d;
  }

  .hljs-function,
  .hljs-class .hljs-title {
    color: #a78bfa;
  }

  .hljs-tag {
    color: #f687b3;
  }

  .hljs-deletion {
    color: #feb2b2;
  }

  .hljs-emphasis {
    font-style: italic;
  }

  /* Paper Content Markdown Styles */
  .paper-markdown-content {
    font-family: 'Times New Roman', serif;
  }

  .paper-markdown-content .markdown-p {
    text-align: justify;
    text-indent: 20px;
    margin: 0.5rem 0;
    line-height: 1.7;
  }

  .paper-markdown-content .markdown-h1,
  .paper-markdown-content .markdown-h2,
  .paper-markdown-content .markdown-h3,
  .paper-markdown-content .markdown-h4,
  .paper-markdown-content .markdown-h5,
  .paper-markdown-content .markdown-h6 {
    font-family: 'Times New Roman', serif;
    text-align: center;
    margin: 1.5rem 0 1rem 0;
  }

  .paper-markdown-content.full-content {
    max-height: 70vh;
    overflow-y: auto;
    background: white;
    border-radius: 8px;
    padding: 20px;
  }

  .paper-markdown-content .markdown-blockquote {
    background: #f8faff;
    border-left: 4px solid #667eea;
    font-family: 'Times New Roman', serif;
    font-style: italic;
    margin: 1rem 0;
    padding: 1rem;
  }

  .paper-markdown-content .markdown-code-inline {
    background: #f1f5f9;
    font-family: 'Times New Roman', serif;
    font-size: 0.95em;
  }

  .paper-markdown-content .markdown-pre {
    font-family: 'Times New Roman', serif;
    background: #f8f9fa;
    color: #2d3748;
    border: 1px solid #e2e8f0;
  }

  .paper-markdown-content .markdown-table {
    font-family: 'Times New Roman', serif;
    margin: 1.5rem auto;
    max-width: 100%;
  }

  .paper-markdown-content .markdown-ul,
  .paper-markdown-content .markdown-ol {
    text-align: left;
    margin: 1rem 0;
    padding-left: 2rem;
  }

  .paper-markdown-content .markdown-li {
    text-align: justify;
    margin: 0.5rem 0;
    line-height: 1.6;
  }

  /* Responsive Design */
  @media (max-width: 768px) {
    .app-container {
      margin: 100px 5px 5px 5px; /* Maintain increased top margin for menu on mobile */
      height: calc(100vh - 110px); /* Adjust height for mobile too */
    }

    .page-title {
      top: 32px; /* Keep same alignment on mobile */
      padding: 12px 16px; /* Slightly smaller padding on mobile */
    }

    .page-title h2 {
      font-size: 1.1rem; /* Slightly smaller font on mobile */
    }
    
    .header-content {
      flex-direction: column;
      gap: 15px;
    }
    
    .search-box {
      min-width: unset;
      width: 100%;
    }
    
    .paper-selector {
      width: 100%;
      justify-content: space-between;
    }
    
    .panel-container {
      flex-direction: column;
    }
    
    .left-panel, .right-panel {
      flex: none;
      height: 50vh;
    }
    
    .panel-header {
      padding: 15px;
    }
    
    .analysis-grid {
      grid-template-columns: 1fr;
    }
  }

  /* Animations */
  .fade-in {
    animation: fadeIn 0.3s ease-in-out;
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .fa-spin {
    animation: spin 1s linear infinite;
  }

  /* Current Note Section */
  .current-note-section {
    margin-bottom: 24px;
    padding: 16px;
    background: #f8faff;
    border: 1px solid #e1e8ff;
    border-radius: 8px;
  }

  .current-note-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    flex-wrap: wrap;
    gap: 8px;
  }

  .current-note-header h4 {
    color: #2c3e50;
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.95rem;
  }

  .current-note-actions {
    display: flex;
    gap: 8px;
  }

  .save-current-note-btn, .clear-current-note-btn {
    padding: 6px 12px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85rem;
    transition: all 0.3s ease;
  }

  .save-current-note-btn {
    background: #27ae60;
    color: white;
  }

  .save-current-note-btn:hover {
    background: #229954;
  }

  .clear-current-note-btn {
    background: #e74c3c;
    color: white;
  }

  .clear-current-note-btn:hover {
    background: #c0392b;
  }

  .current-note-content {
    max-height: 300px;
    overflow-y: auto;
    padding: 12px;
    background: white;
    border-radius: 4px;
    border: 1px solid #dee2e6;
  }

  .current-note-markdown {
    font-size: 0.9rem;
    line-height: 1.5;
  }

  /* Response Editing Modal */
  .response-edit-modal {
    max-width: 90vw;
    max-height: 90vh;
    width: 900px;
  }

  .response-edit-form {
    display: flex;
    flex-direction: column;
    gap: 16px;
    margin-bottom: 20px;
  }

  .response-title-section, .response-content-section {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .response-title-section label, .response-content-section label {
    font-weight: 600;
    color: #2c3e50;
    font-size: 0.9rem;
  }

  .response-title-input {
    padding: 10px 12px;
    border: 2px solid #3498db;
    border-radius: 6px;
    font-size: 1rem;
    background: white;
  }

  .response-title-input:focus {
    outline: none;
    border-color: #2980b9;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
  }

  .response-edit-textarea {
    width: 100%;
    padding: 12px;
    border: 2px solid #3498db;
    border-radius: 6px;
    font-size: 0.9rem;
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    resize: vertical;
    background: white;
    min-height: 400px;
  }

  .response-edit-textarea:focus {
    outline: none;
    border-color: #2980b9;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
  }

  .edit-response-actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    padding-top: 16px;
    border-top: 1px solid #dee2e6;
  }

  .save-response-btn, .cancel-response-btn {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.3s ease;
  }

  .save-response-btn {
    background: #27ae60;
    color: white;
  }

  .save-response-btn:hover:not(:disabled) {
    background: #229954;
  }

  .save-response-btn:disabled {
    background: #bdc3c7;
    cursor: not-allowed;
  }

  .cancel-response-btn {
    background: #95a5a6;
    color: white;
  }

  .cancel-response-btn:hover {
    background: #7f8c8d;
  }

  /* Edit Response Button */
  .edit-response-btn {
    background: none;
    border: none;
    cursor: pointer;
    padding: 6px 8px;
    border-radius: 4px;
    font-size: 0.9rem;
    transition: all 0.3s ease;
    color: #f39c12;
    margin-right: 8px;
  }

  .edit-response-btn:hover {
    background: #fef9e7;
    color: #e67e22;
  }
`;

export default ResearchAgent;
