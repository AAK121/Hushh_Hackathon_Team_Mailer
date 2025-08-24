import React from 'react';
import './ResearchAgentNew.css';

const ResearchAgentNew: React.FC = () => {
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
              />
              <button id="searchBtn" className="search-btn">
                <i className="fas fa-search"></i>
              </button>
            </div>
            <div className="paper-selector">
              <select id="paperDropdown" className="paper-dropdown" disabled>
                <option value="">Select a paper...</option>
              </select>
              <button id="analyzeBtn" className="analyze-btn" disabled>
                <i className="fas fa-brain"></i> Analyze Paper
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="main-content">
        <div className="panel-container">
          {/* Left Panel: Paper Display */}
          <section className="left-panel paper-panel">
            <div className="panel-header">
              <h2><i className="fas fa-file-pdf"></i> Paper Viewer</h2>
              <div className="paper-controls">
                <button id="downloadBtn" className="control-btn" disabled>
                  <i className="fas fa-download"></i> Download PDF
                </button>
                <button id="summaryBtn" className="control-btn" disabled>
                  <i className="fas fa-magic"></i> Generate Summary
                </button>
                <div className="view-toggle">
                  <button id="abstractViewBtn" className="toggle-btn active">Abstract</button>
                  <button id="fullViewBtn" className="toggle-btn">Full Text</button>
                  <button id="pdfViewBtn" className="toggle-btn">PDF View</button>
                </div>
              </div>
            </div>
            <div className="panel-content">
              <div id="paperViewer" className="paper-viewer">
                <div className="empty-state">
                  <i className="fas fa-file-pdf fa-3x"></i>
                  <h3>No Paper Selected</h3>
                  <p>Search for papers and select one from the dropdown to view it here</p>
                </div>
              </div>
            </div>
          </section>

          {/* Resizable Divider */}
          <div className="panel-divider" id="panelDivider"></div>

          {/* Right Panel: AI Agent & Notes */}
          <section className="right-panel agent-panel">
            <div className="panel-header">
              <h2><i className="fas fa-robot"></i> AI Research Assistant</h2>
              <div className="agent-controls">
                <div className="notes-selector">
                  <select id="notesDropdown" className="notes-dropdown">
                    <option value="current">Current Session</option>
                  </select>
                  <button id="newNotesBtn" className="control-btn">
                    <i className="fas fa-plus"></i> New Notes
                  </button>
                  <button id="saveNotesBtn" className="control-btn">
                    <i className="fas fa-save"></i> Save
                  </button>
                  <button id="analysisMenuBtn" className="control-btn analysis-menu-btn">
                    <i className="fas fa-brain"></i> Analysis Menu
                  </button>
                </div>
              </div>
            </div>
            <div className="panel-content">
              {/* Chat Interface */}
              <div className="chat-section">
                <div id="chatMessages" className="chat-messages">
                  {/* Welcome state will be dynamically inserted here */}
                </div>
                <div className="chat-input-container">
                  <div className="chat-input">
                    <textarea 
                      id="chatInput" 
                      placeholder="Ask me about the paper, request explanations, or ask for specific notes..."
                      rows={1}
                    />
                    <button id="sendChatBtn" className="send-btn">
                      <i className="fas fa-paper-plane"></i>
                    </button>
                  </div>
                  <p className="chat-bottom-info">
                    Research Agent may display inaccurate info about papers, so double-check its responses.
                    <a href="#" onClick={e => e.preventDefault()}>Your privacy and Research Apps</a>
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
          <span id="connectionStatus" className="status-item">
            <i className="fas fa-circle connected"></i> Connected
          </span>
          <span id="paperStatus" className="status-item">
            <i className="fas fa-file"></i> No paper selected
          </span>
        </div>
        <div className="status-right">
          <span id="notesStatus" className="status-item">
            <i className="fas fa-sticky-note"></i> 0 notes
          </span>
          <span id="wordCount" className="status-item">
            <i className="fas fa-font"></i> 0 words
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
      <div id="notesModal" className="modal hidden">
        <div className="modal-content">
          <div className="modal-header">
            <h3><i className="fas fa-sticky-note"></i> Create New Notes File</h3>
            <button id="closeModalBtn" className="close-btn">
              <i className="fas fa-times"></i>
            </button>
          </div>
          <div className="modal-body">
            <label htmlFor="notesName">Notes File Name:</label>
            <input type="text" id="notesName" placeholder="Enter notes file name..." />
            <div className="modal-actions">
              <button id="createNotesBtn" className="btn primary">Create</button>
              <button id="cancelModalBtn" className="btn secondary">Cancel</button>
            </div>
          </div>
        </div>
      </div>

      {/* Analysis Menu Modal */}
      <div id="analysisModal" className="modal hidden">
        <div className="modal-content analysis-modal">
          <div className="modal-header">
            <h3><i className="fas fa-brain"></i> Paper Analysis Menu</h3>
            <button id="closeAnalysisModalBtn" className="close-btn">
              <i className="fas fa-times"></i>
            </button>
          </div>
          <div className="modal-body">
            <div className="analysis-grid">
              <button className="analysis-card" data-analysis="comprehensive">
                <div className="analysis-icon">
                  <i className="fas fa-microscope"></i>
                </div>
                <h4>Comprehensive Analysis</h4>
                <p>Complete structured analysis covering all aspects of the paper</p>
              </button>
              <button className="analysis-card" data-analysis="section">
                <div className="analysis-icon">
                  <i className="fas fa-search"></i>
                </div>
                <h4>Section Analysis</h4>
                <p>Select and analyze specific sections of the paper</p>
              </button>
              <button className="analysis-card" data-analysis="notes">
                <div className="analysis-icon">
                  <i className="fas fa-edit"></i>
                </div>
                <h4>Smart Note Taking</h4>
                <p>Generate structured notes and summaries</p>
              </button>
              <button className="analysis-card" data-analysis="compare">
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

      {/* Section Selector Modal */}
      <div id="sectionModal" className="modal hidden">
        <div className="modal-content section-modal">
          <div className="modal-header">
            <h3><i className="fas fa-list"></i> Select Paper Section</h3>
            <button id="closeSectionModalBtn" className="close-btn">
              <i className="fas fa-times"></i>
            </button>
          </div>
          <div className="modal-body">
            <p>Choose a section of the paper to analyze in detail:</p>
            <div className="section-list">
              <button className="section-item" data-section="abstract">
                <i className="fas fa-file-text"></i>
                <span>Abstract</span>
              </button>
              <button className="section-item" data-section="introduction">
                <i className="fas fa-play"></i>
                <span>Introduction</span>
              </button>
              <button className="section-item" data-section="methodology">
                <i className="fas fa-cogs"></i>
                <span>Methodology</span>
              </button>
              <button className="section-item" data-section="results">
                <i className="fas fa-chart-bar"></i>
                <span>Results</span>
              </button>
              <button className="section-item" data-section="discussion">
                <i className="fas fa-comments"></i>
                <span>Discussion</span>
              </button>
              <button className="section-item" data-section="conclusion">
                <i className="fas fa-flag-checkered"></i>
                <span>Conclusion</span>
              </button>
              <button className="section-item" data-section="custom">
                <i className="fas fa-pencil-alt"></i>
                <span>Custom Selection</span>
              </button>
            </div>
            <div id="customSectionInput" className="custom-section-input hidden">
              <label htmlFor="customSectionText">Paste or type the section text:</label>
              <textarea id="customSectionText" placeholder="Paste the text you want to analyze..." rows={6}></textarea>
              <button id="analyzeCustomBtn" className="btn primary">Analyze Custom Text</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResearchAgentNew;
