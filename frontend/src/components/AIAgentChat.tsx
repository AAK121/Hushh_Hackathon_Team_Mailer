import React, { useState, useRef, useEffect } from 'react';
import { CSSTransition } from 'react-transition-group';
import { 
  PaperAirplaneIcon, 
  SparklesIcon, 
  UserIcon, 
  CpuChipIcon,
  ClockIcon,
  CheckIcon,
  XMarkIcon,
  Bars3Icon,
  CalendarIcon,
  DocumentTextIcon,
  ChatBubbleLeftRightIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import { hushMcpApi } from '../services/hushMcpApi';
import GlowButton from './GlowButton';

interface Message {
  id: string;
  content: string;
  type: 'user' | 'agent';
  timestamp: Date;
  status?: 'sending' | 'sent' | 'error';
}

interface AIAgentChatProps {
  emailContent?: string;
  onEmailUpdate?: (content: string) => void;
  onClose?: () => void;
  isOpen: boolean;
  onAgentSwitch?: (agent: 'mass-mail' | 'calendar' | 'email-assistant') => void;
}

const AIAgentChat: React.FC<AIAgentChatProps> = ({ 
  emailContent = '', 
  onEmailUpdate, 
  onClose, 
  isOpen,
  onAgentSwitch 
}) => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [promptTransition, setPromptTransition] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [currentEmailDraft, setCurrentEmailDraft] = useState(emailContent);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    setCurrentEmailDraft(emailContent);
  }, [emailContent]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Start transition animation for prompt textbox
    setPromptTransition(true);

    if (!user) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Please sign in to use the AI email assistant.',
        type: 'agent',
        timestamp: new Date(),
        status: 'error'
      };
      setMessages(prev => [...prev, errorMessage]);
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      type: 'user',
      timestamp: new Date(),
      status: 'sent'
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Create consent tokens for email assistance using authenticated user
      // This follows the same pattern as MassMail component for proper authorization
      const consentTokens = await hushMcpApi.createMailerPandaTokens(user.id);
      
      // Call the MailerPanda execute endpoint with proper authentication
      // Using the same service as MassMail but in interactive mode for email assistance
      const response = await hushMcpApi.executeMailerPanda({
        user_id: user.id,
        user_input: input,
        mode: 'interactive',
        consent_tokens: consentTokens,
        sender_email: user.email || '',
        recipient_emails: [],
        require_approval: false,
        use_ai_generation: true,
        body: currentEmailDraft,
      });

      // Extract the AI response and any updated email content
      let agentResponse: string;
      
      if (response.status === 'error') {
        agentResponse = response.errors?.join(', ') || 'I encountered an error processing your request.';
      } else if (response.status === 'awaiting_approval') {
        agentResponse = 'Your request is being processed and requires approval.';
      } else {
        agentResponse = response.email_template?.body || 'I\'ve processed your request but couldn\'t generate content.';
      }
      
      const updatedEmail = response.email_template?.body || currentEmailDraft;

      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: agentResponse,
        type: 'agent',
        timestamp: new Date(),
        status: 'sent'
      };

      setMessages(prev => [...prev, agentMessage]);
      
      // Update email draft if content changed
      if (updatedEmail !== currentEmailDraft) {
        setCurrentEmailDraft(updatedEmail);
      }

    } catch (error) {
      console.error('AI Agent Error:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, I encountered an error. Please try again.',
        type: 'agent',
        timestamp: new Date(),
        status: 'error'
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Reset transition after animation completes
  useEffect(() => {
    if (promptTransition) {
      const timeout = setTimeout(() => setPromptTransition(false), 500);
      return () => clearTimeout(timeout);
    }
  }, [promptTransition]);

  const applyEmailChanges = () => {
    if (onEmailUpdate) {
      onEmailUpdate(currentEmailDraft);
    }
    if (onClose) {
      onClose();
    }
  };

  const discardChanges = () => {
    setCurrentEmailDraft(emailContent);
    if (onClose) {
      onClose();
    }
  };

  const quickPrompts = [
    'Make this email more professional',
    'Make it more concise',
    'Add a call to action',
    'Make it more friendly',
    'Fix grammar and spelling',
    'Translate to formal tone'
  ];

  const availableAgents = [
    {
      id: 'email-assistant' as const,
      name: 'AI Email Assistant',
      description: 'Human-in-the-loop email optimization',
      icon: SparklesIcon,
      gradient: 'from-purple-600 to-blue-600',
      isActive: true
    },
    {
      id: 'mass-mail' as const,
      name: 'Mass Mailing Agent',
      description: 'Create bulk email campaigns',
      icon: DocumentTextIcon,
      gradient: 'from-green-500 to-green-700',
      isActive: false
    },
    {
      id: 'calendar' as const,
      name: 'AI Calendar Agent',
      description: 'Smart calendar management',
      icon: CalendarIcon,
      gradient: 'from-purple-500 to-purple-700',
      isActive: false
    }
  ];

  const handleAgentSwitch = (agentId: 'mass-mail' | 'calendar' | 'email-assistant') => {
    setIsSidebarOpen(false);
    if (onAgentSwitch && agentId !== 'email-assistant') {
      onAgentSwitch(agentId);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="bg-slate-800/80 backdrop-blur-sm border-t border-slate-600/50 flex flex-col h-96 relative">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-slate-600/50">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsSidebarOpen(true)}
            className="w-8 h-8 bg-slate-700/60 hover:bg-slate-600/60 rounded-lg flex items-center justify-center transition-colors group"
            title="Switch Agent"
          >
            <Bars3Icon className="w-5 h-5 text-white/70 group-hover:text-white transition-colors" />
          </button>
          <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full flex items-center justify-center">
            <SparklesIcon className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-white font-medium text-sm">AI Email Assistant</h2>
            <p className="text-white/70 text-xs">Human-in-the-loop email optimization</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-white/60 hover:text-white transition-colors"
        >
          <XMarkIcon className="w-5 h-5" />
        </button>
      </div>

      {/* Agent Selection Sidebar */}
      {isSidebarOpen && (
        <div className="fixed inset-0 z-50 flex" style={{ zIndex: 9999 }}>
          {/* Backdrop */}
          <div 
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={() => setIsSidebarOpen(false)}
          />
          
          {/* Sidebar */}
          <div className="relative w-80 bg-slate-800/95 backdrop-blur-lg border-r border-slate-600/50 flex flex-col shadow-2xl">
            {/* Sidebar Header */}
            <div className="flex items-center justify-between p-4 border-b border-slate-600/50">
              <div className="flex items-center gap-2">
                <ChatBubbleLeftRightIcon className="w-6 h-6 text-purple-400" />
                <h3 className="text-white font-semibold">Switch Agent</h3>
              </div>
              <button
                onClick={() => setIsSidebarOpen(false)}
                className="w-8 h-8 bg-slate-700/60 hover:bg-slate-600/60 rounded-lg flex items-center justify-center transition-colors"
              >
                <XMarkIcon className="w-4 h-4 text-white/70" />
              </button>
            </div>

            {/* Agent List */}
            <div className="flex-1 p-4 space-y-3">
              <p className="text-white/60 text-sm mb-4">Choose an AI agent to help you:</p>
              
              {availableAgents.map((agent) => {
                const IconComponent = agent.icon;
                return (
                  <button
                    key={agent.id}
                    onClick={() => handleAgentSwitch(agent.id)}
                    className={`w-full p-4 rounded-lg border transition-all duration-200 text-left group ${
                      agent.isActive 
                        ? 'bg-gradient-to-r from-purple-600/20 to-blue-600/20 border-purple-500/50 ring-1 ring-purple-500/30' 
                        : 'bg-slate-700/40 border-slate-600/50 hover:bg-slate-600/40 hover:border-slate-500/50'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`w-10 h-10 rounded-lg bg-gradient-to-r ${agent.gradient} flex items-center justify-center transition-transform group-hover:scale-105`}>
                        <IconComponent className="w-5 h-5 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <h4 className="text-white font-medium text-sm">{agent.name}</h4>
                          {agent.isActive && (
                            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                          )}
                        </div>
                        <p className="text-white/60 text-xs mt-1 leading-relaxed">{agent.description}</p>
                      </div>
                      {!agent.isActive && (
                        <div className="w-5 h-5 text-white/40 group-hover:text-white/60 transition-colors">
                          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </div>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Sidebar Footer */}
            <div className="p-4 border-t border-slate-600/50">
              <div className="text-center text-white/50 text-xs">
                <p>🤖 Powered by HushMCP</p>
                <p className="mt-1">Multi-AI Provider Support</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="flex-1 flex">
        {/* Chat Section */}
        <div className="flex-1 flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3 max-h-48">
            {messages.length === 0 && (
              <div className="text-center text-white/60 py-4">
                <CpuChipIcon className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Start a conversation with your AI assistant</p>
                <p className="text-xs mt-1">Ask me to improve your email, change the tone, or make suggestions!</p>
              </div>
            )}

            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-2 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {message.type === 'agent' && (
                  <div className="w-6 h-6 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                    <CpuChipIcon className="w-3 h-3 text-white" />
                  </div>
                )}
                
                <div
                  className={`max-w-xs px-3 py-2 rounded-lg text-sm ${
                    message.type === 'user'
                      ? 'bg-blue-600 text-white'
                      : message.status === 'error'
                      ? 'bg-red-500/20 text-red-200 border border-red-500/30'
                      : 'bg-slate-700/80 text-white border border-slate-600/50'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>
                  <div className="flex items-center gap-1 mt-1 opacity-60">
                    <ClockIcon className="w-3 h-3" />
                    <span className="text-xs">
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </div>

                {message.type === 'user' && (
                  <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-full flex items-center justify-center flex-shrink-0">
                    <UserIcon className="w-4 h-4 text-white" />
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="flex gap-2 justify-start">
                <div className="w-6 h-6 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full flex items-center justify-center">
                  <CpuChipIcon className="w-3 h-3 text-white" />
                </div>
                <div className="bg-slate-700/80 text-white border border-slate-600/50 px-3 py-2 rounded-lg">
                  <div className="flex items-center gap-1">
                    <div className="w-1.5 h-1.5 bg-white rounded-full animate-pulse"></div>
                    <div className="w-1.5 h-1.5 bg-white rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-1.5 h-1.5 bg-white rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Prompts */}
          <div className="p-3 border-t border-slate-600/50">
            <p className="text-white/70 text-xs mb-2">Quick suggestions:</p>
            <div className="flex flex-wrap gap-1">
              {quickPrompts.map((prompt, index) => (
                <button
                  key={index}
                  onClick={() => setInput(prompt)}
                  className="px-2 py-1 bg-slate-700/60 hover:bg-slate-600/60 text-white/80 hover:text-white text-xs rounded-md transition-colors border border-slate-600/50"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>

          {/* Input with animated transition */}
          <div className="p-3 border-t border-slate-600/50">
            <CSSTransition
              in={!promptTransition}
              timeout={500}
              classNames="prompt-move"
              unmountOnExit={false}
            >
              <div className="flex gap-2 prompt-move-container">
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me to improve your email..."
                  className="flex-1 bg-slate-700/60 border border-slate-600/50 rounded-lg px-3 py-2 text-black placeholder:text-black/50 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                  rows={2}
                />
                <GlowButton
                  onClick={sendMessage}
                  disabled={!input.trim() || isLoading}
                  className="glow-button--purple px-3"
                >
                  <PaperAirplaneIcon className="w-4 h-4" />
                </GlowButton>
              </div>
            </CSSTransition>
            {/* Animated moved prompt */}
            <CSSTransition
              in={promptTransition}
              timeout={500}
              classNames="prompt-move"
              unmountOnExit
            >
              <div className="flex gap-2 prompt-move-container prompt-move-up">
                <textarea
                  value={input}
                  readOnly
                  className="flex-1 bg-slate-700/60 border border-slate-600/50 rounded-lg px-3 py-2 text-black placeholder:text-black/50 resize-none text-sm opacity-80"
                  rows={2}
                />
                <GlowButton disabled className="glow-button--purple px-3 opacity-60">
                  <PaperAirplaneIcon className="w-4 h-4" />
                </GlowButton>
              </div>
            </CSSTransition>
          </div>
        </div>

        {/* Bottom Actions */}
        <div className="p-3 border-t border-slate-600/50 flex gap-2">
          <button
            onClick={discardChanges}
            className="flex-1 px-3 py-2 border border-slate-500/50 text-white rounded-lg hover:bg-slate-700/50 transition-colors text-sm"
          >
            Cancel
          </button>
          <GlowButton
            onClick={applyEmailChanges}
            className="flex-1 glow-button--emerald text-sm"
          >
            <CheckIcon className="w-4 h-4" />
            Apply Changes
          </GlowButton>
        </div>
      </div>
    </div>
  );
};

// Add CSS for sidebar and prompt transitions
const style = document.createElement('style');
style.innerHTML = `
.sidebar-enter {
  opacity: 0;
}
.sidebar-enter-active {
  opacity: 1;
  transition: opacity 300ms ease-in-out;
}
.sidebar-exit {
  opacity: 1;
}
.sidebar-exit-active {
  opacity: 0;
  transition: opacity 300ms ease-in-out;
}

.sidebar-enter .relative {
  transform: translateX(-100%);
}
.sidebar-enter-active .relative {
  transform: translateX(0);
  transition: transform 300ms ease-in-out;
}
.sidebar-exit .relative {
  transform: translateX(0);
}
.sidebar-exit-active .relative {
  transform: translateX(-100%);
  transition: transform 300ms ease-in-out;
}

.prompt-move-enter {
  opacity: 0;
  transform: translateY(32px);
}
.prompt-move-enter-active {
  opacity: 1;
  transform: translateY(0);
  transition: opacity 0.5s, transform 0.5s;
}
.prompt-move-exit {
  opacity: 1;
  transform: translateY(0);
}
.prompt-move-exit-active {
  opacity: 0;
  transform: translateY(-32px);
  transition: opacity 0.5s, transform 0.5s;
}
.prompt-move-up {
  opacity: 1;
  transform: translateY(-48px);
  transition: opacity 0.5s, transform 0.5s;
}
`;
document.head.appendChild(style);

export default AIAgentChat;
