import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { 
  PaperAirplaneIcon, 
  CpuChipIcon, 
  UserIcon
} from '@heroicons/react/24/outline';

interface AIAgentSelectionProps {
  onSelectAgent: (agent: 'mass-mail' | 'calendar') => void;
  onShowHITL: (prompt: string) => void;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
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
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

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
          message: input.trim(),
          user_id: 'demo_user',
          conversation_id: 'main_chat'
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date()
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
    <StyledWrapper>
      <div className="chat-container">
        <div className="chat-header">
          <div className="header-content">
            <div className="logo">
              <CpuChipIcon className="logo-icon" />
              <h1>Hushh AI Assistant</h1>
            </div>
            <p className="subtitle">Privacy-first AI agents at your service</p>
          </div>
        </div>

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
  background: linear-gradient(135deg, #ff9800 0%, #ff6f00 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;

  .chat-container {
    width: 100%;
    max-width: 1200px;
    height: 90vh;
    background: #fff;
    border-radius: 24px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .chat-header {
    background: linear-gradient(135deg, #ff9800 0%, #ff6f00 100%);
    padding: 24px;
    color: white;
    border-radius: 24px 24px 0 0;
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
    background: #f8fafc;
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
  }

  .message.user .message-avatar {
    background: linear-gradient(135deg, #ff9800 0%, #ff6f00 100%);
  }

  .message.assistant .message-avatar {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  }

  .avatar-icon {
    width: 20px;
    height: 20px;
    color: white;
  }

  .message-content {
    background: white;
    border-radius: 16px;
    padding: 16px 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    border: 1px solid #e2e8f0;
    position: relative;
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
    background: white;
    border-top: 1px solid #e2e8f0;
  }

  .input-wrapper {
    display: flex;
    align-items: flex-end;
    gap: 12px;
    background: #f8fafc;
    border: 2px solid #e2e8f0;
    border-radius: 16px;
    padding: 12px;
    transition: border-color 0.2s;
  }

  .input-wrapper:focus-within {
    border-color: #ff9800;
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
    transition: transform 0.2s, box-shadow 0.2s;
    flex-shrink: 0;
  }

  .send-button:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(255, 152, 0, 0.3);
  }

  .send-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .send-icon {
    width: 20px;
    height: 20px;
  }

  /* Responsive Design */
  @media (max-width: 768px) {
    padding: 10px;

    .chat-container {
      height: 95vh;
      border-radius: 16px;
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

    .chat-container {
      height: 98vh;
      border-radius: 12px;
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
