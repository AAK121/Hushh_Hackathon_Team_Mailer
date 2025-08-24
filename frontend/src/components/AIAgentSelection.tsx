import React, { useState } from 'react';
import HITLChat from './HITLChat';
import styled from 'styled-components';
import { 
  CalendarIcon, 
  ChatBubbleLeftRightIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';

interface AIAgentSelectionProps {
  onSelectAgent: (agent: 'mass-mail' | 'calendar') => void;
  onShowHITL: (prompt: string) => void;
}

const AIAgentSelection: React.FC<AIAgentSelectionProps> = ({ onSelectAgent, onShowHITL }) => {
  const [prompt, setPrompt] = useState('');
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [preservedPrompt, setPreservedPrompt] = useState('');
  const [selectedAgent, setSelectedAgent] = useState<'mass-mail' | 'calendar' | null>(null);
  const [search, setSearch] = useState('');
  const [fullChatMode, setFullChatMode] = useState(false);

  const agents = [
    {
      id: 'mass-mail' as const,
      title: 'Mass Mailing Campaigns',
      description: 'Create and manage bulk email campaigns with Excel/CSV import support',
      icon: DocumentTextIcon,
      gradient: 'from-green-500 to-green-700',
      features: ['Excel/CSV import', 'Template management', 'Bulk sending', 'Campaign tracking']
    },
    {
      id: 'calendar' as const,
      title: 'AI Calendar Agent',
      description: 'Intelligent calendar management and event scheduling with Google Calendar',
      icon: CalendarIcon,
      gradient: 'from-purple-500 to-purple-700',
      features: ['Smart scheduling', 'Event extraction', 'Google Calendar sync', 'Conflict resolution']
    }
  ];

  const handleSubmitPrompt = () => {
    if (prompt.trim()) {
      setPreservedPrompt(prompt.trim());
      setIsTransitioning(true);
      
      setTimeout(() => {
        onShowHITL(prompt.trim());
        setPrompt('');
        setTimeout(() => {
          setIsTransitioning(false);
        }, 400);
      }, 400); // 400ms transition delay for animation
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmitPrompt();
    }
  };

  const handleAgentSelection = (agentId: 'mass-mail' | 'calendar') => {
    setSelectedAgent(agentId);
    setIsTransitioning(true);
    
    // Add transition delay for smooth agent selection
    setTimeout(() => {
      onSelectAgent(agentId);
    }, 300); // 300ms transition delay
  };

  return (
    <StyledWrapper>
      {fullChatMode ? (
  <div className="full-chat">
          {/* Only show chat and sidebar/menu icon in full chat mode */}
          {/* <HITLChat fullChatMode={true} onSend={() => {}} /> */}
        </div>
      ) : (
  <div className="layout">
          {/* Main Content */}
          <main className="main-content">
            <div className="chat-area">
              {/* <HITLChat onSend={() => setFullChatMode(true)} /> */}
            </div>
            <div className="agents-section">
              <div className="search-box">
                <input
                  type="text"
                  placeholder="Search agents..."
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  className="search-input"
                />
              </div>
              <div className="agents-grid">
                {agents
                  .filter(agent =>
                    agent.title.toLowerCase().includes(search.toLowerCase()) ||
                    agent.description.toLowerCase().includes(search.toLowerCase())
                  )
                  .map((agent) => {
                    const IconComponent = agent.icon;
                    return (
                      <div 
                        key={agent.id}
                        className={`agent-card agent-bubble card`}
                        onClick={() => handleAgentSelection(agent.id)}
                      >
                        <div className={`agent-icon bg-gradient-to-br ${agent.gradient}`}>
                          <IconComponent className="icon" />
                        </div>
                        <div className="agent-content">
                          <h3 className="agent-title">{agent.title}</h3>
                          <p className="agent-description">{agent.description}</p>
                          <div className="agent-features">
                            {agent.features.map((feature, index) => (
                              <span key={index} className="feature-tag">
                                {feature}
                              </span>
                            ))}
                          </div>
                        </div>
                        <div className="agent-arrow">
                          <svg className="arrow-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </div>
                      </div>
                    );
                  })}
              </div>
            </div>
          </main>
        </div>
      )}
    </StyledWrapper>
  );
};

const StyledWrapper = styled.div`
  .full-chat {
    width: 100vw;
    min-height: 100vh;
    background: #f0f4f9;
    display: flex;
    align-items: flex-start;
    justify-content: center;
  }
  width: 100vw;
  min-height: 100vh;
  background: linear-gradient(135deg, #ff9800 0%, #ff6f00 100%);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  .layout {
    display: flex;
    width: 100vw;
    min-height: 100vh;
    max-width: 1600px;
    margin: 0 auto;
    align: center;
  }
  .sidebar {
    width: 260px;
    background: linear-gradient(135deg, #ff9800 0%, #ff6f00 100%);
    border-top-right-radius: 32px;
    border-bottom-right-radius: 32px;
    box-shadow: 0 8px 32px rgba(255,152,0,0.10);
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    padding: 32px 0 32px 0;
    color: #fff;
    min-height: 100vh;
    position: relative;
  }
  .sidebar-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 0 32px 24px 32px;
  }
  .sidebar-logo {
    font-size: 2.2rem;
    background: #fff3e0;
    color: #ff9800;
    border-radius: 12px;
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 8px rgba(255,152,0,0.10);
  }
  .sidebar-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #fff;
    margin: 0;
  }
  .sidebar-nav {
    width: 100%;
    padding: 0 32px;
  }
  .sidebar-nav ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 18px;
  }
  .sidebar-nav li {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 1rem;
    font-weight: 500;
    color: #fff;
    cursor: pointer;
    transition: background 0.2s;
    border-radius: 8px;
    padding: 8px 12px;
    &:hover {
      background: rgba(255,255,255,0.08);
    }
  }
  .sidebar-icon {
    width: 20px;
    height: 20px;
    color: #fff3e0;
  }
  .main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    padding: 40px 0 0 0;
    min-width: 0;
    width: 100%;
    gap: 2.5rem;
  }
  .chat-area {
    width: 100%;
    max-width: 900px;
    margin: 0 auto;
    box-shadow: none;
    border-radius: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .agents-section {
    width: 100%;
    max-width: 1100px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.2rem;
  }
  .search-box {
    width: 100%;
    max-width: 400px;
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: center;
  }
  .search-input {
    width: 100%;
    padding: 0.7rem 1rem;
    border-radius: 12px;
    border: 1px solid #ff9800;
    font-size: 1rem;
    background: #fff3e0;
    color: #ff9800;
    outline: none;
    box-shadow: 0 2px 8px rgba(255,152,0,0.08);
    transition: border 0.2s, box-shadow 0.2s;
    &:focus {
      border: 2px solid #ff9800;
      box-shadow: 0 4px 16px rgba(255,152,0,0.12);
    }
  }
  .agents-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
    gap: 2rem;
    margin: 0 auto 0rem auto;
    max-width: 1100px;
    width: auto;
    align-items: center;
    justify-items: center;
  }
  .agent-bubble.card {
    background: linear-gradient(135deg, #fff3e0 60%, #ffe0b2 100%);
    border-radius: 24px;
    box-shadow: 0 8px 32px rgba(255,152,0,0.10);
    border: 1px solid #ff9800;
    cursor: pointer;
    transition: box-shadow 0.2s, border 0.2s, transform 0.2s;
    display: flex;
    flex-direction: column;
    align-items: left;
    position: relative;
    min-width: 340px;
    max-width: 340px;
    box-sizing: border-box;
    width: 100%;
    gap: 0.4rem;
    padding: 1.2rem 1.2rem 1rem 1.2rem;
    overflow: hidden;
    &:hover {
      box-shadow: 0 12px 32px rgba(255,152,0,0.18);
      border: 2px solid #ff9800;
      transform: translateY(-2px) scale(1.03);
    }
  }
  .agent-icon {
    width: 48px !important;
    height: 48px !important;
    margin-bottom: 0.2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #ff9800 0%, #ff6f00 100%);
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(255,152,0,0.10);
  }
  .icon {
    width: 28px !important;
    height: 28px !important;
    color: #fff3e0;
  }
  .agent-title {
    font-size: 1.15rem !important;
    margin-bottom: 0.1rem;
    font-weight: 700;
    color: #ff9800;
    line-height: 1.1;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
    width: 100%;
  }
  .agent-description {
    font-size: 0.95rem !important;
    margin-bottom: 0.1rem;
    color: #d84315;
    line-height: 1.2;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
    width: 100%;
  }
  .agent-features {
    display: flex;
    flex-wrap: wrap;
    gap: 0.2rem;
    margin-bottom: 0.1rem;
    justify-content: flex-start;
    width: 100%;
    font-size: 0.8rem !important;
    margin: 0.5rem 0;
  }
  .feature-tag {
    padding: 0.15rem 0.5rem !important;
    border-radius: 8px;
    font-size: 0.8rem !important;
    background: #ffe0b2;
    color: #ff9800;
    border: none;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
    max-width: 120px;
    font-weight: 500;
  }
  .agent-arrow {
    position: static;
    margin-top: 0.3rem;
    width: 28px;
    height: 28px;
    color: #ff9800;
    align-self: flex-end;
  }
  .arrow-icon {
    width: 100%;
    height: 100%;
    transition: transform 0.3s ease;
  }
  /* Responsive adjustments */
  @media (max-width: 1200px) {
    .sidebar {
      width: 180px;
      padding: 24px 0 24px 0;
    }
    .sidebar-header {
      padding: 0 16px 16px 16px;
    }
    .sidebar-nav {
      padding: 0 16px;
    }
    .main-content {
      padding: 24px 0 0 0;
    }
    .agents-section {
      max-width: 900px;
    }
  }
  @media (max-width: 900px) {
  .layout {
      flex-direction: column;
    }
    .sidebar {
      width: 100vw;
      min-height: 80px;
      border-radius: 0 0 32px 32px;
      flex-direction: row;
      align-items: center;
      justify-content: flex-start;
      padding: 0 16px;
      box-shadow: 0 4px 16px rgba(255,152,0,0.10);
    }
    .sidebar-header {
      padding: 0 8px 0 8px;
    }
    .sidebar-nav {
      padding: 0 8px;
    }
    .main-content {
      padding: 16px 0 0 0;
    }
    .agents-section {
      max-width: 100vw;
      padding: 0 8px;
    }
    .search-box {
      max-width: 100vw;
      padding: 0 8px;
    }
    .agents-grid {
      grid-template-columns: 1fr;
      max-width: 100vw;
      padding: 0 8px;
    }
  .agent-bubble.card {
      min-width: 90vw;
      max-width: 90vw;
    }
  }
  @media (max-width: 600px) {
    .main-content {
      padding: 8px 0 0 0;
    }
    .agents-section {
      padding: 0 4px;
    }
    .search-box {
      padding: 0 4px;
    }
    .agents-grid {
      padding: 0 4px;
    }
  .agent-bubble.card {
      min-width: 98vw;
      max-width: 98vw;
      padding: 1rem 0.5rem 0.8rem 0.5rem;
    }
  }
`;

// Add CSS for prompt transition globally
// Remove global prompt transition style injection (not needed for this UI)

export default AIAgentSelection;
