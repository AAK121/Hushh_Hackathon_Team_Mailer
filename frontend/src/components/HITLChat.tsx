import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github.css';
import { 
  PaperAirplaneIcon, 
  CpuChipIcon, 
  UserIcon, 
  ExclamationTriangleIcon,
  CheckIcon,
  XMarkIcon,
  CogIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import { hushMcpApi, type ConversationMessage } from '../services/hushMcpApi';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sessionId?: string;
  toolCall?: {
    name: string;
    parameters: any;
    needsApproval: boolean;
    approved?: boolean;
  };
}

interface HITLChatProps {
  onBack?: () => void;
  initialPrompt?: string;
  fullChatMode?: boolean;
  onSend?: (message: string) => void;
}

const HITLChat: React.FC<HITLChatProps> = ({ onBack, initialPrompt, fullChatMode = false, onSend }) => {
  const { user } = useAuth();
  
  // Initialize messages with initial prompt if provided
  const [messages, setMessages] = useState<Message[]>(() => {
    if (initialPrompt) {
      return [{
        id: Date.now().toString(),
        role: 'user',
        content: initialPrompt,
        timestamp: new Date(),
      }];
    }
    return [];
  });
  
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showProviderDropdown, setShowProviderDropdown] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [_conversationHistory, setConversationHistory] = useState<ConversationMessage[]>([]); // Chat Agent API conversation state
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [isBackendConnected, setIsBackendConnected] = useState<boolean | null>(null);
  const initialResponseSent = useRef(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // AI Provider settings
  const [selectedProvider, setSelectedProvider] = useState<'openai' | 'anthropic' | 'google'>('openai');
  const [selectedModel, setSelectedModel] = useState('gpt-4');
  const [isConnected] = useState(false);

  // Model options for each provider
  const modelOptions = {
    openai: ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
    anthropic: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
    google: ['gemini-pro', 'gemini-pro-vision']
  };

  // Initialize chat session
  const initializeSession = async () => {
    if (!user?.id) return;
    
    try {
      setIsLoadingHistory(true);
      
      // Test backend connection first
      const connectionTest = await hushMcpApi.testConnection();
      setIsBackendConnected(connectionTest.connected);
      
      if (!connectionTest.connected) {
        console.warn('Backend not connected, using offline mode');
        const sessionId = `offline-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        setCurrentSessionId(sessionId);
        return;
      }
      
      const sessionsResponse = await hushMcpApi.getUserChatSessions(user.id);
      
      if (sessionsResponse.total_sessions > 0) {
        // Get the most recent session
        const sessionIds = Object.keys(sessionsResponse.sessions);
        const latestSessionId = sessionIds.sort((a, b) => {
          const sessionA = sessionsResponse.sessions[a];
          const sessionB = sessionsResponse.sessions[b];
          return new Date(sessionB.last_activity).getTime() - new Date(sessionA.last_activity).getTime();
        })[0];
        
        setCurrentSessionId(latestSessionId);
        
        // Load conversation history if no initial prompt
        if (!initialPrompt) {
          const history = await hushMcpApi.getChatHistory(user.id, latestSessionId);
          setConversationHistory(history.conversation_history);
          
          // Convert to UI messages
          const uiMessages = history.conversation_history.map((msg, index) => ({
            id: `msg-${index}`,
            role: msg.role as 'user' | 'assistant',
            content: msg.content,
            timestamp: new Date(msg.timestamp),
            sessionId: latestSessionId
          }));
          
          setMessages(uiMessages);
        }
      } else {
        // Start a new session
        const sessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        setCurrentSessionId(sessionId);
      }
    } catch (error) {
      console.error('Error initializing chat session:', error);
      
      // Provide helpful error information
      if (error instanceof Error) {
        if (error.message.includes('fetch')) {
          console.warn('Backend service appears to be unavailable. Starting offline session.');
        } else if (error.message.includes('CORS')) {
          console.warn('CORS issue detected. Check backend configuration.');
        } else {
          console.warn('Session initialization failed:', error.message);
        }
      }
      
      // Fallback to new session
      const sessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      setCurrentSessionId(sessionId);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  useEffect(() => {
    if (user?.id) {
      initializeSession();
    }
  }, [user?.id]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowProviderDropdown(false);
      }
    };

    if (showProviderDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showProviderDropdown]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle AI response for initial prompt
  useEffect(() => {
    if (initialPrompt && !initialResponseSent.current && messages.length === 1 && 
        messages[0].role === 'user' && messages[0].content === initialPrompt && 
        user?.id && currentSessionId) {
      initialResponseSent.current = true;
      setIsLoading(true);
      
      // Process initial prompt through Chat Agent API
      hushMcpApi.sendChatMessageWithAutoTokens(user.id, initialPrompt, currentSessionId)
        .then(response => {
          if (response.status === 'success' && response.response) {
            addMessage('assistant', response.response);
            
            // Update conversation history
            setConversationHistory(prev => [
              ...prev,
              { role: 'user', content: initialPrompt, timestamp: new Date().toISOString() },
              { role: 'assistant', content: response.response!, timestamp: new Date().toISOString() }
            ]);
          } else {
            // Fallback to simulated response if API fails
            const errorMessage = response.error || 'I\'m ready to help you. What would you like to know?';
            addMessage('assistant', errorMessage);
          }
        })
        .catch(error => {
          console.error('Error processing initial prompt:', error);
          addMessage('assistant', 'I\'m ready to help you. What would you like to know?');
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, [initialPrompt, messages, user?.id, currentSessionId]);

  // Removed unused testConnection function

  const addMessage = (role: 'user' | 'assistant', content: string, toolCall?: any) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      role,
      content,
      timestamp: new Date(),
      toolCall
    };
    setMessages(prev => [...prev, newMessage]);
    return newMessage.id;
  };

  const handleToolApproval = async (messageId: string, approved: boolean) => {
    setMessages(prev => prev.map(msg => 
      msg.id === messageId && msg.toolCall
        ? { ...msg, toolCall: { ...msg.toolCall, approved } }
        : msg
    ));
    
    if (approved) {
      setIsLoading(true);
      // Simulate tool execution
      setTimeout(() => {
        addMessage('assistant', 'Tool executed successfully! The action has been completed.');
        setIsLoading(false);
      }, 2000);
    } else {
      addMessage('assistant', 'Tool execution was denied. How else can I help you?');
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading || !user?.id || !currentSessionId) return;

    const userMessage = input.trim();
    addMessage('user', userMessage);
    setInput('');
    if (onSend) onSend(userMessage); // Notify parent to switch to full chat mode
    setIsLoading(true);

    // Check if backend is connected
    if (isBackendConnected === false) {
      setTimeout(() => {
        addMessage('assistant', 'I\'m currently in offline mode as the backend service is not available. Once the service is restored, I\'ll be able to provide AI-powered responses and access to tools like email, calendar, and weather services.');
        setIsLoading(false);
      }, 1000);
      return;
    }

    try {
      const response = await hushMcpApi.sendChatMessageWithAutoTokens(
        user.id,
        userMessage,
        currentSessionId
      );

      if (response.status === 'success' && response.response) {
        addMessage('assistant', response.response);
        setConversationHistory(prev => [
          ...prev,
          { role: 'user', content: userMessage, timestamp: new Date().toISOString() },
          { role: 'assistant', content: response.response!, timestamp: new Date().toISOString() }
        ]);
      } else if (response.status === 'permission_denied') {
        addMessage('assistant', 'I need permission to access the required services. Please check your consent settings and try again.');
      } else {
        const errorMessage = response.error || `API returned status: ${response.status}. Please try again.`;
        addMessage('assistant', errorMessage);
      }

    } catch (error) {
      setIsBackendConnected(false);
      let errorMessage = 'Sorry, I encountered an error while processing your message.';
      if (error instanceof Error) {
        if (error.message.includes('fetch') || error.message.includes('Failed to fetch')) {
          errorMessage = 'The backend service appears to be unavailable. Please check your connection and try again.';
        } else if (error.message.includes('CORS')) {
          errorMessage += ' There was a CORS issue. Please check the backend configuration.';
        } else {
          errorMessage += ` Error: ${error.message}`;
        }
      }
      errorMessage += ' I\'m now in offline mode.';
      addMessage('assistant', errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <StyledWrapper fullChatMode={fullChatMode}>
      <div className={fullChatMode ? "chat-full" : "modal"}>
        {/* ChatGPT-style Header */}
        <div className="chat-header">
          <div className="header-content">
            <div className="header-left">
              <div className="chat-title">
                <CpuChipIcon className="title-icon" />
                <span>Hushh AI Assistant</span>
              </div>
              {currentSessionId && (
                <div className="session-info">
                  <span className={`status-indicator ${isBackendConnected ? 'connected' : 'offline'}`}></span>
                  <span className="session-text">
                    {isBackendConnected ? 'Connected' : 'Offline'} • Session {currentSessionId.slice(-8)}
                  </span>
                </div>
              )}
            </div>
            {onBack && (
              <button onClick={onBack} className="close-button">
                <XMarkIcon />
              </button>
            )}
          </div>
        </div>

        {/* Chat Body */}
        <div className={fullChatMode ? "chat-body" : "modal-body"}>
          <div className="messages-container">
            {isLoadingHistory && (
              <div className="loading-state">
                <ClockIcon className="loading-icon" />
                <div>
                  <h3>Loading conversation...</h3>
                  <p>Retrieving your chat history</p>
                </div>
              </div>
            )}
            
            {!isLoadingHistory && messages.length === 0 && (
              <div className="empty-state">
                <div className="empty-icon">
                  <CpuChipIcon />
                </div>
                <h2>How can I help you today?</h2>
                <p>I'm your AI assistant. Feel free to ask me anything!</p>
              </div>
            )}
            
            {messages.map(message => (
              <div key={message.id} className={`message-wrapper ${message.role}`}>
                <div className="message-container">
                  <div className="message-avatar">
                    {message.role === 'user' ? (
                      <div className="user-avatar">
                        <UserIcon />
                      </div>
                    ) : (
                      <div className="assistant-avatar">
                        <CpuChipIcon />
                      </div>
                    )}
                  </div>
                  <div className="message-content">
                    <div className="message-text">
                      <ReactMarkdown 
                        remarkPlugins={[remarkGfm]} 
                        rehypePlugins={[rehypeHighlight]}
                        components={{
                          code: ({ className, children, ...props }: any) => {
                            const match = /language-(\w+)/.exec(className || '');
                            const codeString = String(children).replace(/\n$/, '');
                            const isInline = !match;
                            if (!isInline && match) {
                              return (
                                <div className="code-block">
                                  <div className="code-header">
                                    <span className="language-label">{match[1]}</span>
                                    <button 
                                      className="copy-button" 
                                      onClick={async () => {
                                        try {
                                          await navigator.clipboard.writeText(codeString);
                                          const button = document.activeElement as HTMLButtonElement;
                                          const originalText = button.textContent;
                                          button.textContent = 'Copied!';
                                          setTimeout(() => { button.textContent = originalText; }, 1000);
                                        } catch (err) {}
                                      }}
                                    >
                                      Copy
                                    </button>
                                  </div>
                                  <pre><code className={className}>{children}</code></pre>
                                </div>
                              );
                            }
                            return (<code className={className} {...props}>{children}</code>);
                          }
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </div>
                    
                    {/* Tool Approval UI */}
                    {message.toolCall && message.toolCall.needsApproval && message.toolCall.approved === undefined && (
                      <div className="tool-approval">
                        <div className="tool-header">
                          <ExclamationTriangleIcon className="tool-icon" />
                          <span>Tool requires approval</span>
                        </div>
                        <div className="tool-details">
                          <p><strong>Tool:</strong> {message.toolCall.name}</p>
                          <details>
                            <summary>View parameters</summary>
                            <pre>{JSON.stringify(message.toolCall.parameters, null, 2)}</pre>
                          </details>
                        </div>
                        <div className="tool-actions">
                          <button 
                            className="approve-btn" 
                            onClick={() => handleToolApproval(message.id, true)}
                            disabled={isLoading}
                          >
                            <CheckIcon />
                            Approve
                          </button>
                          <button 
                            className="deny-btn" 
                            onClick={() => handleToolApproval(message.id, false)}
                            disabled={isLoading}
                          >
                            <XMarkIcon />
                            Deny
                          </button>
                        </div>
                      </div>
                    )}
                    
                    {message.toolCall && message.toolCall.approved !== undefined && (
                      <div className={`tool-result ${message.toolCall.approved ? 'approved' : 'denied'}`}>
                        {message.toolCall.approved ? '✅ Approved' : '❌ Denied'} ({message.toolCall.name})
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="message-wrapper assistant">
                <div className="message-container">
                  <div className="message-avatar">
                    <div className="assistant-avatar">
                      <CpuChipIcon />
                    </div>
                  </div>
                  <div className="message-content">
                    <div className="typing-indicator">
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* ChatGPT-style Input */}
        <div className={fullChatMode ? "chat-footer" : "modal-footer"}>
          <div className="input-container">
            <div className="input-wrapper">
              <textarea
                className="message-input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                placeholder="Message Hushh AI Assistant..."
                disabled={isLoading}
                rows={1}
              />
              <button
                className="send-button"
                onClick={handleSendMessage}
                disabled={!input.trim() || isLoading}
              >
                <PaperAirplaneIcon />
              </button>
            </div>
            
            {/* Settings dropdown for non-fullscreen mode */}
            {!fullChatMode && (
              <div className="settings-dropdown-container" ref={dropdownRef}>
                <button
                  className="settings-button"
                  onClick={() => setShowProviderDropdown(!showProviderDropdown)}
                >
                  <CogIcon />
                  <span>{selectedProvider === 'openai' ? 'OpenAI' : selectedProvider === 'anthropic' ? 'Anthropic' : 'Google'}</span>
                </button>
                
                {showProviderDropdown && (
                  <div className="settings-dropdown">
                    <div className="dropdown-section">
                      <div className="dropdown-header">AI Provider</div>
                      <div className="dropdown-options">
                        {(['openai', 'anthropic', 'google'] as const).map(provider => (
                          <button
                            key={provider}
                            className={`dropdown-option ${selectedProvider === provider ? 'active' : ''}`}
                            onClick={() => {
                              setSelectedProvider(provider);
                              setSelectedModel(modelOptions[provider][0]);
                              setShowProviderDropdown(false);
                            }}
                          >
                            <span>{provider === 'openai' ? 'OpenAI' : provider === 'anthropic' ? 'Anthropic' : 'Google'}</span>
                            {selectedProvider === provider && <span>✓</span>}
                          </button>
                        ))}
                      </div>
                    </div>
                    
                    <div className="dropdown-section">
                      <div className="dropdown-header">Model</div>
                      <div className="dropdown-options">
                        {modelOptions[selectedProvider].map(model => (
                          <button
                            key={model}
                            className={`dropdown-option ${selectedModel === model ? 'active' : ''}`}
                            onClick={() => setSelectedModel(model)}
                          >
                            <span>{model}</span>
                            {selectedModel === model && <span>✓</span>}
                          </button>
                        ))}
                      </div>
                    </div>
                    
                    <div className="dropdown-section">
                      <div className="dropdown-header">Status</div>
                      <div className="status-info">
                        <div className="status-item">
                          <span className={`status-dot ${isBackendConnected ? 'connected' : 'disconnected'}`}></span>
                          Backend: {isBackendConnected ? 'Connected' : 'Offline'}
                        </div>
                        <div className="status-item">
                          <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></span>
                          API: {isConnected ? 'Connected' : 'Disconnected'}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </StyledWrapper>
  );
};

const StyledWrapper = styled.div<{ fullChatMode?: boolean }>`
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  
  ${({ fullChatMode }) => fullChatMode ? `
    width: 100vw;
    height: 100vh;
    background: #ffffff;
    display: flex;
    flex-direction: column;
    
    .chat-full {
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
    }
  ` : `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 20px;
    
    .modal {
      width: 100%;
      max-width: 768px;
      height: 90vh;
      background: #ffffff;
      border-radius: 12px;
      display: flex;
      flex-direction: column;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    }
  `}
  
  /* ChatGPT-style Header */
  .chat-header {
    background: #ffffff;
    border-bottom: 1px solid #e5e7eb;
    padding: 16px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
  }
  
  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
  }
  
  .header-left {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  
  .chat-title {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 18px;
    font-weight: 600;
    color: #111827;
  }
  
  .title-icon {
    width: 24px;
    height: 24px;
    color: #6b7280;
  }
  
  .session-info {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: #6b7280;
  }
  
  .status-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    
    &.connected {
      background: #10b981;
    }
    
    &.offline {
      background: #ef4444;
    }
  }
  
  .close-button {
    width: 32px;
    height: 32px;
    border: none;
    background: none;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: #6b7280;
    transition: all 0.2s;
    
    &:hover {
      background: #f3f4f6;
      color: #111827;
    }
    
    svg {
      width: 16px;
      height: 16px;
    }
  }
  
  /* Chat Body */
  .chat-body, .modal-body {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
  
  .messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 24px 0;
    display: flex;
    flex-direction: column;
    gap: 0;
    
    /* Custom scrollbar */
    &::-webkit-scrollbar {
      width: 4px;
    }
    
    &::-webkit-scrollbar-track {
      background: transparent;
    }
    
    &::-webkit-scrollbar-thumb {
      background: #d1d5db;
      border-radius: 4px;
    }
    
    &::-webkit-scrollbar-thumb:hover {
      background: #9ca3af;
    }
  }
  
  /* Empty and Loading States */
  .empty-state, .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    min-height: 300px;
    gap: 16px;
    color: #6b7280;
  }
  
  .empty-icon, .loading-icon {
    width: 48px;
    height: 48px;
    color: #9ca3af;
  }
  
  .empty-state h2, .loading-state h3 {
    font-size: 24px;
    font-weight: 600;
    color: #111827;
    margin: 0;
  }
  
  .empty-state p, .loading-state p {
    font-size: 16px;
    color: #6b7280;
    margin: 0;
  }
  
  /* Message Styles */
  .message-wrapper {
    border-bottom: 1px solid #f3f4f6;
    
    &.user {
      background: #f9fafb;
    }
    
    &.assistant {
      background: #ffffff;
    }
  }
  
  .message-container {
    max-width: 768px;
    margin: 0 auto;
    padding: 24px;
    display: flex;
    gap: 16px;
    align-items: flex-start;
  }
  
  .message-avatar {
    flex-shrink: 0;
    width: 32px;
    height: 32px;
  }
  
  .user-avatar {
    width: 32px;
    height: 32px;
    background: transparent;
    border: 2px solid #e5e7eb;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    
    svg {
      width: 16px;
      height: 16px;
      color: #6b7280;
    }
  }
  
  .assistant-avatar {
    width: 32px;
    height: 32px;
    background: #10b981;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    
    svg {
      width: 16px;
      height: 16px;
      color: white;
    }
  }
  
  .message-content {
    flex: 1;
    min-width: 0;
  }
  
  .message-text {
    font-size: 15px;
    line-height: 1.6;
    color: #111827;
    
    /* Markdown styling */
    h1, h2, h3, h4, h5, h6 {
      margin: 16px 0 8px 0;
      font-weight: 600;
      color: #111827;
      
      &:first-child {
        margin-top: 0;
      }
    }
    
    h1 { font-size: 1.5em; }
    h2 { font-size: 1.3em; }
    h3 { font-size: 1.1em; }
    
    p {
      margin: 12px 0;
      
      &:first-child {
        margin-top: 0;
      }
      
      &:last-child {
        margin-bottom: 0;
      }
    }
    
    ul, ol {
      margin: 12px 0;
      padding-left: 24px;
      
      li {
        margin: 4px 0;
      }
    }
    
    blockquote {
      margin: 16px 0;
      padding: 12px 16px;
      background: #f9fafb;
      border-left: 4px solid #d1d5db;
      border-radius: 0 6px 6px 0;
      
      p {
        margin: 0;
      }
    }
    
    code {
      background: #f3f4f6;
      padding: 2px 6px;
      border-radius: 4px;
      font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
      font-size: 0.9em;
      color: #1f2937;
    }
    
    pre {
      margin: 16px 0;
      
      code {
        background: none;
        padding: 0;
        font-size: 0.85em;
      }
    }
    
    strong {
      font-weight: 600;
    }
    
    em {
      font-style: italic;
    }
    
    a {
      color: #3b82f6;
      text-decoration: underline;
      
      &:hover {
        color: #1d4ed8;
      }
    }
  }
  
  /* Code blocks */
  .code-block {
    margin: 16px 0;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    overflow: hidden;
    background: #f8fafc;
  }
  
  .code-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 16px;
    background: #f1f5f9;
    border-bottom: 1px solid #e5e7eb;
    font-size: 12px;
  }
  
  .language-label {
    font-weight: 500;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  
  .copy-button {
    background: none;
    border: none;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    color: #6b7280;
    cursor: pointer;
    transition: all 0.2s;
    
    &:hover {
      background: #e5e7eb;
      color: #111827;
    }
  }
  
  .code-block pre {
    margin: 0;
    padding: 16px;
    background: #f8fafc;
    overflow-x: auto;
    
    code {
      background: none;
      font-size: 13px;
    }
  }
  
  /* Tool approval */
  .tool-approval {
    margin-top: 16px;
    border: 1px solid #fbbf24;
    border-radius: 8px;
    overflow: hidden;
    background: #fffbeb;
  }
  
  .tool-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 16px;
    background: #fef3c7;
    border-bottom: 1px solid #fbbf24;
    font-size: 14px;
    font-weight: 500;
    color: #92400e;
  }
  
  .tool-icon {
    width: 16px;
    height: 16px;
  }
  
  .tool-details {
    padding: 16px;
    
    p {
      margin: 0 0 8px 0;
      font-size: 14px;
      color: #78716c;
    }
    
    details {
      margin-top: 8px;
      
      summary {
        cursor: pointer;
        font-size: 13px;
        color: #6b7280;
        
        &:hover {
          color: #111827;
        }
      }
      
      pre {
        margin-top: 8px;
        padding: 8px;
        background: #f3f4f6;
        border-radius: 4px;
        font-size: 12px;
        overflow-x: auto;
      }
    }
  }
  
  .tool-actions {
    display: flex;
    gap: 8px;
    padding: 0 16px 16px;
  }
  
  .approve-btn, .deny-btn {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 8px 16px;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    
    svg {
      width: 14px;
      height: 14px;
    }
    
    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
  
  .approve-btn {
    background: #10b981;
    color: white;
    
    &:hover:not(:disabled) {
      background: #059669;
    }
  }
  
  .deny-btn {
    background: #ef4444;
    color: white;
    
    &:hover:not(:disabled) {
      background: #dc2626;
    }
  }
  
  .tool-result {
    margin-top: 12px;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
    
    &.approved {
      background: #d1fae5;
      color: #065f46;
    }
    
    &.denied {
      background: #fee2e2;
      color: #991b1b;
    }
  }
  
  /* Typing indicator */
  .typing-indicator {
    display: flex;
    gap: 4px;
    align-items: center;
    padding: 16px 0;
  }
  
  .typing-dot {
    width: 8px;
    height: 8px;
    background: #9ca3af;
    border-radius: 50%;
    animation: typing 1.4s infinite ease-in-out;
    
    &:nth-child(2) {
      animation-delay: 0.2s;
    }
    
    &:nth-child(3) {
      animation-delay: 0.4s;
    }
  }
  
  @keyframes typing {
    0%, 60%, 100% {
      transform: translateY(0);
      opacity: 0.4;
    }
    30% {
      transform: translateY(-8px);
      opacity: 1;
    }
  }
  
  /* Input area */
  .chat-footer, .modal-footer {
    background: #ffffff;
    border-top: 1px solid #e5e7eb;
    padding: 24px;
    flex-shrink: 0;
  }
  
  .input-container {
    max-width: 768px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  .input-wrapper {
    display: flex;
    align-items: flex-end;
    gap: 12px;
    background: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 12px;
    padding: 12px;
    transition: all 0.2s;
    
    &:focus-within {
      border-color: #9ca3af;
      box-shadow: 0 0 0 3px rgba(156, 163, 175, 0.1);
    }
  }
  
  .message-input {
    flex: 1;
    border: none;
    outline: none;
    background: none;
    resize: none;
    font-size: 15px;
    line-height: 1.5;
    color: #111827;
    font-family: inherit;
    min-height: 24px;
    max-height: 120px;
    
    &::placeholder {
      color: #9ca3af;
    }
    
    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
  
  .send-button {
    width: 32px;
    height: 32px;
    border: 1px solid #d1d5db;
    background: transparent;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
    flex-shrink: 0;
    
    svg {
      width: 16px;
      height: 16px;
      color: #6b7280;
    }
    
    &:hover:not(:disabled) {
      background: #f9fafb;
      border-color: #9ca3af;
    }
    
    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      background: #d1d5db;
    }
  }
  
  /* Settings dropdown */
  .settings-dropdown-container {
    position: relative;
  }
  
  .settings-button {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border: 1px solid #d1d5db;
    background: #ffffff;
    border-radius: 8px;
    font-size: 13px;
    color: #6b7280;
    cursor: pointer;
    transition: all 0.2s;
    
    svg {
      width: 14px;
      height: 14px;
    }
    
    &:hover {
      background: #f9fafb;
      border-color: #9ca3af;
    }
  }
  
  .settings-dropdown {
    position: absolute;
    bottom: 100%;
    right: 0;
    margin-bottom: 8px;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    min-width: 240px;
    z-index: 1000;
    overflow: hidden;
  }
  
  .dropdown-section {
    padding: 12px;
    border-bottom: 1px solid #f3f4f6;
    
    &:last-child {
      border-bottom: none;
    }
  }
  
  .dropdown-header {
    font-size: 12px;
    font-weight: 600;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
  }
  
  .dropdown-options {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  
  .dropdown-option {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    border: none;
    background: none;
    border-radius: 6px;
    font-size: 14px;
    text-align: left;
    cursor: pointer;
    transition: all 0.2s;
    
    &:hover {
      background: #f3f4f6;
    }
    
    &.active {
      background: #f3f4f6;
      color: #374151;
    }
  }
  
  .status-info {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  
  .status-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: #6b7280;
  }
  
  .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    
    &.connected {
      background: #10b981;
    }
    
    &.disconnected {
      background: #ef4444;
    }
  }
  
  /* Responsive design */
  @media (max-width: 768px) {
    ${({ fullChatMode }) => !fullChatMode && `
      padding: 10px;
      
      .modal {
        height: 95vh;
        max-width: none;
        border-radius: 8px;
      }
    `}
    
    .chat-header {
      padding: 12px 16px;
    }
    
    .chat-title {
      font-size: 16px;
    }
    
    .message-container {
      padding: 16px;
    }
    
    .chat-footer, .modal-footer {
      padding: 16px;
    }
    
    .input-wrapper {
      padding: 8px;
    }
    
    .message-input {
      font-size: 16px; /* Prevents zoom on iOS */
    }
  }
`;

export default HITLChat;
