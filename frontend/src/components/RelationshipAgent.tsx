import React, { useState, useEffect } from 'react';

interface Contact {
  id: string;
  name: string;
  email: string;
  phone?: string;
  company?: string;
  position?: string;
  lastContact: string;
  relationship: 'family' | 'friend' | 'colleague' | 'client' | 'prospect';
  priority: 'high' | 'medium' | 'low';
  notes: string;
  tags: string[];
  socialMedia?: {
    linkedin?: string;
    twitter?: string;
  };
}

interface Interaction {
  id: string;
  contactId: string;
  date: string;
  type: 'call' | 'email' | 'meeting' | 'message' | 'social';
  description: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  followUpRequired?: boolean;
  followUpDate?: string;
}

interface Reminder {
  id: string;
  contactId: string;
  title: string;
  description: string;
  dueDate: string;
  type: 'birthday' | 'follow_up' | 'meeting' | 'anniversary' | 'check_in';
  completed: boolean;
}

interface RelationshipAgentProps {
  onBack: () => void;
  onSendToHITL?: (message: string, context: any) => void;
}

const RelationshipAgent: React.FC<RelationshipAgentProps> = ({ onBack, onSendToHITL }) => {
  const [activeTab, setActiveTab] = useState<'chat' | 'dashboard' | 'contacts' | 'interactions' | 'reminders'>('chat');
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [loading, setLoading] = useState(false);
  
  // Chat state
  const [chatMessages, setChatMessages] = useState<Array<{id: string, text: string, sender: 'user' | 'agent', timestamp: Date}>>([]);
  const [chatInput, setChatInput] = useState('');
  
  // Form states
  const [showAddContact, setShowAddContact] = useState(false);
  const [showAddInteraction, setShowAddInteraction] = useState(false);
  const [newContact, setNewContact] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    position: '',
    relationship: 'colleague' as const,
    priority: 'medium' as const,
    notes: '',
    tags: ''
  });

  const [newInteraction, setNewInteraction] = useState({
    contactId: '',
    type: 'email' as const,
    description: '',
    sentiment: 'neutral' as const,
    followUpRequired: false,
    followUpDate: ''
  });

  useEffect(() => {
    loadRelationshipData();
  }, []);

  const loadRelationshipData = () => {
    // Mock data - in production, this would come from an API
    const mockContacts: Contact[] = [
      {
        id: '1',
        name: 'John Smith',
        email: 'john.smith@company.com',
        phone: '+1234567890',
        company: 'Tech Corp',
        position: 'Senior Developer',
        lastContact: '2025-01-15',
        relationship: 'colleague',
        priority: 'high',
        notes: 'Great collaborator on projects, interested in AI/ML',
        tags: ['AI', 'Programming', 'Mentor'],
        socialMedia: {
          linkedin: 'linkedin.com/in/johnsmith'
        }
      },
      {
        id: '2',
        name: 'Sarah Johnson',
        email: 'sarah.johnson@startup.io',
        company: 'Startup Inc',
        position: 'Product Manager',
        lastContact: '2025-01-10',
        relationship: 'prospect',
        priority: 'high',
        notes: 'Interested in our AI solutions, follow up next week',
        tags: ['Product', 'AI', 'Potential Client']
      }
    ];

    const mockReminders: Reminder[] = [
      {
        id: '1',
        contactId: '1',
        title: 'Follow up on AI project',
        description: 'Check progress on the machine learning implementation',
        dueDate: '2025-01-20',
        type: 'follow_up',
        completed: false
      }
    ];

    setContacts(mockContacts);
    setReminders(mockReminders);
  };

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [startingSession, setStartingSession] = useState(false);

  const startSessionIfNeeded = async () => {
    if (sessionId || startingSession) return;
    try {
      setStartingSession(true);
      // Lazy import to avoid circular dep at module load
      const { hushMcpApi } = await import('../services/hushMcpApi');
      const tokens = await hushMcpApi.createRelationshipTokens('demo_user');
      const res = await hushMcpApi.startRelationshipChat({
        user_id: 'demo_user',
        tokens,
        session_name: 'default'
      });
      if (res?.session_id) setSessionId(res.session_id);
    } catch (e) {
      console.error('Failed to start relationship chat session:', e);
    } finally {
      setStartingSession(false);
    }
  };

  useEffect(() => {
    startSessionIfNeeded();
  }, []);

  const handleChatSend = async () => {
    if (!chatInput.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      text: chatInput,
      sender: 'user' as const,
      timestamp: new Date()
    };

    setChatMessages(prev => [...prev, userMessage]);
    const toSend = chatInput; // capture before clearing state
    setChatInput('');

    try {
      await startSessionIfNeeded();
      const { hushMcpApi } = await import('../services/hushMcpApi');
      const res = await hushMcpApi.sendRelationshipChatMessage({
        session_id: sessionId || '',
        message: toSend
      });

      const aiResponse = {
        id: (Date.now() + 1).toString(),
        text: res?.agent_response || 'No response from agent',
        sender: 'agent' as const,
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, aiResponse]);
    } catch (e) {
      console.error('Chat send failed:', e);
      const aiResponse = {
        id: (Date.now() + 1).toString(),
        text: generateAIResponse(toSend),
        sender: 'agent' as const,
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, aiResponse]);
    }

    // Send to HITL if needed
    if (onSendToHITL) {
      onSendToHITL(toSend, { 
        context: 'relationship_manager',
        contacts: contacts.length,
        interactions: interactions.length,
        reminders: reminders.filter(r => !r.completed).length
      });
    }
  };

  const generateAIResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();
    
    if (input.includes('contact') || input.includes('add')) {
      return 'I can help you add new contacts! Click on the "Contacts" button below to add a new contact with their details, relationship type, and priority level.';
    } else if (input.includes('interaction') || input.includes('meeting') || input.includes('call')) {
      return 'Great! You can track interactions by clicking the "Interactions" button. This helps you keep a record of all your communications and their outcomes.';
    } else if (input.includes('reminder') || input.includes('follow up')) {
      return 'I can help you set reminders! Use the "Reminders" button to create follow-up reminders, birthday alerts, and meeting notifications.';
    } else if (input.includes('dashboard') || input.includes('overview')) {
      return 'The dashboard gives you a complete overview of your relationships, including recent interactions, upcoming reminders, and contact statistics.';
    } else {
      return 'I\'m here to help you manage your relationships effectively! You can ask me about adding contacts, tracking interactions, setting reminders, or viewing your relationship dashboard. What would you like to do?';
    }
  };

  const addContact = () => {
    if (!newContact.name || !newContact.email) {
      alert('Please fill in required fields');
      return;
    }

    const contact: Contact = {
      id: Date.now().toString(),
      name: newContact.name,
      email: newContact.email,
      phone: newContact.phone,
      company: newContact.company,
      position: newContact.position,
      lastContact: new Date().toISOString().split('T')[0],
      relationship: newContact.relationship,
      priority: newContact.priority,
      notes: newContact.notes,
      tags: newContact.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
    };

    setContacts(prev => [contact, ...prev]);
    setNewContact({
      name: '',
      email: '',
      phone: '',
      company: '',
      position: '',
      relationship: 'colleague',
      priority: 'medium',
      notes: '',
      tags: ''
    });
    setShowAddContact(false);

    // Send to HITL for relationship insights
    if (onSendToHITL) {
      const message = `New contact added: ${contact.name} (${contact.relationship}). Can you suggest the best way to build and maintain this relationship?`;
      onSendToHITL(message, { contact, totalContacts: contacts.length + 1 });
    }
  };

  const styles = {
    container: {
      padding: '2rem',
      background: 'linear-gradient(135deg, #272757, #505081)',
      minHeight: '100vh',
      color: 'white',
    },
    header: {
      textAlign: 'center' as const,
      marginBottom: '2rem',
    },
    title: {
      fontSize: '2.5rem',
      fontWeight: '700',
      marginBottom: '1rem',
      textShadow: '0 4px 6px rgba(0, 0, 0, 0.3)',
    },
    backButton: {
      position: 'absolute' as const,
      top: '2rem',
      left: '2rem',
      padding: '0.5rem 1rem',
      background: 'rgba(255, 255, 255, 0.2)',
      border: 'none',
      borderRadius: '0.5rem',
      color: 'white',
      cursor: 'pointer',
      fontSize: '0.9rem',
      transition: 'all 0.3s ease',
    },
    contentContainer: {
      maxWidth: '800px',
      margin: '0 auto',
      marginBottom: '2rem',
    },
    chatContainer: {
      background: 'rgba(255, 255, 255, 0.1)',
      borderRadius: '1rem',
      padding: '1.5rem',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      height: '500px',
      display: 'flex',
      flexDirection: 'column' as const,
      position: 'relative' as const,
    },
    chatBackgroundText: {
      position: 'absolute' as const,
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
      fontSize: '1.1rem',
      color: 'rgba(255, 255, 255, 0.08)',
      textAlign: 'center' as const,
      pointerEvents: 'none' as const,
      zIndex: 0,
      maxWidth: '80%',
      lineHeight: '1.8',
      userSelect: 'none' as const,
    },
    chatMessages: {
      flex: 1,
      overflowY: 'auto' as const,
      marginBottom: '1rem',
      display: 'flex',
      flexDirection: 'column' as const,
      gap: '1rem',
      position: 'relative' as const,
      zIndex: 1,
    },
    message: {
      maxWidth: '80%',
      padding: '0.75rem 1rem',
      borderRadius: '1rem',
      wordWrap: 'break-word' as const,
    },
    userMessage: {
      alignSelf: 'flex-end',
      background: 'linear-gradient(135deg, #505081, #0F0E47)',
      color: 'white',
    },
    agentMessage: {
      alignSelf: 'flex-start',
      background: 'rgba(255, 255, 255, 0.9)',
      color: '#333',
    },
    messageText: {
      marginBottom: '0.25rem',
      lineHeight: '1.4',
    },
    messageTime: {
      fontSize: '0.75rem',
      opacity: 0.7,
    },
    chatInput: {
      display: 'flex',
      gap: '0.5rem',
      alignItems: 'center',
      position: 'relative' as const,
      zIndex: 1,
    },
    chatInputField: {
      flex: 1,
      padding: '0.75rem',
      borderRadius: '0.5rem',
      border: '1px solid rgba(255, 255, 255, 0.3)',
      background: 'rgba(255, 255, 255, 0.1)',
      color: 'white',
      fontSize: '1rem',
      outline: 'none',
    },
    chatSendButton: {
      padding: '0.75rem 1.5rem',
      background: 'linear-gradient(135deg, #505081, #0F0E47)',
      border: 'none',
      borderRadius: '0.5rem',
      color: 'white',
      cursor: 'pointer',
      fontSize: '0.9rem',
      fontWeight: '500',
      transition: 'all 0.3s ease',
    },
    buttonsContainer: {
      display: 'flex',
      justifyContent: 'center',
      gap: '1rem',
      flexWrap: 'wrap' as const,
      marginTop: '2rem',
    },
    actionButton: {
      padding: '1rem 2rem',
      background: 'rgba(255, 255, 255, 0.2)',
      border: 'none',
      borderRadius: '0.75rem',
      color: 'white',
      cursor: 'pointer',
      fontSize: '1rem',
      fontWeight: '500',
      transition: 'all 0.3s ease',
      minWidth: '150px',
    },
    activeButton: {
      background: 'linear-gradient(135deg, #8686AC, #505081)',
    },
    overlay: {
      position: 'fixed' as const,
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.8)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 2000,
    },
    overlayContent: {
      background: 'linear-gradient(135deg, #272757, #505081)',
      borderRadius: '1rem',
      width: '90%',
      height: '90%',
      color: 'white',
      display: 'flex',
      flexDirection: 'column' as const,
      overflow: 'hidden',
    },
    overlayHeader: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '1.5rem',
      borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
    },
    overlayTitle: {
      margin: 0,
      fontSize: '1.5rem',
      fontWeight: '600',
    },
    closeButton: {
      background: 'none',
      border: 'none',
      color: 'white',
      fontSize: '1.5rem',
      cursor: 'pointer',
      padding: '0.5rem',
      borderRadius: '50%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    },
    overlayBody: {
      flex: 1,
      padding: '1.5rem',
      overflowY: 'auto' as const,
    }
  };

  const renderChat = () => (
    <div style={styles.chatContainer}>
      <div style={styles.chatBackgroundText}>
        🤖 Relationship Assistant
        <br />
        Ask me anything about managing your relationships
      </div>
      
      <div style={styles.chatMessages}>
        {chatMessages.map((message) => (
          <div 
            key={message.id} 
            style={{
              ...styles.message,
              ...(message.sender === 'user' ? styles.userMessage : styles.agentMessage)
            }}
          >
            <div style={styles.messageText}>{message.text}</div>
            <div style={styles.messageTime}>
              {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
          </div>
        ))}
      </div>
      
      <div style={styles.chatInput}>
        <input
          type="text"
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleChatSend()}
          placeholder="Type your message here..."
          style={styles.chatInputField}
        />
        <button 
          onClick={handleChatSend}
          style={styles.chatSendButton}
        >
          Send
        </button>
      </div>
    </div>
  );

  const renderDashboard = () => (
    <div>
      <h3>Dashboard Overview</h3>
      <p>Total Contacts: {contacts.length}</p>
      <p>Pending Reminders: {reminders.filter(r => !r.completed).length}</p>
      <p>Recent Interactions: {interactions.length}</p>
    </div>
  );

  const renderContacts = () => (
    <div>
      <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
        <button 
          style={{...styles.actionButton, background: 'linear-gradient(135deg, #10b981, #047857)'}}
          onClick={() => setShowAddContact(true)}
        >
          + Add Contact
        </button>
      </div>
      <div>
        {contacts.map((contact) => (
          <div key={contact.id} style={{
            background: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '0.75rem',
            padding: '1.5rem',
            marginBottom: '1rem',
            border: '1px solid rgba(255, 255, 255, 0.2)',
          }}>
            <h4>{contact.name}</h4>
            <p>{contact.email}</p>
            <p>{contact.company} - {contact.position}</p>
            <p>Relationship: {contact.relationship}</p>
            <p>Priority: {contact.priority}</p>
          </div>
        ))}
      </div>
    </div>
  );

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
        <h1 style={styles.title}>🤝 Relationship Manager</h1>
      </div>

      {/* Main Content Area - Chat is always visible */}
      <div style={styles.contentContainer}>
        {renderChat()}
      </div>

      {/* Navigation Buttons */}
      <div style={styles.buttonsContainer}>
        {[
          { key: 'dashboard', label: 'Dashboard' },
          { key: 'contacts', label: 'Contacts' },
          { key: 'interactions', label: 'Interactions' },
          { key: 'reminders', label: 'Reminders' }
        ].map((tab) => (
          <button
            key={tab.key}
            style={{
              ...styles.actionButton,
              ...(activeTab === tab.key ? styles.activeButton : {})
            }}
            onClick={() => setActiveTab(tab.key as any)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Specific Content Views (shown as overlay/modal when buttons are clicked) */}
      {activeTab !== 'chat' && (
        <div style={styles.overlay}>
          <div style={styles.overlayContent}>
            <div style={styles.overlayHeader}>
              <h2 style={styles.overlayTitle}>
                {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}
              </h2>
              <button 
                onClick={() => setActiveTab('chat')}
                style={styles.closeButton}
              >
                ✕
              </button>
            </div>
            <div style={styles.overlayBody}>
              {activeTab === 'dashboard' && renderDashboard()}
              {activeTab === 'contacts' && renderContacts()}
              {activeTab === 'interactions' && (
                <div>
                  <p style={{ textAlign: 'center', color: 'rgba(255, 255, 255, 0.8)' }}>
                    Interactions functionality will be added here
                  </p>
                </div>
              )}
              {activeTab === 'reminders' && (
                <div>
                  <p style={{ textAlign: 'center', color: 'rgba(255, 255, 255, 0.8)' }}>
                    Reminders functionality will be added here
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Add Contact Modal */}
      {showAddContact && (
        <div style={styles.overlay} onClick={() => setShowAddContact(false)}>
          <div style={{
            ...styles.overlayContent,
            width: '500px',
            height: 'auto',
            maxHeight: '80vh',
            background: 'rgba(255, 255, 255, 0.95)',
            color: '#333'
          }} onClick={(e) => e.stopPropagation()}>
            <div style={styles.overlayHeader}>
              <h3 style={{...styles.overlayTitle, color: '#333'}}>Add New Contact</h3>
              <button 
                onClick={() => setShowAddContact(false)}
                style={{...styles.closeButton, color: '#333'}}
              >
                ✕
              </button>
            </div>
            <div style={styles.overlayBody}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>Name *</label>
                <input
                  type="text"
                  value={newContact.name}
                  onChange={(e) => setNewContact({...newContact, name: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    borderRadius: '0.5rem',
                    border: '1px solid #ddd',
                    fontSize: '1rem',
                  }}
                  placeholder="Enter contact name"
                />
              </div>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>Email *</label>
                <input
                  type="email"
                  value={newContact.email}
                  onChange={(e) => setNewContact({...newContact, email: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    borderRadius: '0.5rem',
                    border: '1px solid #ddd',
                    fontSize: '1rem',
                  }}
                  placeholder="Enter email address"
                />
              </div>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
                <button
                  onClick={addContact}
                  style={{
                    flex: 1,
                    padding: '0.75rem',
                    fontSize: '1rem',
                    borderRadius: '0.5rem',
                    border: 'none',
                    background: 'linear-gradient(135deg, #505081, #0F0E47)',
                    color: 'white',
                    cursor: 'pointer'
                  }}
                >
                  Add Contact
                </button>
                <button
                  onClick={() => setShowAddContact(false)}
                  style={{
                    flex: 1,
                    padding: '0.75rem',
                    fontSize: '1rem',
                    borderRadius: '0.5rem',
                    border: '1px solid #ddd',
                    background: 'white',
                    color: '#333',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RelationshipAgent;
