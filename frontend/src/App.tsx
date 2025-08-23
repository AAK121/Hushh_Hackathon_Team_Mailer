import { useState } from 'react';
import SignIn from './components/SignIn';
import AIAgentSelection from './components/AIAgentSelection';
import HITLChat from './components/HITLChat';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import './App.css';

import AICalendarAgent from './components/AICalendarAgent';
import AgentStore from './components/AgentStore';
import MailerPandaAgent from './components/MailerPandaAgent';
import AddToCalendarAgent from './components/AddToCalendarAgent';
import FinanceAgent from './components/FinanceAgent';
import RelationshipAgent from './components/RelationshipAgent';
import ResearchAgent from './components/ResearchAgent';

function AppContent() {
  const { user, loading: authLoading } = useAuth();
  const [activeView, setActiveView] = useState('ai-agents');
  const [selectedAIAgent, setSelectedAIAgent] = useState<'calendar' | null>(null);
  const [selectedStoreAgent, setSelectedStoreAgent] = useState<string | null>(null);
  const [showHITL, setShowHITL] = useState(false);
  const [hitlPrompt, setHitlPrompt] = useState('');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const handleSelectAIAgent = (agent: 'calendar') => {
    setSelectedAIAgent(agent);
  };

  const handleSendToHITL = (message: string, _context?: any) => {
    setHitlPrompt(message);
    setShowHITL(true);
    setActiveView('ai-agents');
    setSelectedAIAgent(null);
    setSelectedStoreAgent(null);
    setIsSidebarOpen(false);
  };

  const handleShowHITL = (prompt: string) => {
    handleSendToHITL(prompt);
  };

  const handleBackToAgentSelection = () => {
    setSelectedAIAgent(null);
    setShowHITL(false);
    setHitlPrompt('');
    setSelectedStoreAgent(null);
    setActiveView('ai-agents');
  };

  const handleViewChange = (view: string) => {
    setActiveView(view);
    setIsSidebarOpen(false);
    // Reset all states when changing views
    setSelectedAIAgent(null);
    setSelectedStoreAgent(null);
    setShowHITL(false);
    setHitlPrompt('');
  };

  const handleAgentStoreSelection = (agentId: string) => {
    setSelectedStoreAgent(agentId);
    setActiveView('selected-agent');
  };

  const handleBackToAgentStore = () => {
    setSelectedStoreAgent(null);
    setActiveView('agent-store');
  };

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <SignIn />;
  }

  return (
    <div className="min-h-screen flex relative overflow-hidden bg-white">
      {/* Modern Menu Toggle with Label */}
      <div className="menu-toggle-wrapper">
        <span className="menu-label">Menu</span>
        <div className="toggle-wrapper">
          <input 
            className="toggle-checkbox" 
            type="checkbox"
            checked={isSidebarOpen}
            onChange={() => setIsSidebarOpen(!isSidebarOpen)}
            aria-label="Toggle menu"
          />
          <div className="toggle-container">  
            <div className="toggle-button">
              <div className="toggle-button-circles-container">
                <div className="toggle-button-circle"></div>
                <div className="toggle-button-circle"></div>
                <div className="toggle-button-circle"></div>
                <div className="toggle-button-circle"></div>
                <div className="toggle-button-circle"></div>
                <div className="toggle-button-circle"></div>
                <div className="toggle-button-circle"></div>
                <div className="toggle-button-circle"></div>
                <div className="toggle-button-circle"></div>
                <div className="toggle-button-circle"></div>
                <div className="toggle-button-circle"></div>
                <div className="toggle-button-circle"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Sidebar */}
      <div className={`sidebar ${isSidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-content">
          <div className="sidebar-header">
            <h2 className="sidebar-title">Personal Agent Stack</h2>
            <p className="sidebar-subtitle">AI Agent Platform</p>
          </div>

          <nav className="sidebar-nav">
            {[
              { label: 'Agent Selection', action: () => handleViewChange('ai-agents'), icon: '🤖' },
              { label: 'Agent Store', action: () => handleViewChange('agent-store'), icon: '🏪' },

              { label: 'MailerPanda Agent', action: () => handleAgentStoreSelection('agent_mailerpanda'), icon: '🐼' },
              { label: 'AI Calendar Agent', action: () => handleViewChange('ai-calendar'), icon: '📅' },
              { label: 'Finance Manager', action: () => handleAgentStoreSelection('agent_finance'), icon: '💰' },
              { label: 'Relationship Manager', action: () => handleAgentStoreSelection('agent_relationship'), icon: '🤝' },
              { label: 'Research Assistant', action: () => handleAgentStoreSelection('agent_research'), icon: '🔬' },
              { label: 'HITL Chat', action: () => handleShowHITL('Start a conversation'), icon: '💬' },
              { label: 'Settings', action: () => {}, icon: '⚙️' }
            ].map((item, index) => (
              <button
                key={item.label}
                onClick={() => {
                  item.action();
                  setIsSidebarOpen(false);
                }}
                className="sidebar-item"
                style={{ '--delay': `${index * 0.1}s` } as React.CSSProperties}
              >
                <span className="sidebar-item-icon">{item.icon}</span>
                <span>{item.label}</span>
              </button>
            ))}
          </nav>

          <div className="sidebar-user">
            <div className="user-avatar">
              {user?.email?.charAt(0).toUpperCase()}
            </div>
            <div className="user-info">
              <div className="user-email">{user?.email}</div>
              <div className="user-role">Platform User</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className={`main-content ${isSidebarOpen ? 'content-shifted' : ''}`}>
        {activeView === 'ai-agents' ? (
          showHITL ? (
            <HITLChat onBack={handleBackToAgentSelection} initialPrompt={hitlPrompt} />
          ) : selectedAIAgent === null ? (
            <AIAgentSelection onSelectAgent={handleSelectAIAgent} onShowHITL={handleShowHITL} />
          ) : selectedAIAgent === 'calendar' ? (
            <AICalendarAgent onBack={handleBackToAgentSelection} />
          ) : null
        ) : activeView === 'ai-calendar' ? (
          <AICalendarAgent onBack={() => handleViewChange('ai-agents')} />
        ) : activeView === 'agent-store' ? (
          <AgentStore 
            onBack={() => handleViewChange('ai-agents')} 
            onSelectAgent={handleAgentStoreSelection}
          />
        ) : activeView === 'selected-agent' ? (
          selectedStoreAgent === 'agent_mailerpanda' ? (
            <MailerPandaAgent onBack={handleBackToAgentStore} />
          ) : selectedStoreAgent === 'agent_addtocalendar' ? (
            <AddToCalendarAgent onBack={handleBackToAgentStore} />
          ) : selectedStoreAgent === 'agent_finance' ? (
            <FinanceAgent onBack={handleBackToAgentStore} onSendToHITL={handleSendToHITL} />
          ) : selectedStoreAgent === 'agent_relationship' ? (
            <RelationshipAgent onBack={handleBackToAgentStore} onSendToHITL={handleSendToHITL} />
          ) : selectedStoreAgent === 'agent_research' ? (
            <ResearchAgent onBack={handleBackToAgentStore} onSendToHITL={handleSendToHITL} />
          ) : (
            <div style={{ padding: '2rem', textAlign: 'center' }}>
              <h2>Agent not implemented yet</h2>
              <p>Selected agent: {selectedStoreAgent}</p>
              <button onClick={handleBackToAgentStore}>Back to Agent Store</button>
            </div>
          )
        ) : null}
      </div>

      {/* CSS Styles */}
      <style>{`
        .menu-toggle-wrapper {
          position: fixed;
          top: 2rem;
          left: 2rem;
          z-index: 1001;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0.5rem;
        }

        .menu-label {
          font-size: 0.875rem;
          font-weight: 500;
          color: ${isSidebarOpen ? '#000000' : (activeView === 'ai-agents' && !showHITL) ? '#ffffff' : activeView === 'ai-calendar' ? '#ffffff' : activeView === 'agent-store' ? '#ffffff' : showHITL ? '#000000' : '#333333'};
          transition: color 0.3s ease-in-out;
        }

        .toggle-wrapper {
          display: flex;
          justify-content: center;
          align-items: center;
          position: relative;
          border-radius: .5em;
          padding: .125em;
          background-image: linear-gradient(to bottom, #d5d5d5, #e8e8e8);
          box-shadow: 0 1px 1px rgb(255 255 255 / .6);
          font-size: 1.5em;
        }

        .toggle-checkbox {
          appearance: none;
          position: absolute;
          z-index: 1;
          border-radius: inherit;
          width: 100%;
          height: 100%;
          font: inherit;
          opacity: 0;
          cursor: pointer;
        }

        .toggle-container {
          display: flex;
          align-items: center;
          position: relative;
          border-radius: .375em;
          width: 3em;
          height: 1.5em;
          background-color: #e8e8e8;
          box-shadow: inset 0 0 .0625em .125em rgb(255 255 255 / .2), inset 0 .0625em .125em rgb(0 0 0 / .4);
          transition: background-color .4s linear;
        }

        .toggle-checkbox:checked + .toggle-container {
          background-color: #f3b519;
        }

        .toggle-button {
          display: flex;
          justify-content: center;
          align-items: center;
          position: absolute;
          left: .0625em;
          border-radius: .3125em;
          width: 1.375em;
          height: 1.375em;
          background-color: #e8e8e8;
          box-shadow: inset 0 -.0625em .0625em .125em rgb(0 0 0 / .1), inset 0 -.125em .0625em rgb(0 0 0 / .2), inset 0 .1875em .0625em rgb(255 255 255 / .3), 0 .125em .125em rgb(0 0 0 / .5);
          transition: left .4s;
        }

        .toggle-checkbox:checked + .toggle-container > .toggle-button {
          left: 1.5625em;
        }

        .toggle-button-circles-container {
          display: grid;
          grid-template-columns: repeat(3, min-content);
          gap: .125em;
          position: absolute;
          margin: 0 auto;
        }

        .toggle-button-circle {
          border-radius: 50%;
          width: .125em;
          height: .125em;
          background-image: radial-gradient(circle at 50% 0, #f5f5f5, #c4c4c4);
        }

        .sidebar {
          position: fixed;
          top: 0;
          left: 0;
          width: 20rem;
          height: 100vh;
          background: linear-gradient(135deg, #ffffff, #f8f9fa);
          box-shadow: 2px 0 20px rgba(0, 0, 0, 0.1);
          transform: translateX(-100%);
          transition: transform 0.3s ease-in-out;
          z-index: 999;
        }

        .sidebar-open {
          transform: translateX(0);
        }

        .sidebar-content {
          padding: 6rem 2rem 2rem;
          height: 100%;
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }

        .sidebar-header {
          margin-bottom: 2rem;
          flex-shrink: 0;
        }

        .sidebar-title {
          font-size: 1.5rem;
          font-weight: bold;
          color: #333;
          margin-bottom: 0.5rem;
        }

        .sidebar-subtitle {
          color: #666;
          font-size: 0.875rem;
        }

        .sidebar-nav {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          overflow-y: auto;
          overflow-x: hidden;
          padding-right: 0.5rem;
          margin-right: -0.5rem;
        }

        .sidebar-nav::-webkit-scrollbar {
          width: 6px;
        }

        .sidebar-nav::-webkit-scrollbar-track {
          background: rgba(0, 0, 0, 0.1);
          border-radius: 3px;
        }

        .sidebar-nav::-webkit-scrollbar-thumb {
          background: rgba(0, 0, 0, 0.3);
          border-radius: 3px;
        }

        .sidebar-nav::-webkit-scrollbar-thumb:hover {
          background: rgba(0, 0, 0, 0.5);
        }

        .sidebar-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.875rem 1rem;
          background: transparent;
          border: none;
          border-radius: 0.5rem;
          color: #333;
          font-size: 1rem;
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          text-align: left;
          width: 100%;
          cursor: pointer;
          transition: all 0.2s ease;
          opacity: 0;
          transform: translateX(-1rem);
          animation: slideIn 0.3s ease forwards;
          animation-delay: var(--delay);
        }

        .sidebar-item:hover {
          background: #f0f0f0;
          transform: translateX(0) scale(1.02);
        }

        .sidebar-item-icon {
          font-size: 1.125rem;
        }

        .sidebar-user {
          display: flex;
          align-items: center;
          padding: 1.5rem 2rem;
          border-top: 1px solid #e5e5e5;
          margin-top: auto;
          box-sizing: border-box;
          width: 100%;
          background: transparent;
          flex-shrink: 0;
        }

        .user-avatar {
          width: 2.5rem;
          height: 2.5rem;
          border-radius: 50%;
          background: linear-gradient(135deg, #ffc901, #ff7900);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-weight: bold;
          flex-shrink: 0;
          margin-right: 0.5rem;
          font-size: 1rem;
        }

        .user-info {
          flex: 1;
          overflow: hidden;
        }

        .user-email {
          font-size: 0.875rem;
          font-weight: 500;
          color: #333;
          margin: 0 0 0.25rem 0;
          padding: 0;
          line-height: 1.2;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .user-role {
          font-size: 0.75rem;
          color: #666;
          margin: 0;
          padding: 0;
          line-height: 1.2;
        }

        .main-content {
          flex: 1;
          transition: margin-left 0.3s ease-in-out;
          min-height: 100vh;
        }

        .content-shifted {
          margin-left: 20rem;
        }

        @keyframes slideIn {
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
      `}</style>
    </div>
  );
}

  function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
