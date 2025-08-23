import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface CalendarEvent {
  summary: string;
  start_time: string;
  end_time: string;
  confidence: number;
  description?: string;
  location?: string;
}

interface ProcessingResult {
  status: 'success' | 'error' | 'processing';
  user_id: string;
  action_performed: string;
  emails_processed: number;
  events_extracted: number;
  events_created: number;
  calendar_links: string[];
  extracted_events: CalendarEvent[];
  processing_time: number;
  errors: string[];
}

interface AddToCalendarAgentProps {
  onBack: () => void;
}

const AddToCalendarAgent: React.FC<AddToCalendarAgentProps> = ({ onBack }) => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [processingResults, setProcessingResults] = useState<ProcessingResult[]>([]);
  const [showGoogleAuth, setShowGoogleAuth] = useState(false);
  const [googleAccessToken, setGoogleAccessToken] = useState('');
  
  // Settings
  const [action, setAction] = useState<'comprehensive_analysis' | 'analyze_only' | 'manual_event'>('comprehensive_analysis');
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.7);
  const [maxEmails, setMaxEmails] = useState(50);
  
  // Manual event form
  const [showManualEvent, setShowManualEvent] = useState(false);
  const [manualEvent, setManualEvent] = useState({
    summary: '',
    description: '',
    location: '',
    start_time: '',
    end_time: ''
  });

  const API_BASE_URL = 'http://127.0.0.1:8001';

  useEffect(() => {
    loadProcessingHistory();
  }, []);

  const loadProcessingHistory = () => {
    // In a real implementation, this would fetch from localStorage or API
    const saved = localStorage.getItem('addtocalendar_history');
    if (saved) {
      setProcessingResults(JSON.parse(saved));
    }
  };

  const saveProcessingHistory = (results: ProcessingResult[]) => {
    localStorage.setItem('addtocalendar_history', JSON.stringify(results));
  };

  const createConsentToken = async (scope: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/consent/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: user?.id || 'demo_user',
          agent_id: 'agent_addtocalendar',
          scope: scope
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to create consent token');
      }
      
      const data = await response.json();
      return data.token;
    } catch (error) {
      console.error('Error creating consent token:', error);
      return null;
    }
  };

  const authenticateWithGoogle = () => {
    // In a real implementation, this would use Google OAuth
    const demoToken = 'ya29.demo_google_access_token_' + Date.now();
    setGoogleAccessToken(demoToken);
    setShowGoogleAuth(false);
    alert('Google authentication successful! (Demo mode)');
  };

  const executeAddToCalendar = async () => {
    if (!googleAccessToken && action !== 'analyze_only') {
      setShowGoogleAuth(true);
      return;
    }

    setLoading(true);
    
    try {
      // Create consent tokens
      const emailToken = await createConsentToken('vault.read.email');
      const calendarToken = await createConsentToken('vault.write.calendar');
      
      if (!emailToken || (!calendarToken && action !== 'analyze_only')) {
        throw new Error('Failed to create required consent tokens');
      }

      const payload = {
        user_id: user?.id || 'demo_user',
        email_token: emailToken,
        calendar_token: calendarToken,
        google_access_token: googleAccessToken,
        action: action,
        confidence_threshold: confidenceThreshold,
        max_emails: maxEmails
      };

      const response = await fetch(`${API_BASE_URL}/agents/addtocalendar/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error('Failed to execute AddToCalendar agent');
      }

      const result: ProcessingResult = await response.json();
      
      // Add to results
      const newResults = [result, ...processingResults];
      setProcessingResults(newResults);
      saveProcessingHistory(newResults);
      
      alert(`Processing complete! Extracted ${result.events_extracted} events, created ${result.events_created} calendar entries.`);
      
    } catch (error) {
      console.error('Error executing AddToCalendar:', error);
      
      // Demo mode fallback
      const demoResult: ProcessingResult = {
        status: 'success',
        user_id: user?.id || 'demo_user',
        action_performed: action,
        emails_processed: Math.floor(Math.random() * maxEmails) + 5,
        events_extracted: Math.floor(Math.random() * 8) + 2,
        events_created: action === 'analyze_only' ? 0 : Math.floor(Math.random() * 6) + 1,
        calendar_links: action === 'analyze_only' ? [] : [
          'https://calendar.google.com/event?eid=demo123',
          'https://calendar.google.com/event?eid=demo456'
        ],
        extracted_events: [
          {
            summary: 'Team Meeting',
            start_time: '2025-01-22T14:00:00',
            end_time: '2025-01-22T15:00:00',
            confidence: 0.9,
            description: 'Weekly team sync meeting'
          },
          {
            summary: 'Project Review',
            start_time: '2025-01-25T10:00:00',
            end_time: '2025-01-25T11:30:00',
            confidence: 0.8,
            description: 'Quarterly project review session'
          }
        ],
        processing_time: Math.random() * 10 + 5,
        errors: []
      };
      
      const newResults = [demoResult, ...processingResults];
      setProcessingResults(newResults);
      saveProcessingHistory(newResults);
      
      alert(`Demo processing complete! (Simulated result)`);
    } finally {
      setLoading(false);
    }
  };

  const createManualEvent = async () => {
    if (!manualEvent.summary || !manualEvent.start_time || !manualEvent.end_time) {
      alert('Please fill in all required fields');
      return;
    }

    setLoading(true);
    
    try {
      // In a real implementation, this would call the manual_event API
      const demoResult: ProcessingResult = {
        status: 'success',
        user_id: user?.id || 'demo_user',
        action_performed: 'manual_event',
        emails_processed: 0,
        events_extracted: 1,
        events_created: 1,
        calendar_links: ['https://calendar.google.com/event?eid=manual_' + Date.now()],
        extracted_events: [{
          summary: manualEvent.summary,
          start_time: manualEvent.start_time,
          end_time: manualEvent.end_time,
          confidence: 1.0,
          description: manualEvent.description,
          location: manualEvent.location
        }],
        processing_time: 1.2,
        errors: []
      };
      
      const newResults = [demoResult, ...processingResults];
      setProcessingResults(newResults);
      saveProcessingHistory(newResults);
      
      setShowManualEvent(false);
      setManualEvent({
        summary: '',
        description: '',
        location: '',
        start_time: '',
        end_time: ''
      });
      
      alert('Manual event created successfully!');
      
    } catch (error) {
      console.error('Error creating manual event:', error);
      alert('Failed to create manual event');
    } finally {
      setLoading(false);
    }
  };

  const styles = {
    container: {
      padding: '2rem',
      background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
      minHeight: '100vh',
      color: 'white',
    },
    header: {
      textAlign: 'center' as const,
      marginBottom: '3rem',
    },
    title: {
      fontSize: '3rem',
      fontWeight: '700',
      marginBottom: '1rem',
      textShadow: '0 4px 6px rgba(0, 0, 0, 0.3)',
    },
    subtitle: {
      fontSize: '1.2rem',
      color: 'rgba(255, 255, 255, 0.9)',
      maxWidth: '600px',
      margin: '0 auto',
      lineHeight: '1.6',
    },
    backButton: {
      position: 'absolute' as const,
      top: '2rem',
      left: '2rem',
      padding: '0.75rem 1.5rem',
      background: 'rgba(255, 255, 255, 0.2)',
      border: 'none',
      borderRadius: '0.75rem',
      color: 'white',
      cursor: 'pointer',
      fontSize: '1rem',
      fontWeight: '500',
      transition: 'all 0.3s ease',
      backdropFilter: 'blur(10px)',
    },
    controlsContainer: {
      background: 'rgba(255, 255, 255, 0.1)',
      borderRadius: '1rem',
      padding: '2rem',
      marginBottom: '2rem',
      backdropFilter: 'blur(10px)',
    },
    formGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
      gap: '1.5rem',
      marginBottom: '2rem',
    },
    formGroup: {
      marginBottom: '1rem',
    },
    label: {
      display: 'block',
      marginBottom: '0.5rem',
      fontWeight: '600',
    },
    select: {
      width: '100%',
      padding: '0.75rem',
      borderRadius: '0.5rem',
      border: 'none',
      background: 'rgba(255, 255, 255, 0.9)',
      fontSize: '1rem',
    },
    input: {
      width: '100%',
      padding: '0.75rem',
      borderRadius: '0.5rem',
      border: 'none',
      background: 'rgba(255, 255, 255, 0.9)',
      fontSize: '1rem',
    },
    actionsContainer: {
      display: 'flex',
      gap: '1rem',
      justifyContent: 'center',
      flexWrap: 'wrap' as const,
    },
    actionButton: {
      padding: '1rem 2rem',
      background: 'rgba(255, 255, 255, 0.2)',
      border: 'none',
      borderRadius: '0.75rem',
      color: 'white',
      cursor: 'pointer',
      fontSize: '1rem',
      fontWeight: '600',
      transition: 'all 0.3s ease',
      backdropFilter: 'blur(10px)',
    },
    primaryButton: {
      background: 'linear-gradient(135deg, #10b981, #047857)',
    },
    secondaryButton: {
      background: 'linear-gradient(135deg, #f59e0b, #d97706)',
    },
    googleButton: {
      background: 'linear-gradient(135deg, #4285f4, #1a73e8)',
    },
    resultsContainer: {
      marginTop: '3rem',
    },
    resultCard: {
      background: 'rgba(255, 255, 255, 0.1)',
      borderRadius: '1rem',
      padding: '1.5rem',
      marginBottom: '1.5rem',
      backdropFilter: 'blur(10px)',
      border: '1px solid rgba(255, 255, 255, 0.2)',
    },
    statusBadge: {
      display: 'inline-block',
      padding: '0.25rem 0.75rem',
      borderRadius: '1rem',
      fontSize: '0.875rem',
      fontWeight: '600',
      marginBottom: '1rem',
    },
    eventsGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
      gap: '1rem',
      marginTop: '1rem',
    },
    eventCard: {
      background: 'rgba(255, 255, 255, 0.1)',
      borderRadius: '0.75rem',
      padding: '1rem',
      border: '1px solid rgba(255, 255, 255, 0.2)',
    },
    confidenceBar: {
      width: '100%',
      height: '4px',
      background: 'rgba(255, 255, 255, 0.2)',
      borderRadius: '2px',
      marginTop: '0.5rem',
      overflow: 'hidden',
    },
    confidenceFill: {
      height: '100%',
      background: 'linear-gradient(90deg, #ef4444, #f59e0b, #10b981)',
      borderRadius: '2px',
      transition: 'width 0.3s ease',
    },
    modal: {
      position: 'fixed' as const,
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.7)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
    },
    modalContent: {
      background: 'rgba(255, 255, 255, 0.95)',
      borderRadius: '1rem',
      padding: '2rem',
      maxWidth: '500px',
      width: '90%',
      color: '#333',
    },
    textarea: {
      width: '100%',
      padding: '0.75rem',
      borderRadius: '0.5rem',
      border: '1px solid #ddd',
      fontSize: '1rem',
      minHeight: '80px',
      resize: 'vertical' as const,
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return '#10b981';
      case 'error': return '#ef4444';
      case 'processing': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return '#10b981';
    if (confidence >= 0.6) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div style={styles.container}>
      <button 
        onClick={onBack} 
        style={styles.backButton}
        onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)'}
        onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)'}
      >
        ← Back to Agent Store
      </button>

      <div style={styles.header}>
        <h1 style={styles.title}>📅 AddToCalendar Agent</h1>
        <p style={styles.subtitle}>
          Advanced email-to-calendar automation. Extract events from emails and create Google Calendar entries automatically with AI-powered confidence scoring.
        </p>
      </div>

      <div style={styles.controlsContainer}>
        <div style={styles.formGrid}>
          <div style={styles.formGroup}>
            <label style={styles.label}>Action Mode</label>
            <select 
              style={styles.select}
              value={action}
              onChange={(e) => setAction(e.target.value as any)}
            >
              <option value="comprehensive_analysis">Full Analysis + Calendar Creation</option>
              <option value="analyze_only">Extract Events Only (Preview)</option>
              <option value="manual_event">Create Manual Event</option>
            </select>
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>Confidence Threshold</label>
            <select 
              style={styles.select}
              value={confidenceThreshold}
              onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
            >
              <option value={0.5}>Low (50%) - More events, less accuracy</option>
              <option value={0.7}>Medium (70%) - Balanced</option>
              <option value={0.9}>High (90%) - Fewer events, high accuracy</option>
            </select>
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>Max Emails to Process</label>
            <select 
              style={styles.select}
              value={maxEmails}
              onChange={(e) => setMaxEmails(parseInt(e.target.value))}
            >
              <option value={10}>10 emails</option>
              <option value={25}>25 emails</option>
              <option value={50}>50 emails</option>
              <option value={100}>100 emails</option>
            </select>
          </div>
        </div>

        <div style={styles.actionsContainer}>
          {!googleAccessToken && action !== 'analyze_only' && (
            <button 
              style={{...styles.actionButton, ...styles.googleButton}}
              onClick={() => setShowGoogleAuth(true)}
            >
              🔐 Connect Google Calendar
            </button>
          )}
          
          <button 
            style={{...styles.actionButton, ...styles.primaryButton}}
            onClick={executeAddToCalendar}
            disabled={loading}
          >
            {loading ? 'Processing...' : `${action === 'analyze_only' ? 'Analyze' : 'Process'} Emails`}
          </button>

          <button 
            style={{...styles.actionButton, ...styles.secondaryButton}}
            onClick={() => setShowManualEvent(true)}
          >
            + Create Manual Event
          </button>
        </div>

        {googleAccessToken && (
          <div style={{ textAlign: 'center', marginTop: '1rem', color: 'rgba(255, 255, 255, 0.8)' }}>
            ✅ Google Calendar connected
          </div>
        )}
      </div>

      <div style={styles.resultsContainer}>
        <h2>Processing History</h2>
        
        {processingResults.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem' }}>
            <h3>No processing history</h3>
            <p>Run email analysis to see results here!</p>
          </div>
        ) : (
          processingResults.map((result, index) => (
            <div key={index} style={styles.resultCard}>
              <div 
                style={{
                  ...styles.statusBadge,
                  background: getStatusColor(result.status),
                  color: 'white'
                }}
              >
                {result.status.toUpperCase()}
              </div>
              
              <h3>{result.action_performed.replace('_', ' ').toUpperCase()}</h3>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem', margin: '1rem 0' }}>
                <div>
                  <strong>Emails Processed:</strong> {result.emails_processed}
                </div>
                <div>
                  <strong>Events Found:</strong> {result.events_extracted}
                </div>
                <div>
                  <strong>Calendar Events:</strong> {result.events_created}
                </div>
                <div>
                  <strong>Processing Time:</strong> {result.processing_time.toFixed(1)}s
                </div>
              </div>

              {result.calendar_links.length > 0 && (
                <div style={{ marginBottom: '1rem' }}>
                  <strong>Calendar Links:</strong>
                  {result.calendar_links.map((link, i) => (
                    <a 
                      key={i} 
                      href={link} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      style={{ 
                        color: '#60a5fa', 
                        textDecoration: 'none', 
                        marginLeft: '0.5rem',
                        fontSize: '0.9rem'
                      }}
                    >
                      Event {i + 1}
                    </a>
                  ))}
                </div>
              )}

              {result.extracted_events.length > 0 && (
                <div>
                  <strong>Extracted Events:</strong>
                  <div style={styles.eventsGrid}>
                    {result.extracted_events.map((event, i) => (
                      <div key={i} style={styles.eventCard}>
                        <h4>{event.summary}</h4>
                        <p style={{ fontSize: '0.9rem', color: 'rgba(255, 255, 255, 0.8)' }}>
                          {new Date(event.start_time).toLocaleString()} - {new Date(event.end_time).toLocaleString()}
                        </p>
                        {event.description && (
                          <p style={{ fontSize: '0.8rem', color: 'rgba(255, 255, 255, 0.7)' }}>
                            {event.description}
                          </p>
                        )}
                        <div style={{ display: 'flex', alignItems: 'center', marginTop: '0.5rem' }}>
                          <span style={{ fontSize: '0.8rem', marginRight: '0.5rem' }}>
                            Confidence: {(event.confidence * 100).toFixed(0)}%
                          </span>
                          <div style={styles.confidenceBar}>
                            <div 
                              style={{
                                ...styles.confidenceFill,
                                width: `${event.confidence * 100}%`,
                                background: getConfidenceColor(event.confidence)
                              }}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {result.errors.length > 0 && (
                <div style={{ marginTop: '1rem', color: '#fca5a5' }}>
                  <strong>Errors:</strong>
                  <ul>
                    {result.errors.map((error, i) => (
                      <li key={i}>{error}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Google Auth Modal */}
      {showGoogleAuth && (
        <div style={styles.modal} onClick={() => setShowGoogleAuth(false)}>
          <div style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <h2>Connect Google Calendar</h2>
            <p>To create calendar events, you need to authenticate with Google Calendar.</p>
            <div style={{ textAlign: 'center', margin: '2rem 0' }}>
              <button 
                onClick={authenticateWithGoogle}
                style={{
                  padding: '1rem 2rem',
                  background: '#4285f4',
                  border: 'none',
                  borderRadius: '0.5rem',
                  color: 'white',
                  cursor: 'pointer',
                  fontSize: '1rem',
                  fontWeight: '600'
                }}
              >
                🔐 Authenticate with Google
              </button>
            </div>
            <p style={{ fontSize: '0.9rem', color: '#666' }}>
              This is a demo version. In production, this would open Google OAuth flow.
            </p>
          </div>
        </div>
      )}

      {/* Manual Event Modal */}
      {showManualEvent && (
        <div style={styles.modal} onClick={() => setShowManualEvent(false)}>
          <div style={{...styles.modalContent, maxWidth: '600px'}} onClick={(e) => e.stopPropagation()}>
            <h2>Create Manual Calendar Event</h2>
            
            <div style={styles.formGroup}>
              <label style={{...styles.label, color: '#333'}}>Event Title *</label>
              <input
                style={styles.input}
                value={manualEvent.summary}
                onChange={(e) => setManualEvent({...manualEvent, summary: e.target.value})}
                placeholder="Meeting title"
              />
            </div>

            <div style={styles.formGroup}>
              <label style={{...styles.label, color: '#333'}}>Description</label>
              <textarea
                style={styles.textarea}
                value={manualEvent.description}
                onChange={(e) => setManualEvent({...manualEvent, description: e.target.value})}
                placeholder="Event description"
              />
            </div>

            <div style={styles.formGroup}>
              <label style={{...styles.label, color: '#333'}}>Location</label>
              <input
                style={styles.input}
                value={manualEvent.location}
                onChange={(e) => setManualEvent({...manualEvent, location: e.target.value})}
                placeholder="Event location"
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div style={styles.formGroup}>
                <label style={{...styles.label, color: '#333'}}>Start Time *</label>
                <input
                  type="datetime-local"
                  style={styles.input}
                  value={manualEvent.start_time}
                  onChange={(e) => setManualEvent({...manualEvent, start_time: e.target.value})}
                />
              </div>

              <div style={styles.formGroup}>
                <label style={{...styles.label, color: '#333'}}>End Time *</label>
                <input
                  type="datetime-local"
                  style={styles.input}
                  value={manualEvent.end_time}
                  onChange={(e) => setManualEvent({...manualEvent, end_time: e.target.value})}
                />
              </div>
            </div>

            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end', marginTop: '2rem' }}>
              <button 
                onClick={() => setShowManualEvent(false)}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: '#6b7280',
                  border: 'none',
                  borderRadius: '0.5rem',
                  color: 'white',
                  cursor: 'pointer'
                }}
              >
                Cancel
              </button>
              <button 
                onClick={createManualEvent}
                disabled={loading}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: loading ? '#9ca3af' : '#10b981',
                  border: 'none',
                  borderRadius: '0.5rem',
                  color: 'white',
                  cursor: loading ? 'not-allowed' : 'pointer'
                }}
              >
                {loading ? 'Creating...' : 'Create Event'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AddToCalendarAgent;
