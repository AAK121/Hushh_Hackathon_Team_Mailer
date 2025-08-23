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
        {/* Modal Header (hidden in fullChatMode) */}
        {!fullChatMode && (
          <div className="modal-header">
            <div className="modal-logo">
              <span className="logo-circle">
                <CpuChipIcon />
              </span>
              <div>
                <h2 className="modal-title">Your Personal Agent</h2>
                <p className="modal-subtitle">
                  Human-in-the-Loop AI Chat Interface
                  {currentSessionId && (
                    <span style={{ fontSize: '0.75rem', color: 'var(--c-text-secondary)', marginLeft: '8px', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                      Session: {currentSessionId.slice(-8)}
                    </span>
                  )}
                  {isBackendConnected !== null && (
                    <span style={{ fontSize: '0.75rem', color: isBackendConnected ? '#10b981' : '#ef4444', marginLeft: '8px', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                      <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: isBackendConnected ? '#10b981' : '#ef4444' }}></span>
                      {isBackendConnected ? 'Connected' : 'Offline'}
                    </span>
                  )}
                </p>
              </div>
            </div>
            {onBack && (
              <button onClick={onBack} className="btn-close">
                <XMarkIcon />
              </button>
            )}
          </div>
        )}
        {/* Chat Body */}
  <div className={fullChatMode ? "chat-body" : "modal-body"}>
          <div className="messages-container">
            {isLoadingHistory && (
              <div className="welcome-message">
                <div className="welcome-icon">
                  <ClockIcon style={{ width: '48px', height: '48px', color: 'var(--c-action-primary)' }} />
                </div>
                <h2>Loading conversation history...</h2>
                <p>Please wait while we retrieve your previous chat sessions.</p>
              </div>
            )}
            {!isLoadingHistory && messages.length === 0 && (
              <div className="welcome-message"></div>
            )}
            {messages.map(message => (
              <div key={message.id} className={`message ${message.role} chat-appear`}>
                <div className="message-avatar">
                  {message.role === 'user' ? (
                    <UserIcon className="avatar-icon" />
                  ) : (
                    <CpuChipIcon className="avatar-icon" />
                  )}
                </div>
                <div className="message-content">
                  <div className="message-role">{message.role === 'user' ? 'You' : 'AI Assistant'}</div>
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
                              <div className="code-block-container">
                                <div className="code-header">
                                  <span className="language-label">{match[1]}</span>
                                  <button className="copy-button" onClick={async () => {
                                    try {
                                      await navigator.clipboard.writeText(codeString);
                                      const button = document.activeElement as HTMLButtonElement;
                                      const originalText = button.textContent;
                                      button.textContent = '✅';
                                      setTimeout(() => { button.textContent = originalText; }, 1000);
                                    } catch (err) {}
                                  }} title="Copy code">📋</button>
                                </div>
                                <pre className={className}><code>{children}</code></pre>
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
                  {/* ...existing code... */}
                  {message.toolCall && message.toolCall.needsApproval && message.toolCall.approved === undefined && (
                    <div className="tool-confirmation">
                      <div className="tool-header">
                        <ExclamationTriangleIcon className="tool-icon" />
                        <span className="tool-title">Action Requires Approval</span>
                      </div>
                      <div className="tool-details">
                        <div className="tool-name">Tool: <code>{message.toolCall.name}</code></div>
                        <div className="tool-args">
                          <strong>Parameters:</strong>
                          <pre className="args-display">{JSON.stringify(message.toolCall.parameters, null, 2)}</pre>
                        </div>
                      </div>
                      <div className="tool-actions">
                        <button className="approve-button" onClick={() => handleToolApproval(message.id, true)} disabled={isLoading}>
                          <CheckIcon className="button-icon" /> Approve & Execute
                        </button>
                        <button className="deny-button" onClick={() => handleToolApproval(message.id, false)} disabled={isLoading}>
                          <XMarkIcon className="button-icon" /> Deny
                        </button>
                      </div>
                    </div>
                  )}
                  {message.toolCall && message.toolCall.approved !== undefined && (
                    <div className={`tool-result ${message.toolCall.approved ? 'approved' : 'denied'}`}>
                      <div className="result-header">
                        <strong>{message.toolCall.approved ? '✅ Approved' : '❌ Denied'} ({message.toolCall.name})</strong>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="loading-indicator">
                <CpuChipIcon className="avatar-icon" />
                <div className="loading-dots">
                  <div className="loading-dot"></div>
                  <div className="loading-dot"></div>
                  <div className="loading-dot"></div>
                </div>
                <span>AI is thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
        {/* Chat Footer */}
  <div className={fullChatMode ? "chat-footer" : "modal-footer"}>
          <div className="input-area">
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
              placeholder="Type your message here... (Shift+Enter for new line)"
              disabled={isLoading}
            />
            <button
              className="btn-primary"
              onClick={handleSendMessage}
              disabled={!input.trim() || isLoading}
            >
              <PaperAirplaneIcon className="button-icon" />
              Send
            </button>
            {/* Hide AI Provider dropdown in fullChatMode */}
            {!fullChatMode && (
              <div className="settings-dropdown-container" ref={dropdownRef}>
                <button
                  className="btn-secondary settings-trigger"
                  onClick={() => { setShowProviderDropdown(!showProviderDropdown); }}
                  title="AI Provider"
                >
                  <CogIcon className="button-icon" />
                  <span className="provider-label">
                    {selectedProvider === 'openai' ? 'OpenAI' : selectedProvider === 'anthropic' ? 'Anthropic' : 'Google'}
                  </span>
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
                            <span className="option-name">
                              {provider === 'openai' ? 'OpenAI' : provider === 'anthropic' ? 'Anthropic' : 'Google'}
                            </span>
                            {selectedProvider === provider && <span className="checkmark">✓</span>}
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
                            onClick={() => { setSelectedModel(model); }}
                          >
                            <span className="option-name">{model}</span>
                            {selectedModel === model && <span className="checkmark">✓</span>}
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
  ${({ fullChatMode }) => fullChatMode && `
    width: 100vw !important;
    min-height: 100vh !important;
    background: #f0f4f9 !important;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  .chat-full {
      width: 100vw;
      min-height: 100vh;
      background: #f0f4f9;
      border-radius: 0;
      box-shadow: none;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 0;
    }
  .chat-body {
      flex: 1;
      width: 100vw;
      max-width: 900px;
      margin: 0 auto;
      padding: 32px 0 0 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: #f0f4f9;
      min-height: 0;
    }
  .chat-footer {
      width: 100vw;
      max-width: 900px;
      margin: 0 auto;
      padding: 0 0 32px 0;
      background: #f0f4f9;
      border-top: 1px solid #e2e8f0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }
    .input-area {
      width: 100%;
      display: flex;
      gap: 12px;
      align-items: center;
      justify-content: center;
      padding: 0 32px;
    }
    .message-input {
      flex: 1;
      border: 2px solid #e2e8f0;
      border-radius: 12px;
      padding: 16px;
      font-size: 15px;
      background: #ffffff;
      color: #0d0f21;
      transition: border-color 0.2s;
      &:focus {
        outline: none;
        border-color: #4b90ff;
      }
      &::placeholder {
        color: #64748b;
      }
      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
    .btn-primary {
      background: #4b90ff;
      color: white;
      border-radius: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      min-width: 56px;
      border: none;
      padding: 16px;
      &:hover:not(:disabled) {
        background: #1e40af;
        transform: translateY(-1px);
      }
      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
    .messages-container {
      flex: 1;
      overflow-y: auto;
      overflow-x: hidden;
      padding: 0 32px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      min-height: 0;
      align-items: center;
      justify-content: center;
    }
    .message {
      max-width: 85%;
      margin: 0 auto;
      opacity: 0;
      transform: translateY(24px);
      animation: chatFadeIn 0.6s cubic-bezier(0.23, 1, 0.32, 1) forwards;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    @keyframes chatFadeIn {
      0% { opacity: 0; transform: translateY(24px); }
      60% { opacity: 0.7; transform: translateY(-4px); }
      100% { opacity: 1; transform: translateY(0); }
    }
    .message-avatar {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: #e9e5ff;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }
    .avatar-icon {
      width: 20px;
      height: 20px;
      color: #4b90ff;
    }
    .message.user .message-content {
      background: #4b90ff;
      color: white;
    }
    .message.assistant .message-content {
      background: #f8fafc;
      color: #0d0f21;
    }
    .message-content {
      border-radius: 16px;
      padding: 16px;
      position: relative;
      min-width: 0;
      overflow-wrap: break-word;
      word-wrap: break-word;
      word-break: break-word;
      hyphens: auto;
    }
    .message-role {
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 8px;
      color: #64748b;
    }
    .message-text {
      font-size: 15px;
      line-height: 1.5;
      margin: 0;
      color: #0d0f21;
      word-wrap: break-word;
      overflow-wrap: break-word;
      max-width: 100%;
      overflow-x: hidden;
    }
    /* ...existing code... */
  `}
  /* ...existing code... */
  :root {
    --c-action-primary: #2e44ff;
    --c-action-primary-accent: #e9e5ff;
    --c-text-primary: #0d0f21;
    --c-text-secondary: #64748b;
    --c-bg-primary: #ffffff;
    --c-bg-secondary: #f8fafc;
    --c-border: #e2e8f0;
    --c-shadow: rgba(15, 23, 42, 0.08);
  }

  * {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  }

  width: 100%;
  height: auto;

  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;

  .modal {
    background: #ffffff;
    border-radius: 32px;
    box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.08), 0 10px 10px -5px rgba(15, 23, 42, 0.04);
    max-width: 800px;
    width: 100%;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    border: 1px solid #e2e8f0;
  }

  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 24px 32px;
    border-bottom: 1px solid #e2e8f0;
    background: #ffffff;
  }

  .modal-logo {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .logo-circle {
    width: 48px;
    height: 48px;
    background: #2e44ff;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;

    svg {
      width: 24px;
      height: 24px;
    }
  }

  .modal-title {
    font-size: 20px;
    font-weight: 600;
    color: #0d0f21;
    margin: 0 0 4px 0;
  }

  .modal-subtitle {
    font-size: 14px;
    color: #64748b;
    margin: 0;
  }

  .btn-close {
    width: 40px;
    height: 40px;
    border: none;
    background: #f8fafc;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: #64748b;
    transition: all 0.2s;

    &:hover {
      background: #e2e8f0;
      color: #0d0f21;
    }

    svg {
      width: 20px;
      height: 20px;
    }
  }

  .modal-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .messages-container {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 24px 32px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    min-height: 0; /* Important for flex container overflow */
  }

  .welcome-message {
    text-align: center;
    max-width: 500px;
    margin: auto;
    padding: 48px 24px;
  }

  .welcome-icon {
    font-size: 48px;
    margin-bottom: 24px;
  }

  .welcome-message h2 {
    font-size: 24px;
    font-weight: 600;
    color: #0d0f21;
    margin: 0 0 16px 0;
  }

  .welcome-message p {
    font-size: 16px;
    color: #64748b;
    line-height: 1.6;
    margin: 0 0 32px 0;
  }

  .example-prompts {
    background: #f8fafc;
    border-radius: 12px;
    padding: 24px;
    text-align: left;

    p {
      font-weight: 600;
      color: #0d0f21;
      margin: 0 0 12px 0;
    }

    ul {
      margin: 0;
      padding-left: 20px;
      
      li {
        color: #64748b;
        margin: 8px 0;
        font-style: italic;
      }
    }
  }

  .message {
    display: flex;
    gap: 12px;
    max-width: 85%;
    min-width: 0; /* Allows flex items to shrink below content size */
    opacity: 0;
    transform: translateY(24px);
    animation: chatFadeIn 0.6s cubic-bezier(0.23, 1, 0.32, 1) forwards;

    &.user {
      align-self: flex-end;
      flex-direction: row-reverse;

      .message-content {
        background: #2e44ff;
        color: white;
      }

      .message-role {
        color: rgba(255, 255, 255, 0.8);
      }
    }

    &.assistant {
      align-self: flex-start;

      .message-content {
        background: #f8fafc;
        color: #0d0f21;
      }
    }
  }

  @keyframes chatFadeIn {
    0% {
      opacity: 0;
      transform: translateY(24px);
    }
    60% {
      opacity: 0.7;
      transform: translateY(-4px);
    }
    100% {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .message-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #e9e5ff;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;

    .avatar-icon {
      width: 20px;
      height: 20px;
      color: #2e44ff;
    }

    .user & {
      background: #2e44ff;

      .avatar-icon {
        color: white;
      }
    }
  }

  .message-content {
    border-radius: 16px;
    padding: 16px;
    position: relative;
    min-width: 0; /* Allows content to shrink */
    overflow-wrap: break-word;
    word-wrap: break-word;
    word-break: break-word;
    hyphens: auto;
  }

  .message-role {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
    color: #64748b;
  }

  .message-text {
    font-size: 15px;
    line-height: 1.5;
    margin: 0;
    color: var(--c-text-primary);
    word-wrap: break-word;
    overflow-wrap: break-word;
    max-width: 100%;
    overflow-x: hidden;

    /* Ensure all child elements respect container bounds */
    * {
      max-width: 100% !important;
      word-wrap: break-word !important;
      overflow-wrap: break-word !important;
    }

    /* Specific handling for different elements */
    p, div, span {
      word-break: break-word;
      hyphens: auto;
    }

    /* Code spans should break */
    code:not(pre code) {
      word-break: break-all;
      white-space: pre-wrap;
    }

    /* Markdown styling */
    h1, h2, h3, h4, h5, h6 {
      margin: 16px 0 8px 0;
      font-weight: 600;
      color: var(--c-text-primary);
    }

    h1 { font-size: 1.4em; }
    h2 { font-size: 1.25em; }
    h3 { font-size: 1.1em; }
    h4, h5, h6 { font-size: 1em; }

    p {
      margin: 8px 0;
      
      &:first-child {
        margin-top: 0;
      }
      
      &:last-child {
        margin-bottom: 0;
      }
    }

    ul, ol {
      margin: 8px 0;
      padding-left: 20px;

      li {
        margin: 4px 0;
      }
    }

    blockquote {
      margin: 12px 0;
      padding: 12px 16px;
      border-left: 4px solid var(--c-action-primary);
      background: rgba(46, 68, 255, 0.05);
      border-radius: 0 8px 8px 0;
      
      p {
        margin: 0;
      }
    }

    code {
      background: #f1f5f9;
      border: 1px solid #e2e8f0;
      padding: 2px 6px;
      border-radius: 4px;
      font-family: 'Fira Code', 'Monaco', 'Cascadia Code', monospace;
      font-size: 0.9em;
      color: #1e293b;
    }

    pre {
      background: #f8fafc !important;
      border: 1px solid #e2e8f0;
      padding: 16px;
      border-radius: 8px;
      overflow-x: auto;
      margin: 12px 0;
      position: relative;
      max-width: 100%;
      white-space: pre-wrap;
      word-wrap: break-word;
      
      code {
        background: none !important;
        padding: 0;
        border-radius: 0;
        font-size: 0.85em;
        color: inherit !important;
      }

      &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 8px;
        background: linear-gradient(90deg, #2e44ff, #7c3aed);
        border-radius: 8px 8px 0 0;
      }
    }

    strong {
      font-weight: 600;
      color: var(--c-text-primary);
    }

    em {
      font-style: italic;
      color: var(--c-text-secondary);
    }

    a {
      color: var(--c-action-primary);
      text-decoration: none;
      
      &:hover {
        text-decoration: underline;
      }
    }

    table {
      width: 100%;
      max-width: 100%;
      border-collapse: collapse;
      margin: 12px 0;
      overflow-x: auto;
      display: block;

      thead, tbody, tr {
        display: table;
        width: 100%;
        table-layout: fixed;
      }

      th, td {
        border: 1px solid var(--c-border);
        padding: 8px 12px;
        text-align: left;
        overflow: hidden;
        text-overflow: ellipsis;
        word-wrap: break-word;
        max-width: 0;
        white-space: normal;
      }

      th {
        background: var(--c-bg-secondary);
        font-weight: 600;
      }
    }

    hr {
      border: none;
      border-top: 1px solid var(--c-border);
      margin: 16px 0;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      margin: 16px 0;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      overflow: hidden;
      
      th, td {
        border: 1px solid #e2e8f0;
        padding: 12px 16px;
        text-align: left;
      }
      
      th {
        background: #f8fafc;
        font-weight: 600;
        color: var(--c-text-primary);
      }

      tbody tr:nth-child(even) {
        background: #fafbfc;
      }

      tbody tr:hover {
        background: #f1f5f9;
      }
    }

    /* GitHub Flavored Markdown - Task Lists */
    input[type="checkbox"] {
      margin-right: 8px;
    }

    /* GitHub Flavored Markdown - Strikethrough */
    del {
      color: var(--c-text-secondary);
      text-decoration: line-through;
    }

    /* Code block enhancements */
    .code-block-container {
      margin: 12px 0;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      overflow: hidden;

      .code-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 16px;
        background: #f8fafc;
        border-bottom: 1px solid #e2e8f0;

        .language-label {
          font-size: 12px;
          font-weight: 600;
          color: #64748b;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .copy-button {
          background: none;
          border: none;
          cursor: pointer;
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 14px;
          transition: background-color 0.2s;

          &:hover {
            background: #e2e8f0;
          }
        }
      }

      pre {
        margin: 0 !important;
        border: none !important;
        border-radius: 0 !important;

        &::before {
          display: none;
        }
      }
    }
  }

  .tool-confirmation {
    margin-top: 16px;
    border: 1px solid #fbbf24;
    border-radius: 12px;
    background: #fffbeb;
    overflow: hidden;
  }

  .tool-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 16px;
    background: #fef3c7;
    border-bottom: 1px solid #fbbf24;

    .tool-icon {
      width: 16px;
      height: 16px;
      color: #d97706;
    }

    .tool-title {
      font-weight: 600;
      color: #92400e;
    }
  }

  .tool-details {
    padding: 16px;

    .tool-name {
      font-size: 14px;
      margin-bottom: 12px;
      color: #78716c;

      code {
        background: #f3f4f6;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: 'Monaco', 'Menlo', monospace;
        color: #1f2937;
      }
    }

    .tool-args {
      margin-bottom: 16px;

      strong {
        color: #374151;
        font-size: 14px;
        display: block;
        margin-bottom: 8px;
      }

      .args-display {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        padding: 12px;
        font-size: 12px;
        color: #374151;
        margin: 0;
        overflow-x: auto;
      }
    }
  }

  .tool-actions {
    display: flex;
    gap: 8px;
    padding: 0 16px 16px;

    button {
      flex: 1;
      padding: 10px 16px;
      border: none;
      border-radius: 8px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;

      .button-icon {
        width: 16px;
        height: 16px;
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }

    .approve-button {
      background: #10b981;
      color: white;

      &:hover:not(:disabled) {
        background: #059669;
      }
    }

    .deny-button {
      background: #ef4444;
      color: white;

      &:hover:not(:disabled) {
        background: #dc2626;
      }
    }
  }

  .tool-result {
    margin-top: 12px;
    padding: 12px;
    border-radius: 8px;
    font-size: 14px;

    &.approved {
      background: #d1fae5;
      border: 1px solid #10b981;
      color: #065f46;
    }

    &.denied {
      background: #fee2e2;
      border: 1px solid #ef4444;
      color: #991b1b;
    }

    .result-header {
      margin: 0;
    }
  }

  .loading-indicator {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    color: #64748b;

    .avatar-icon {
      width: 20px;
      height: 20px;
      color: #2e44ff;
    }

    .loading-dots {
      display: flex;
      gap: 4px;

      .loading-dot {
        width: 8px;
        height: 8px;
        background: #2e44ff;
        border-radius: 50%;
        animation: pulse 1.4s ease-in-out infinite both;

        &:nth-child(1) { animation-delay: -0.32s; }
        &:nth-child(2) { animation-delay: -0.16s; }
        &:nth-child(3) { animation-delay: 0s; }
      }
    }
  }

  @keyframes pulse {
    0%, 80%, 100% {
      transform: scale(0.5);
      opacity: 0.5;
    }
    40% {
      transform: scale(1);
      opacity: 1;
    }
  }

  .modal-footer {
    padding: 24px 32px;
    border-top: 1px solid #e2e8f0;
    background: #ffffff;
  }

  .input-area {
    display: flex;
    gap: 12px;
    align-items: end;
  }

  .message-input {
    flex: 1;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px;
    font-size: 15px;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    resize: none;
    min-height: 56px;
    max-height: 120px;
    background: #ffffff;
    color: #0d0f21;
    transition: border-color 0.2s;

    &:focus {
      outline: none;
      border-color: #2e44ff;
    }

    &::placeholder {
      color: #64748b;
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }

  .btn-primary, .btn-secondary {
    padding: 16px;
    border: none;
    border-radius: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    min-width: 56px;

    .button-icon {
      width: 20px;
      height: 20px;
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }

  .btn-primary {
    background: #2e44ff;
    color: white;

    &:hover:not(:disabled) {
      background: #1e40af;
      transform: translateY(-1px);
    }
  }

  .btn-secondary {
    background: #f8fafc;
    color: #64748b;

    &:hover:not(:disabled) {
      background: #e2e8f0;
      color: #0d0f21;
    }
  }

  /* Settings Dropdown Styles */
  .settings-dropdown-container {
    position: relative;
  }

  .settings-trigger {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: auto;
    padding: 16px 20px;

    .provider-label {
      font-size: 14px;
      font-weight: 500;
    }
  }

  .settings-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    margin-top: 8px;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.08), 0 10px 10px -5px rgba(15, 23, 42, 0.04);
    min-width: 280px;
    max-width: 320px;
    z-index: 1000;
    overflow: hidden;
  }

  .dropdown-section {
    padding: 16px;
    border-bottom: 1px solid #f1f5f9;

    &:last-child {
      border-bottom: none;
    }
  }

  .dropdown-header {
    font-size: 14px;
    font-weight: 600;
    color: #0d0f21;
    margin-bottom: 12px;
  }

  .dropdown-options {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .dropdown-option {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px;
    border: none;
    background: transparent;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    text-align: left;

    &:hover {
      background: #f8fafc;
    }

    &.active {
      background: #e9e5ff;
      color: #2e44ff;
    }

    .option-name {
      font-size: 14px;
      font-weight: 500;
    }

    .checkmark {
      color: #2e44ff;
      font-weight: 600;
    }
  }

  .status-info {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .status-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
  }

  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    
    &.connected {
      background-color: #10b981;
    }
    
    &.disconnected {
      background-color: #ef4444;
    }
  }

  .settings-overlay {
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
  }

  .settings-modal {
    background: var(--c-bg-primary);
    border-radius: 12px;
    box-shadow: 0 20px 25px -5px var(--c-shadow);
    max-width: 500px;
    width: 100%;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .settings-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 24px 32px;
    border-bottom: 1px solid var(--c-border);

    h2 {
      font-size: 20px;
      font-weight: 600;
      color: var(--c-text-primary);
      margin: 0;
    }
  }

  .settings-content {
    flex: 1;
    padding: 24px 32px;
    overflow-y: auto;
  }

  .provider-section, .model-section, .connection-section, .agents-info {
    margin-bottom: 32px;

    h3 {
      font-size: 16px;
      font-weight: 600;
      color: var(--c-text-primary);
      margin: 0 0 16px 0;
    }
  }

  .provider-options {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .provider-option {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    border: 2px solid var(--c-border);
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      border-color: var(--c-action-primary);
    }

    input[type="radio"] {
      margin: 0;
    }

    .provider-name {
      font-weight: 500;
      color: var(--c-text-primary);
    }
  }

  .model-select {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid var(--c-border);
    border-radius: 8px;
    font-size: 15px;
    font-family: inherit;
    background: var(--c-bg-primary);
    color: var(--c-text-primary);

    &:focus {
      outline: none;
      border-color: var(--c-action-primary);
    }
  }

  .status-info {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .api-status, .google-status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    color: var(--c-text-secondary);
  }

  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;

    &.connected {
      background: #10b981;
    }

    &.disconnected {
      background: #ef4444;
    }
  }

  .agents-list {
    background: var(--c-bg-secondary);
    border-radius: 12px;
    padding: 20px;

    p {
      font-size: 14px;
      color: var(--c-text-primary);
      margin: 0 0 12px 0;
    }

    ul {
      margin: 0;
      padding-left: 20px;

      li {
        color: var(--c-text-secondary);
        margin: 8px 0;
        font-size: 14px;
      }
    }
  }

  @media (max-width: 768px) {
    padding: 10px;

    .modal {
      max-height: 95vh;
    }

    .modal-header, .modal-footer {
      padding: 16px 20px;
    }

    .messages-container {
      padding: 16px 20px;
    }

    .message {
      max-width: 95%;
    }

    .input-area {
      flex-direction: column;
      gap: 8px;

      .message-input {
        min-height: 48px;
      }

      .btn-primary {
        align-self: flex-end;
        min-width: auto;
        padding: 12px 24px;
      }
    }
  }
`;

export default HITLChat;
