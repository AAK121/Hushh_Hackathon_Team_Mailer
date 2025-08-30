import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { 
  PaperAirplaneIcon, 
  CpuChipIcon, 
  UserIcon,
  Bars3Icon,
  PlusIcon,
  QuestionMarkCircleIcon,
  ClockIcon,
  Cog6ToothIcon,
  ChatBubbleLeftRightIcon,
  LightBulbIcon,
  CodeBracketIcon,
  PhotoIcon,
  MicrophoneIcon,
  MapIcon
} from '@heroicons/react/24/outline';

interface AIAgentSelectionProps {
  onSelectAgent?: (agent: 'mass-mail' | 'calendar') => void;
  onShowHITL?: (prompt: string) => void;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatResponse {
  response: string;
  conversation_id: string;
  timestamp: string;
  session_id: string;
}

const AIAgentSelection: React.FC<AIAgentSelectionProps> = ({ onSelectAgent, onShowHITL }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: `# Welcome to Hushh AI Agent Ecosystem! 🚀

I'm your AI assistant, here to help you navigate our privacy-first AI platform with 6 specialized agents:

**🤖 Available Agents:**
- **📧 MailerPanda**: AI-powered email marketing with human oversight
- **💰 ChanduFinance**: Personal financial advisor with real-time market data  
- **🧠 Relationship Memory**: Persistent context and cross-agent memory
- **📅 AddToCalendar**: Intelligent calendar management with Google sync
- **🔍 Research Agent**: Multi-source information gathering and analysis
- **📨 Basic Mailer**: Simple email sending with Excel/CSV support

**🔐 Privacy-First Features:**
- Cryptographic consent management (HushhMCP)
- End-to-end encryption for all personal data
- User-controlled permissions for every AI action

Ask me anything about our agents, how to use them, or get started with the platform!`,
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [userId, setUserId] = useState('default_user');
  const [isMaximized, setIsMaximized] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    // Make chat interface fullscreen when sending first user message
    if (messages.length === 1) {
      setIsMaximized(true);
      setIsFullscreen(true);
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8001/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          user_id: userId,
          conversation_id: conversationId
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ChatResponse = await response.json();
      
      // Update conversation ID if this is the first message
      if (!conversationId) {
        setConversationId(data.conversation_id);
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date(data.timestamp)
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I apologize, but I\'m having trouble connecting to the server right now. Please try again in a moment.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <StyledWrapper className={isFullscreen ? 'fullscreen' : ''}>
      <div className={`chat-container ${isMaximized ? 'maximized' : ''} ${isFullscreen ? 'fullscreen' : ''}`}>
        <div className="messages-container">
          {messages.map((message) => (
            <div key={message.id} className={`message ${message.role}`}>
              <div className="message-avatar">
                {message.role === 'user' ? (
                  <UserIcon className="avatar-icon" />
                ) : (
                  <CpuChipIcon className="avatar-icon" />
                )}
              </div>
              <div className="message-content">
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm]}
                  components={{
                    h1: ({children}) => <h1 className="markdown-h1">{children}</h1>,
                    h2: ({children}) => <h2 className="markdown-h2">{children}</h2>,
                    h3: ({children}) => <h3 className="markdown-h3">{children}</h3>,
                    p: ({children}) => <p className="markdown-p">{children}</p>,
                    ul: ({children}) => <ul className="markdown-ul">{children}</ul>,
                    li: ({children}) => <li className="markdown-li">{children}</li>,
                    strong: ({children}) => <strong className="markdown-strong">{children}</strong>,
                    code: ({children}) => <code className="markdown-code">{children}</code>
                  }}
                >
                  {message.content}
                </ReactMarkdown>
                <div className="message-time">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message assistant">
              <div className="message-avatar">
                <CpuChipIcon className="avatar-icon" />
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
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <div className="input-wrapper">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask me about Hushh AI agents, their capabilities, or how to get started..."
              className="message-input"
              rows={1}
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={!input.trim() || isLoading}
              className="send-button"
            >
              <PaperAirplaneIcon className="send-icon" />
            </button>
          </div>
        </div>
      </div>
    </StyledWrapper>
  );
};

const StyledWrapper = styled.div`
  width: 100vw;
  min-height: 100vh;
  position: relative;
  overflow: hidden;

  /* Simple white background */
  background: white;

  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;

  /* Fullscreen mode removes padding and centers content */
  &.fullscreen {
    padding: 0;
    align-items: stretch;
    justify-content: stretch;
    /* Add padding to avoid menu button interference */
    padding-top: 120px; /* Space for menu button */
    padding-left: 20px;
    padding-right: 20px;
    padding-bottom: 20px;
  }

  .chat-container {
    width: 100%;
    max-width: 1200px;
    height: 85vh;
    
    /* Neuromorphic design */
    background: #f0f0f0;
    border-radius: 24px;
    
    /* Neuromorphic shadows - inset and outset for 3D effect */
    box-shadow: 
      8px 8px 16px #d1d1d1,
      -8px -8px 16px #ffffff;
    
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: relative;

    &.maximized {
      height: 95vh;
      max-width: 1400px;
      /* Enhanced neuromorphic shadows for maximized state */
      box-shadow: 
        12px 12px 24px #d1d1d1,
        -12px -12px 24px #ffffff;
    }

    /* Fullscreen mode - remove boundaries completely */
    &.fullscreen {
      width: 100%;
      height: calc(100vh - 100px); /* Adjust height to account for wrapper padding */
      max-width: none;
      border-radius: 0;
      box-shadow: none;
      background: #f0f0f0;
    }
  }

  .chat-header {
    background: linear-gradient(135deg, 
      rgba(255, 152, 0, 0.9) 0%, 
      rgba(255, 111, 0, 0.9) 100%);
    padding: 24px;
    color: white;
    border-radius: 24px 24px 0 0;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    position: relative;
    z-index: 2;

    /* Subtle inner shadow for neumorphic effect */
    box-shadow: 
      inset 0 2px 4px rgba(255, 255, 255, 0.1),
      inset 0 -2px 4px rgba(0, 0, 0, 0.1);

    /* Fullscreen mode styling */
    .chat-container.fullscreen & {
      border-radius: 0;
      border: none;
      backdrop-filter: blur(10px);
      background: linear-gradient(135deg, 
        rgba(255, 152, 0, 0.8) 0%, 
        rgba(255, 111, 0, 0.8) 100%);
    }
  }

  .header-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
  }

  .logo-icon {
    width: 32px;
    height: 32px;
    color: #fff3e0;
  }

  .logo h1 {
    font-size: 1.8rem;
    font-weight: 700;
    margin: 0;
    color: white;
  }

  .subtitle {
    font-size: 1rem;
    opacity: 0.9;
    margin: 0;
  }

  .messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    background: linear-gradient(135deg, 
      rgba(248, 250, 252, 0.8) 0%, 
      rgba(241, 245, 249, 0.8) 100%);
    backdrop-filter: blur(10px);
    position: relative;
    z-index: 1;
  }

  .message {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    max-width: 85%;
  }

  .message.user {
    align-self: flex-end;
    flex-direction: row-reverse;
  }

  .message.assistant {
    align-self: flex-start;
  }

  .message-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    transition: all 0.3s ease;

    /* Neumorphic shadow effect */
    box-shadow: 
      0 4px 8px rgba(0, 0, 0, 0.1),
      inset 0 2px 4px rgba(255, 255, 255, 0.1);
  }

  .message.user .message-avatar {
    background: linear-gradient(135deg, #ff9800 0%, #ff6f00 100%);
  }

  .message.assistant .message-avatar {
    background: linear-gradient(135deg, 
      rgba(255, 255, 255, 0.2) 0%, 
      rgba(255, 255, 255, 0.1) 100%);
  }

  .avatar-icon {
    width: 20px;
    height: 20px;
    color: white;
  }

  .message.assistant .avatar-icon {
    color: #64748b;
  }

  .message-content {
    background: linear-gradient(135deg, 
      rgba(255, 255, 255, 0.9) 0%, 
      rgba(255, 255, 255, 0.8) 100%);
    border-radius: 16px;
    padding: 16px 20px;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    position: relative;
    transition: all 0.2s ease;

    /* Subtle neumorphic shadow effect */
    box-shadow: 
      0 4px 16px rgba(0, 0, 0, 0.1),
      inset 0 1px 0 rgba(255, 255, 255, 0.2);

    &:hover {
      box-shadow: 
        0 6px 20px rgba(0, 0, 0, 0.12),
        inset 0 1px 0 rgba(255, 255, 255, 0.25);
    }
  }

  .message.user .message-content {
    background: linear-gradient(135deg, #ff9800 0%, #ff6f00 100%);
    color: white;
  }

  .message.assistant .message-content {
    background: white;
    color: #1e293b;
  }

  .message-time {
    font-size: 0.75rem;
    opacity: 0.6;
    margin-top: 8px;
    text-align: right;
  }

  .message.user .message-time {
    color: rgba(255, 255, 255, 0.8);
  }

  .message.assistant .message-time {
    color: #64748b;
  }

  /* Markdown Styling */
  .markdown-h1 {
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0 0 12px 0;
    color: inherit;
  }

  .markdown-h2 {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 16px 0 8px 0;
    color: inherit;
  }

  .markdown-h3 {
    font-size: 1.1rem;
    font-weight: 600;
    margin: 12px 0 6px 0;
    color: inherit;
  }

  .markdown-p {
    margin: 8px 0;
    line-height: 1.6;
    color: inherit;
  }

  .markdown-ul {
    margin: 8px 0;
    padding-left: 20px;
  }

  .markdown-li {
    margin: 4px 0;
    line-height: 1.5;
  }

  .markdown-strong {
    font-weight: 600;
    color: inherit;
  }

  .markdown-code {
    background: rgba(0, 0, 0, 0.08);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
  }

  .message.user .markdown-code {
    background: rgba(255, 255, 255, 0.2);
  }

  .typing-indicator {
    display: flex;
    gap: 4px;
    align-items: center;
  }

  .typing-indicator span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #94a3b8;
    animation: typing 1.4s infinite ease-in-out;
  }

  .typing-indicator span:nth-child(2) {
    animation-delay: 0.2s;
  }

  .typing-indicator span:nth-child(3) {
    animation-delay: 0.4s;
  }

  @keyframes typing {
    0%, 60%, 100% {
      transform: translateY(0);
      opacity: 0.4;
    }
    30% {
      transform: translateY(-10px);
      opacity: 1;
    }
  }

  .input-container {
    padding: 24px;
    background: linear-gradient(135deg, 
      rgba(255, 255, 255, 0.1) 0%, 
      rgba(255, 255, 255, 0.05) 100%);
    backdrop-filter: blur(20px);
    border-top: 1px solid rgba(255, 255, 255, 0.2);
    position: relative;
    z-index: 2;
  }

  .input-wrapper {
    display: flex;
    align-items: flex-end;
    gap: 12px;
    background: linear-gradient(135deg, 
      rgba(248, 250, 252, 0.9) 0%, 
      rgba(241, 245, 249, 0.9) 100%);
    backdrop-filter: blur(10px);
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 16px;
    padding: 12px;
    transition: all 0.3s ease;

    /* Neumorphic shadow effect */
    box-shadow: 
      0 4px 16px rgba(0, 0, 0, 0.1),
      inset 0 1px 0 rgba(255, 255, 255, 0.2);

    &:focus-within {
      border-color: rgba(255, 152, 0, 0.6);
      box-shadow: 
        0 6px 20px rgba(0, 0, 0, 0.15),
        0 0 0 2px rgba(255, 152, 0, 0.2),
        inset 0 1px 0 rgba(255, 255, 255, 0.3);
      /* Remove upward movement animation */
    }
  }

  .message-input {
    flex: 1;
    border: none;
    outline: none;
    background: transparent;
    resize: none;
    font-size: 1rem;
    line-height: 1.5;
    color: #1e293b;
    min-height: 24px;
    max-height: 120px;
    font-family: inherit;
  }

  .message-input::placeholder {
    color: #94a3b8;
  }

  .send-button {
    width: 40px;
    height: 40px;
    border: none;
    border-radius: 12px;
    background: linear-gradient(135deg, #ff9800 0%, #ff6f00 100%);
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    flex-shrink: 0;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    position: relative;
    overflow: hidden;

    /* Neumorphic shadow effect */
    box-shadow: 
      0 4px 12px rgba(255, 152, 0, 0.3),
      inset 0 1px 0 rgba(255, 255, 255, 0.2);

    /* Hover gradient effect */
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, 
        transparent, 
        rgba(255, 255, 255, 0.2), 
        transparent);
      transition: left 0.5s;
    }

    &:hover:not(:disabled) {
      transform: translateY(-4px);
      box-shadow: 
        0 8px 25px rgba(255, 152, 0, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.3);

      &::before {
        left: 100%;
      }
    }

    &:active:not(:disabled) {
      transform: translateY(-2px);
      transition: transform 0.1s;
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      transform: none;
      box-shadow: 
        0 2px 8px rgba(0, 0, 0, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
  }

  .send-icon {
    width: 20px;
    height: 20px;
  }

  /* Responsive Design */
  @media (max-width: 768px) {
    padding: 10px;

    &.fullscreen {
      padding-top: 70px; /* Reduced space for mobile menu button */
      padding-left: 10px;
      padding-right: 10px;
      padding-bottom: 10px;
    }

    .chat-container {
      height: 95vh;
      border-radius: 16px;
      
      &.fullscreen {
        height: calc(100vh - 80px); /* Adjust for mobile */
        border-radius: 8px; /* Keep slight border radius on mobile */
      }
    }

    .chat-header {
      padding: 16px;
      border-radius: 16px 16px 0 0;
    }

    .logo h1 {
      font-size: 1.5rem;
    }

    .messages-container {
      padding: 16px;
    }

    .message {
      max-width: 95%;
    }

    .input-container {
      padding: 16px;
    }
  }

  @media (max-width: 480px) {
    padding: 5px;

    &.fullscreen {
      padding-top: 60px; /* Even more compact for small screens */
      padding-left: 5px;
      padding-right: 5px;
      padding-bottom: 5px;
    }

    .chat-container {
      height: 98vh;
      border-radius: 12px;
      
      &.fullscreen {
        height: calc(100vh - 65px); /* Adjust for small screens */
        border-radius: 6px;
      }
    }

    .chat-header {
      padding: 12px;
    }

    .logo h1 {
      font-size: 1.3rem;
    }

    .messages-container {
      padding: 12px;
    }

    .input-container {
      padding: 12px;
    }
  }
`;

export default AIAgentSelection;
