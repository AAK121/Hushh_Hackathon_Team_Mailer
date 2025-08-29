import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css'; // You can choose different themes

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
  contactName?: string;
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
  contactName?: string;
  title: string;
  description: string;
  dueDate: string;
  type: 'birthday' | 'follow_up' | 'meeting' | 'anniversary' | 'check_in';
  completed: boolean;
}

interface Memory {
  id: string;
  contactName: string;
  summary: string;
  location?: string;
  date?: string;
  tags: string[];
}

interface RelationshipAgentProps {
  onBack: () => void;
  onSendToHITL?: (message: string, context: any) => void;
}

// Hardcoded vault key that matches the backend encryption key
const RELATIONSHIP_VAULT_KEY = 'e2d989c4d382c80beebbe58c6f07f94b42e554f691ab11738115a489350584b8';

const RelationshipAgent: React.FC<RelationshipAgentProps> = ({ onBack, onSendToHITL }) => {
  // Tab state
  const [activeTab, setActiveTab] = useState<'chat' | 'dashboard' | 'contacts' | 'interactions' | 'reminders' | 'memories'>('chat');
  
  // Data state
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [memories, setMemories] = useState<Memory[]>([]);
  
  // Loading and session state
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [startingSession, setStartingSession] = useState(false);
  const [notification, setNotification] = useState<string>('');
  
  // Chat state
  const [chatMessages, setChatMessages] = useState<Array<{
    id: string, 
    text: string, 
    sender: 'user' | 'agent', 
    timestamp: Date
  }>>([]);
  const [chatInput, setChatInput] = useState('');
  
  // UI state
  const [showOverlay, setShowOverlay] = useState(false);
  const [showAddContact, setShowAddContact] = useState(false);
  const [showAddInteraction, setShowAddInteraction] = useState(false);
  const [showAddReminder, setShowAddReminder] = useState(false);
  const [showAddMemory, setShowAddMemory] = useState(false);
  
  // Form states
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
    type: 'meeting' as const,
    description: '',
    sentiment: 'neutral' as const,
    followUpRequired: false,
    followUpDate: ''
  });

  const [newReminder, setNewReminder] = useState({
    contactId: '',
    title: '',
    description: '',
    dueDate: '',
    type: 'follow_up' as const
  });

  const [newMemory, setNewMemory] = useState({
    contactName: '',
    summary: '',
    location: '',
    date: '',
    tags: ''
  });

  // Initialize with real data from agent
  useEffect(() => {
    loadRealDataFromAgent();
    
    // Set up periodic refresh of relationship data
    const interval = setInterval(() => {
      refreshRelationshipData();
    }, 30000); // Refresh every 30 seconds
    
    return () => clearInterval(interval);
  }, []);

  // Function to load real data from the relationship memory agent
  const loadRealDataFromAgent = async () => {
    console.log('🔄 Starting to load real data from relationship memory agent...');
    try {
      const { hushMcpApi } = await import('../services/hushMcpApi');
      console.log('✅ API service imported successfully');
      
      // Create real consent tokens for the relationship memory agent
      console.log('🎫 Creating consent tokens...');
      const tokens = await hushMcpApi.createRelationshipTokens('demo_user');
      console.log('✅ Tokens created:', Object.keys(tokens));
      
      // Use the relationship memory agent's execute endpoint to get data
      console.log('📡 Fetching contacts...');
      const contactsResponse = await hushMcpApi.executeRelationshipMemory({
        user_id: 'demo_user',
        tokens: tokens,
        user_input: 'show my contacts',
        vault_key: RELATIONSHIP_VAULT_KEY
      });
      
      console.log('📞 Contacts Response:', contactsResponse);
      
      if (contactsResponse?.status === 'success' && contactsResponse.results) {
        const formattedContacts = formatAgentContacts(contactsResponse.results);
        setContacts(formattedContacts);
        console.log('✅ Contacts loaded:', formattedContacts.length);
      }

      console.log('📡 Fetching memories...');
      const memoriesResponse = await hushMcpApi.executeRelationshipMemory({
        user_id: 'demo_user',
        tokens: tokens,
        user_input: 'show my memories',
        vault_key: RELATIONSHIP_VAULT_KEY
      });
      
      console.log('🧠 Memories Response:', memoriesResponse);
      
      if (memoriesResponse?.status === 'success' && memoriesResponse.results) {
        const formattedMemories = formatAgentMemories(memoriesResponse.results);
        setMemories(formattedMemories);
        console.log('✅ Memories loaded:', formattedMemories.length);
      }

      console.log('📡 Fetching reminders...');
      const remindersResponse = await hushMcpApi.executeRelationshipMemory({
        user_id: 'demo_user',
        tokens: tokens,
        user_input: 'show my reminders',
        vault_key: RELATIONSHIP_VAULT_KEY
      });
      
      console.log('⏰ Reminders Response:', remindersResponse);
      
      if (remindersResponse?.status === 'success' && remindersResponse.results) {
        const formattedReminders = formatAgentReminders(remindersResponse.results);
        setReminders(formattedReminders);
        console.log('✅ Reminders loaded:', formattedReminders.length);
      }

      console.log('📡 Fetching interactions...');
      const interactionsResponse = await hushMcpApi.executeRelationshipMemory({
        user_id: 'demo_user',
        tokens: tokens,
        user_input: 'show my interactions',
        vault_key: RELATIONSHIP_VAULT_KEY
      });
      
      console.log('🤝 Interactions Response:', interactionsResponse);
      
      if (interactionsResponse?.status === 'success' && interactionsResponse.results) {
        const formattedInteractions = formatAgentInteractions(interactionsResponse.results);
        setInteractions(formattedInteractions);
        console.log('✅ Interactions loaded:', formattedInteractions.length);
      }
      
      console.log('🎉 Successfully loaded data from relationship memory agent');
      setNotification('✅ Data loaded from relationship memory agent');
      setTimeout(() => setNotification(''), 3000);
      
    } catch (error) {
      console.error('❌ Failed to load data from agent:', error);
      
      // Check if this is a decryption error
      const errorMessage = error?.toString() || '';
      if (errorMessage.includes('decryption') || errorMessage.includes('authentication tag')) {
        console.log('🔄 Decryption error detected, attempting vault reset...');
        setNotification('🔄 Fixing data corruption, please wait...');
        
        try {
          const { hushMcpApi } = await import('../services/hushMcpApi');
          await hushMcpApi.clearRelationshipVault('demo_user');
          await hushMcpApi.initializeFreshVault('demo_user');
          
          // Try loading data again after reset
          setTimeout(() => loadRealDataFromAgent(), 2000);
          setNotification('✅ Data corruption fixed, reloading...');
          return;
        } catch (resetError) {
          console.error('❌ Failed to reset vault:', resetError);
          setNotification('❌ Vault reset failed. Using complete reset...');
          setTimeout(() => forceCompleteReset(), 1000);
          return;
        }
      }
      
      // Check if this is an API quota error
      if (errorMessage.includes('quota') || errorMessage.includes('429') || errorMessage.includes('rate limit')) {
        console.log('⚠️ API quota exceeded, using cached/mock data...');
        setNotification('⚠️ API quota exceeded. Using cached data. Try again later.');
        setTimeout(() => setNotification(''), 5000);
        loadMockData();
        return;
      }
      
      setNotification('⚠️ Using mock data (agent connection failed)');
      setTimeout(() => setNotification(''), 5000);
      loadMockData(); // Fallback to mock data
    }
  };

  // Function to reset vault when decryption errors occur
  const resetVault = async () => {
    try {
      setNotification('🔄 Resetting vault and fixing decryption issues...');
      const { hushMcpApi } = await import('../services/hushMcpApi');
      
      // First try to clear the vault completely
      console.log('🧹 Clearing relationship vault...');
      await hushMcpApi.clearRelationshipVault('demo_user');
      
      // Initialize a fresh vault
      console.log('🔧 Initializing fresh vault...');
      await hushMcpApi.initializeFreshVault('demo_user');
      
      // Clear any cached data in frontend
      setContacts([]);
      setMemories([]);
      setReminders([]);
      setInteractions([]);
      
      setNotification('✅ Vault reset successfully! Reloading data...');
      setTimeout(() => loadRealDataFromAgent(), 2000);
    } catch (error) {
      console.error('❌ Failed to reset vault:', error);
      setNotification('❌ Failed to reset vault. Using mock data.');
      setTimeout(() => {
        setNotification('');
        loadMockData();
      }, 3000);
    }
  };

  // Function to force complete reset including clearing local storage and session data
  const forceCompleteReset = async () => {
    try {
      setNotification('🔥 Performing complete system reset...');
      
      // Clear all frontend state
      setContacts([]);
      setMemories([]);
      setReminders([]);
      setInteractions([]);
      setChatMessages([]);
      setSessionId(null);
      
      // Clear local storage
      localStorage.clear();
      
      const { hushMcpApi } = await import('../services/hushMcpApi');
      
      // Multiple vault clearing attempts
      try {
        await hushMcpApi.clearRelationshipVault('demo_user');
        console.log('✅ First vault clear successful');
      } catch (e) {
        console.warn('⚠️ First vault clear failed, continuing...');
      }
      
      try {
        await hushMcpApi.initializeFreshVault('demo_user');
        console.log('✅ Fresh vault initialization successful');
      } catch (e) {
        console.warn('⚠️ Fresh vault init failed, continuing...');
      }
      
      // Wait a bit then try to reload
      setTimeout(() => {
        setNotification('✅ Complete reset finished! Reloading...');
        setTimeout(() => loadRealDataFromAgent(), 1000);
      }, 2000);
      
    } catch (error) {
      console.error('❌ Complete reset failed:', error);
      setNotification('❌ Reset failed. Using mock data.');
      setTimeout(() => {
        setNotification('');
        loadMockData();
      }, 3000);
    }
  };

  // Function to refresh data from the relationship memory agent
  const refreshRelationshipData = async () => {
    if (sessionId) {
      await loadRealDataFromAgent();
    }
  };

  // Data formatting functions to convert agent data to frontend format
  const formatAgentContacts = (agentData: any): Contact[] => {
    console.log('🔍 Formatting agent contacts data:', agentData);
    
    // Handle different response structures
    let contactsArray = [];
    
    if (Array.isArray(agentData)) {
      contactsArray = agentData;
    } else if (agentData && typeof agentData === 'object') {
      // Check if it's a single contact or has contacts property
      if (agentData.contacts && Array.isArray(agentData.contacts)) {
        contactsArray = agentData.contacts;
      } else if (agentData.name) {
        // Single contact object
        contactsArray = [agentData];
      } else {
        // Look for any array property that might contain contacts
        const arrayProps = Object.values(agentData).filter(value => Array.isArray(value));
        if (arrayProps.length > 0) {
          contactsArray = arrayProps[0] as any[];
        }
      }
    }
    
    console.log('📋 Processing contacts array:', contactsArray);
    
    return contactsArray.map((item: any, index: number) => ({
      id: item.id || `contact_${index + 1}`,
      name: item.name || item.display_name || item.contact_name || 'Unknown',
      email: item.email || item.email_address || '',
      phone: item.phone || item.phone_number || '',
      company: item.company || item.organization || '',
      position: item.position || item.job_title || '',
      lastContact: item.last_contact || item.last_interaction || item.last_talked_date || new Date().toISOString().split('T')[0],
      relationship: (item.relationship_type || item.relationship || 'colleague') as 'family' | 'friend' | 'colleague' | 'client' | 'prospect',
      priority: (item.priority || 'medium') as 'high' | 'medium' | 'low',
      notes: item.notes || item.description || '',
      tags: Array.isArray(item.tags) ? item.tags : (item.keywords ? item.keywords : []),
      socialMedia: {
        linkedin: item.linkedin_url || item.social_media?.linkedin,
        twitter: item.twitter_handle || item.social_media?.twitter,
      }
    }));
  };

  const formatAgentMemories = (agentData: any): Memory[] => {
    console.log('🧠 Formatting agent memories data:', agentData);
    
    let memoriesArray = [];
    
    if (Array.isArray(agentData)) {
      memoriesArray = agentData;
    } else if (agentData && typeof agentData === 'object') {
      if (agentData.memories && Array.isArray(agentData.memories)) {
        memoriesArray = agentData.memories;
      } else if (agentData.summary || agentData.content) {
        memoriesArray = [agentData];
      } else {
        const arrayProps = Object.values(agentData).filter(value => Array.isArray(value));
        if (arrayProps.length > 0) {
          memoriesArray = arrayProps[0] as any[];
        }
      }
    }
    
    console.log('📝 Processing memories array:', memoriesArray);
    
    return memoriesArray.map((item: any, index: number) => ({
      id: item.id || `memory_${index + 1}`,
      contactName: item.contact_name || item.person || 'General',
      summary: item.content || item.description || item.summary || '',
      location: item.location || item.place || '',
      date: item.date || item.created_at || new Date().toISOString().split('T')[0],
      tags: Array.isArray(item.tags) ? item.tags : (item.categories ? item.categories : ['AI-Generated'])
    }));
  };

  const formatAgentReminders = (agentData: any): Reminder[] => {
    console.log('⏰ Formatting agent reminders data:', agentData);
    
    let remindersArray = [];
    
    if (Array.isArray(agentData)) {
      remindersArray = agentData;
    } else if (agentData && typeof agentData === 'object') {
      if (agentData.reminders && Array.isArray(agentData.reminders)) {
        remindersArray = agentData.reminders;
      } else if (agentData.title || agentData.description) {
        remindersArray = [agentData];
      } else {
        const arrayProps = Object.values(agentData).filter(value => Array.isArray(value));
        if (arrayProps.length > 0) {
          remindersArray = arrayProps[0] as any[];
        }
      }
    }
    
    console.log('📅 Processing reminders array:', remindersArray);
    
    return remindersArray.map((item: any, index: number) => ({
      id: item.id || `reminder_${index + 1}`,
      contactId: item.contact_id || '',
      contactName: item.contact_name || item.contactName || 'Unknown',
      title: item.title || item.reminder_text || 'Reminder',
      description: item.description || item.details || '',
      dueDate: item.due_date || item.reminder_date || new Date().toISOString().split('T')[0],
      type: (item.type || 'follow_up') as 'birthday' | 'follow_up' | 'meeting' | 'anniversary' | 'check_in',
      completed: item.completed || item.is_completed || false
    }));
  };

  const formatAgentInteractions = (agentData: any): Interaction[] => {
    console.log('🤝 Formatting agent interactions data:', agentData);
    
    let interactionsArray = [];
    
    if (Array.isArray(agentData)) {
      interactionsArray = agentData;
    } else if (agentData && typeof agentData === 'object') {
      if (agentData.interactions && Array.isArray(agentData.interactions)) {
        interactionsArray = agentData.interactions;
      } else if (agentData.description || agentData.summary) {
        interactionsArray = [agentData];
      } else {
        const arrayProps = Object.values(agentData).filter(value => Array.isArray(value));
        if (arrayProps.length > 0) {
          interactionsArray = arrayProps[0] as any[];
        }
      }
    }
    
    console.log('💼 Processing interactions array:', interactionsArray);
    
    return interactionsArray.map((item: any, index: number) => ({
      id: item.id || `interaction_${index + 1}`,
      contactId: item.contact_id || '',
      contactName: item.contact_name || item.contactName || 'Unknown',
      date: item.date || item.interaction_date || item.created_at || new Date().toISOString().split('T')[0],
      type: (item.type || item.interaction_type || 'message') as 'call' | 'email' | 'meeting' | 'message' | 'social',
      description: item.description || item.summary || item.content || '',
      sentiment: (item.sentiment || 'neutral') as 'positive' | 'neutral' | 'negative',
      followUpRequired: item.follow_up_required || item.followUpRequired || false,
      followUpDate: item.follow_up_date || item.followUpDate
    }));
  };

  const loadMockData = () => {
    const mockContacts: Contact[] = [
      {
        id: '1',
        name: 'Sarah Johnson',
        email: 'sarah.johnson@techcorp.com',
        phone: '+1 555-0123',
        company: 'TechCorp',
        position: 'Product Manager',
        lastContact: '2025-01-15',
        relationship: 'colleague',
        priority: 'high',
        notes: 'Great collaborator on AI projects. Always innovative and reliable.',
        tags: ['AI', 'Product', 'Tech'],
        socialMedia: {
          linkedin: 'https://linkedin.com/in/sarahjohnson'
        }
      },
      {
        id: '2',
        name: 'Mike Chen',
        email: 'mike.chen@startup.io',
        phone: '+1 555-0456',
        company: 'Startup.io',
        position: 'CTO',
        lastContact: '2025-01-10',
        relationship: 'client',
        priority: 'high',
        notes: 'Potential for partnership. Interested in our ML solutions.',
        tags: ['Startup', 'CTO', 'Partnership'],
        socialMedia: {
          linkedin: 'https://linkedin.com/in/mikechen',
          twitter: 'https://twitter.com/mikechen'
        }
      }
    ];

    const mockReminders: Reminder[] = [
      {
        id: '1',
        contactId: '1',
        contactName: 'Sarah Johnson',
        title: 'Follow up on AI project',
        description: 'Check progress on the machine learning implementation',
        dueDate: '2025-01-20',
        type: 'follow_up',
        completed: false
      }
    ];

    const mockMemories: Memory[] = [
      {
        id: '1',
        contactName: 'Sarah Johnson',
        summary: 'Had a great discussion about AI ethics and implementation strategies during coffee meeting',
        location: 'Coffee shop downtown',
        date: '2025-01-15',
        tags: ['AI', 'Ethics', 'Strategy']
      }
    ];

    const mockInteractions: Interaction[] = [
      {
        id: '1',
        contactId: '1',
        contactName: 'John Smith',
        date: '2025-01-15',
        type: 'meeting',
        description: 'Coffee meeting to discuss AI project collaboration',
        sentiment: 'positive',
        followUpRequired: true,
        followUpDate: '2025-01-20'
      },
      {
        id: '2',
        contactId: '2',
        contactName: 'Sarah Johnson',
        date: '2025-01-10',
        type: 'call',
        description: 'Initial consultation call about ML implementation',
        sentiment: 'positive',
        followUpRequired: false
      },
      {
        id: '3',
        contactId: '1',
        contactName: 'John Smith',
        date: '2025-01-08',
        type: 'email',
        description: 'Sent project proposal and timeline',
        sentiment: 'neutral',
        followUpRequired: true,
        followUpDate: '2025-01-15'
      }
    ];

    setContacts(mockContacts);
    setReminders(mockReminders);
    setMemories(mockMemories);
    setInteractions(mockInteractions);
  };

  // Session management
  const startSessionIfNeeded = async () => {
    if (sessionId || startingSession) return;
    try {
      setStartingSession(true);
      const { hushMcpApi } = await import('../services/hushMcpApi');
      const tokens = await hushMcpApi.createRelationshipTokens('demo_user');
      const res = await hushMcpApi.startRelationshipChat({
        user_id: 'demo_user',
        tokens,
        vault_key: RELATIONSHIP_VAULT_KEY,
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

  // Chat functionality
  const handleChatSend = async () => {
    if (!chatInput.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      text: chatInput,
      sender: 'user' as const,
      timestamp: new Date()
    };

    setChatMessages(prev => [...prev, userMessage]);
    const toSend = chatInput;
    setChatInput('');

    try {
      await startSessionIfNeeded();
      const { hushMcpApi } = await import('../services/hushMcpApi');
      const tokens = await hushMcpApi.createRelationshipTokens('demo_user');
      
      try {
        const res = await hushMcpApi.sendRelationshipChatMessage({
          session_id: sessionId || '',
          message: toSend,
          user_id: 'demo_user',
          consent_tokens: tokens
        });

        const aiResponse = {
          id: (Date.now() + 1).toString(),
          text: res?.agent_response || 'No response from agent',
          sender: 'agent' as const,
          timestamp: new Date()
        };
        setChatMessages(prev => [...prev, aiResponse]);
        
        // Parse AI response for structured data
        parseAIResponseForData(res?.agent_response || '', toSend);
        
        // Refresh data from agent after each interaction
        setTimeout(() => {
          refreshRelationshipData();
        }, 2000); // Wait 2 seconds for agent to process
        
      } catch (chatError: any) {
        // If session not found (404), recreate session and retry
        if (chatError.message?.includes('404') || chatError.message?.includes('not found')) {
          console.log('Chat session expired, creating new session...');
          setSessionId(null); // Clear the invalid session
          
          // Recreate session
          const newSessionRes = await hushMcpApi.startRelationshipChat({
            user_id: 'demo_user',
            tokens,
            vault_key: RELATIONSHIP_VAULT_KEY,
            session_name: 'default'
          });
          
          if (newSessionRes?.session_id) {
            setSessionId(newSessionRes.session_id);
            
            // Retry the message with new session
            const retryRes = await hushMcpApi.sendRelationshipChatMessage({
              session_id: newSessionRes.session_id,
              message: toSend,
              user_id: 'demo_user',
              consent_tokens: tokens
            });

            const aiResponse = {
              id: (Date.now() + 1).toString(),
              text: retryRes?.agent_response || 'No response from agent',
              sender: 'agent' as const,
              timestamp: new Date()
            };
            setChatMessages(prev => [...prev, aiResponse]);
            
            // Parse AI response for structured data
            parseAIResponseForData(retryRes?.agent_response || '', toSend);
            
            // Refresh data from agent after each interaction
            setTimeout(() => {
              refreshRelationshipData();
            }, 2000);
          }
        } else {
          throw chatError; // Re-throw if it's not a session error
        }
      }
      
    } catch (e) {
      console.error('Chat send failed:', e);
      
      // Check for API quota errors
      const errorMessage = e?.toString() || '';
      let fallbackMessage = generateAIResponse(toSend);
      
      if (errorMessage.includes('quota') || errorMessage.includes('429') || errorMessage.includes('rate limit')) {
        fallbackMessage = `⚠️ **API Quota Exceeded**\n\nI'm currently experiencing rate limits. Here's what I can help with using cached data:\n\n${fallbackMessage}\n\n*Please try again in a few minutes when the API quota resets.*`;
      } else if (errorMessage.includes('decryption') || errorMessage.includes('authentication')) {
        fallbackMessage = `🔧 **Data Corruption Detected**\n\nThere seems to be an issue with the encrypted data. Please use the **Reset Vault** or **Complete Reset** buttons above to fix this.\n\n${fallbackMessage}`;
      }
      
      const aiResponse = {
        id: (Date.now() + 1).toString(),
        text: fallbackMessage,
        sender: 'agent' as const,
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, aiResponse]);
    }
  };

  // Parse AI response for actionable data
  const parseAIResponseForData = (response: string, userInput: string) => {
    const now = new Date().toISOString();
    
    // Extract contact information
    const contactMatch = response.match(/(?:contact|person|individual).*?(?:name|called):\s*([^,\n.]+)/i);
    const emailMatch = response.match(/email.*?:\s*([^\s,\n.]+@[^\s,\n.]+)/i);
    const phoneMatch = response.match(/phone.*?:\s*([\+\d\-\(\)\s]+)/i);
    const companyMatch = response.match(/(?:company|organization|works?\s+at).*?:\s*([^,\n.]+)/i);
    
    if (contactMatch && contactMatch[1]) {
      const newContact: Contact = {
        id: Date.now().toString(),
        name: contactMatch[1].trim(),
        email: emailMatch ? emailMatch[1].trim() : '',
        phone: phoneMatch ? phoneMatch[1].trim() : '',
        company: companyMatch ? companyMatch[1].trim() : '',
        position: '',
        lastContact: now.split('T')[0],
        relationship: 'colleague' as const,
        priority: 'medium' as const,
        notes: `Added from conversation: ${userInput}`,
        tags: ['AI-Generated']
      };
      
      // Check if contact already exists
      const existingContact = contacts.find(c => 
        c.name.toLowerCase() === newContact.name.toLowerCase() ||
        (c.email && newContact.email && c.email.toLowerCase() === newContact.email.toLowerCase())
      );
      
      if (!existingContact) {
        setContacts(prev => [...prev, newContact]);
        setNotification(`✅ Added new contact: ${newContact.name}`);
        setTimeout(() => setNotification(''), 3000);
        console.log('Added new contact from conversation:', newContact.name);
      }
    }
    
    // Extract reminders
    const reminderMatch = response.match(/(?:remind|reminder|follow.?up|remember).*?(?:to|about|that)\s*([^.!?\n]+)/i);
    const dateMatch = response.match(/(?:tomorrow|next week|in \d+ days?|\d{4}-\d{2}-\d{2})/i);
    
    if (reminderMatch && reminderMatch[1]) {
      const newReminder: Reminder = {
        id: Date.now().toString(),
        contactId: contacts[0]?.id || '',
        title: reminderMatch[1].trim(),
        description: `Reminder from conversation: ${userInput}`,
        dueDate: dateMatch ? calculateDueDate(dateMatch[0]) : new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        type: 'follow_up',
        completed: false
      };
      
      setReminders(prev => [...prev, newReminder]);
      setNotification(`🔔 Added reminder: ${newReminder.title}`);
      setTimeout(() => setNotification(''), 3000);
      console.log('Added reminder from conversation:', newReminder.title);
    }
    
    // Extract memories
    const memoryKeywords = ['remember', 'mentioned', 'told me', 'discussed', 'talked about'];
    const hasMemoryKeyword = memoryKeywords.some(keyword => 
      response.toLowerCase().includes(keyword) || userInput.toLowerCase().includes(keyword)
    );
    
    if (hasMemoryKeyword && response.length > 50) {
      const newMemory: Memory = {
        id: Date.now().toString(),
        contactName: contactMatch ? contactMatch[1].trim() : 'General',
        summary: response.length > 200 ? response.substring(0, 200) + '...' : response,
        date: now.split('T')[0],
        tags: ['AI-Generated', 'Conversation']
      };
      
      setMemories(prev => [...prev, newMemory]);
      setNotification(`💭 Added memory: ${newMemory.contactName}`);
      setTimeout(() => setNotification(''), 3000);
      console.log('Added memory from conversation');
    }
    
    // Extract interactions
    const interactionTypes = ['call', 'email', 'meeting', 'message'];
    const interactionMatch = interactionTypes.find(type => 
      userInput.toLowerCase().includes(type) || response.toLowerCase().includes(type)
    );
    
    if (interactionMatch) {
      const newInteraction: Interaction = {
        id: Date.now().toString(),
        contactId: contacts[0]?.id || '',
        date: now.split('T')[0],
        type: interactionMatch as any,
        description: userInput,
        sentiment: determineSentiment(response),
        followUpRequired: response.toLowerCase().includes('follow') || response.toLowerCase().includes('next')
      };
      
      setInteractions(prev => [...prev, newInteraction]);
      setNotification(`📋 Added interaction: ${interactionMatch}`);
      setTimeout(() => setNotification(''), 3000);
      console.log('Added interaction from conversation');
    }
  };
  
  // Helper function to calculate due dates
  const calculateDueDate = (dateText: string): string => {
    const today = new Date();
    
    if (dateText.toLowerCase() === 'tomorrow') {
      return new Date(today.getTime() + 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    } else if (dateText.toLowerCase() === 'next week') {
      return new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    } else if (dateText.match(/in (\d+) days?/)) {
      const days = parseInt(dateText.match(/(\d+)/)![1]);
      return new Date(today.getTime() + days * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    } else if (dateText.match(/\d{4}-\d{2}-\d{2}/)) {
      return dateText;
    }
    
    return new Date(today.getTime() + 24 * 60 * 60 * 1000).toISOString().split('T')[0];
  };
  
  // Helper function to determine sentiment
  const determineSentiment = (text: string): 'positive' | 'neutral' | 'negative' => {
    const positiveWords = ['good', 'great', 'excellent', 'happy', 'pleased', 'successful', 'wonderful'];
    const negativeWords = ['bad', 'terrible', 'disappointed', 'frustrated', 'problem', 'issue', 'concern'];
    
    const lowerText = text.toLowerCase();
    const positiveCount = positiveWords.filter(word => lowerText.includes(word)).length;
    const negativeCount = negativeWords.filter(word => lowerText.includes(word)).length;
    
    if (positiveCount > negativeCount) return 'positive';
    if (negativeCount > positiveCount) return 'negative';
    return 'neutral';
  };

  const generateAIResponse = (input: string) => {
    const lowerInput = input.toLowerCase();
    
    if (lowerInput.includes('error') || lowerInput.includes('issue') || lowerInput.includes('problem') || lowerInput.includes('fix')) {
      return `## 🔧 Troubleshooting

I notice you're experiencing some issues. Here are common problems and solutions:

### 🔐 Decryption Errors:
If you see "authentication tag" or "decryption failed" errors:
1. **Try the Reset Vault button** (🔧) - This clears corrupted data
2. **Use Complete Reset** (🔥) - Nuclear option that clears everything
3. **Wait and retry** - Sometimes it's a temporary issue

### ⚠️ API Quota Issues:
If you see "quota exceeded" or "429" errors:
- The AI service has hit rate limits
- **Wait 5-10 minutes** then try again
- I'll fall back to cached responses meanwhile

### 📊 Missing Data:
If interactions, contacts, or other data aren't showing:
- Use **Refresh Data** button (🔄)
- Check if the vault needs resetting
- I'll show mock data as fallback

### 🆘 Need More Help?
Try these buttons in the header:
- 🔄 **Refresh Data** - Reload from agent
- 🔧 **Reset Vault** - Fix data corruption  
- 🔥 **Complete Reset** - Start completely fresh

*I'm designed to be resilient and will work with cached/mock data even when things go wrong!*`;
    } else if (lowerInput.includes('contact') || lowerInput.includes('person')) {
      return `## 👥 Contact Management

I can help you manage your contacts. You currently have **${contacts.length}** contacts in your network. 

### How to add contacts:
- Say: *"I met John Smith from TechCorp, his email is john@techcorp.com"*
- I'll automatically extract and add the contact information!

**Features:**
- Automatic contact extraction from conversations
- Priority levels and relationship tracking
- Company and role information
- Notes and tags`;
    } else if (lowerInput.includes('remind') || lowerInput.includes('reminder')) {
      return `## ⏰ Reminder Management

I'll help you set reminders! Here are some examples:

### Natural language reminders:
- *"Remind me to follow up with Sarah tomorrow"*
- *"Remember to call the client next week"*
- *"Set a reminder for John's birthday on March 15th"*

> I'll automatically create reminders and associate them with your contacts!`;
    } else if (lowerInput.includes('memory') || lowerInput.includes('remember')) {
      return `## 🧠 Memory Storage

I'm storing our conversation as memories. You currently have **${memories.length}** memories stored.

### What I remember:
- Important conversations and interactions
- Personal details mentioned about contacts
- Business discussions and insights
- Meeting outcomes and follow-ups

*I automatically capture important details from our chats!*`;
    } else if (lowerInput.includes('interaction') || lowerInput.includes('meeting')) {
      return `## 📋 Interaction Tracking

I'm tracking your interactions! You have **${interactions.length}** recorded interactions.

### Types of interactions I track:
1. **Meetings** - Coffee chats, business meetings
2. **Calls** - Phone conversations
3. **Emails** - Email exchanges
4. **Messages** - Text or chat communications

Just mention these activities in our chat and I'll log them automatically!`;
    } else if (lowerInput.includes('dashboard') || lowerInput.includes('summary')) {
      return `## 📊 Your Relationship Dashboard

Here's your current overview:

| Category | Count |
|----------|-------|
| Contacts | ${contacts.length} |
| Interactions | ${interactions.length} |
| Memories | ${memories.length} |
| Pending Reminders | ${reminders.filter(r => !r.completed).length} |

### 💡 Tip:
Try mentioning specific people or activities and I'll update your data automatically!`;
    } else if (lowerInput.includes('markdown') || lowerInput.includes('format')) {
      return `## ✨ Markdown Support

I now support **rich markdown formatting**! You can use:

### Text Formatting:
- **Bold text** with \`**bold**\`
- *Italic text* with \`*italic*\`
- \`Code snippets\` with backticks
- ~~Strikethrough~~ with \`~~text~~\`

### Lists:
1. Numbered lists
2. Work great
3. For step-by-step instructions

- Bullet points
- Are perfect for
- Quick lists

### Code Blocks:
\`\`\`javascript
// Code blocks with syntax highlighting
function hello() {
  console.log("Hello, world!");
}
\`\`\`

### Tables:
| Feature | Status |
|---------|--------|
| Markdown | ✅ Working |
| Tables | ✅ Supported |
| Code | ✅ Highlighted |

> **Quote blocks** are great for important notes!

[Links work too!](https://example.com)`;
    } else {
      return `## 🤝 Welcome to Relationship Memory Assistant!

I'm here to help you manage your **professional and personal relationships**.

### What I can do:
- 👥 **Manage Contacts** - Add and organize your network
- ⏰ **Set Reminders** - Never forget to follow up
- 🧠 **Store Memories** - Remember important conversations
- 📋 **Track Interactions** - Log meetings, calls, and more

### 🚀 Quick Start:
Try saying something like:
- *"I met Sarah Johnson from TechCorp today"*
- *"Remind me to call Mike next week"*
- *"Remember that Alice loves hiking"*

**New:** I now support **full markdown formatting** for rich, beautiful responses! ✨`;
    }
  };

  // CRUD operations
  const addContact = async () => {
    if (!newContact.name || !newContact.email) return;

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
      tags: newContact.tags ? newContact.tags.split(',').map(t => t.trim()) : []
    };

    setContacts(prev => [...prev, contact]);
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

    // Try to add via API
    try {
      const { hushMcpApi } = await import('../services/hushMcpApi');
      await hushMcpApi.executeRelationshipMemory({
        user_id: 'demo_user',
        tokens: await hushMcpApi.createRelationshipTokens('demo_user'),
        user_input: `Add contact: ${contact.name}, email: ${contact.email}, company: ${contact.company || 'N/A'}`
      });
    } catch (e) {
      console.error('Failed to add contact via API:', e);
    }
  };

  const addMemory = async () => {
    if (!newMemory.contactName || !newMemory.summary) return;

    const memory: Memory = {
      id: Date.now().toString(),
      contactName: newMemory.contactName,
      summary: newMemory.summary,
      location: newMemory.location,
      date: newMemory.date,
      tags: newMemory.tags ? newMemory.tags.split(',').map(t => t.trim()) : []
    };

    setMemories(prev => [...prev, memory]);
    setNewMemory({
      contactName: '',
      summary: '',
      location: '',
      date: '',
      tags: ''
    });
    setShowAddMemory(false);

    // Try to add via API
    try {
      const { hushMcpApi } = await import('../services/hushMcpApi');
      await hushMcpApi.executeRelationshipMemory({
        user_id: 'demo_user',
        tokens: await hushMcpApi.createRelationshipTokens('demo_user'),
        user_input: `Remember about ${memory.contactName}: ${memory.summary} ${memory.location ? `at ${memory.location}` : ''} ${memory.date ? `on ${memory.date}` : ''}`
      });
    } catch (e) {
      console.error('Failed to add memory via API:', e);
    }
  };

  const addReminder = async () => {
    if (!newReminder.title || !newReminder.dueDate) return;

    const contactName = contacts.find(c => c.id === newReminder.contactId)?.name || 'Unknown';
    const reminder: Reminder = {
      id: Date.now().toString(),
      contactId: newReminder.contactId,
      contactName: contactName,
      title: newReminder.title,
      description: newReminder.description,
      dueDate: newReminder.dueDate,
      type: newReminder.type,
      completed: false
    };

    setReminders(prev => [...prev, reminder]);
    setNewReminder({
      contactId: '',
      title: '',
      description: '',
      dueDate: '',
      type: 'follow_up'
    });
    setShowAddReminder(false);

    // Try to add via API
    try {
      const { hushMcpApi } = await import('../services/hushMcpApi');
      await hushMcpApi.executeRelationshipMemory({
        user_id: 'demo_user',
        tokens: await hushMcpApi.createRelationshipTokens('demo_user'),
        user_input: `Set reminder: ${reminder.title} for ${contactName} on ${reminder.dueDate}. ${reminder.description}`
      });
    } catch (e) {
      console.error('Failed to add reminder via API:', e);
    }
  };

  const addInteraction = async () => {
    if (!newInteraction.contactId || !newInteraction.description) return;

    const selectedContact = contacts.find(c => c.id === newInteraction.contactId);
    const interaction: Interaction = {
      id: Date.now().toString(),
      contactId: newInteraction.contactId,
      contactName: selectedContact?.name || 'Unknown',
      date: new Date().toISOString().split('T')[0],
      type: newInteraction.type,
      description: newInteraction.description,
      sentiment: newInteraction.sentiment,
      followUpRequired: newInteraction.followUpRequired,
      followUpDate: newInteraction.followUpDate
    };

    setInteractions(prev => [...prev, interaction]);
    setNewInteraction({
      contactId: '',
      type: 'meeting',
      description: '',
      sentiment: 'neutral',
      followUpRequired: false,
      followUpDate: ''
    });
    setShowAddInteraction(false);

    // Try to add via API
    try {
      const { hushMcpApi } = await import('../services/hushMcpApi');
      const contactName = contacts.find(c => c.id === interaction.contactId)?.name || 'Unknown';
      await hushMcpApi.executeRelationshipMemory({
        user_id: 'demo_user',
        tokens: await hushMcpApi.createRelationshipTokens('demo_user'),
        user_input: `Log interaction with ${contactName}: ${interaction.description} (${interaction.type}, ${interaction.sentiment})`
      });
    } catch (e) {
      console.error('Failed to add interaction via API:', e);
    }
  };

  // Render functions
  const renderDashboard = () => (
    <div style={styles.dashboardGrid}>
      <div style={styles.statCard}>
        <h3 style={styles.statTitle}>Total Contacts</h3>
        <div style={styles.statValue}>{contacts.length}</div>
        <div style={styles.statSubtext}>Across all relationships</div>
      </div>
      <div style={styles.statCard}>
        <h3 style={styles.statTitle}>Pending Reminders</h3>
        <div style={styles.statValue}>{reminders.filter(r => !r.completed).length}</div>
        <div style={styles.statSubtext}>Require attention</div>
      </div>
      <div style={styles.statCard}>
        <h3 style={styles.statTitle}>Recent Interactions</h3>
        <div style={styles.statValue}>{interactions.length}</div>
        <div style={styles.statSubtext}>This month</div>
      </div>
      <div style={styles.statCard}>
        <h3 style={styles.statTitle}>Stored Memories</h3>
        <div style={styles.statValue}>{memories.length}</div>
        <div style={styles.statSubtext}>Personal insights</div>
      </div>
    </div>
  );

  const renderContacts = () => {
    console.log('📋 Rendering contacts tab with data:', contacts);
    console.log('📊 Contacts count:', contacts.length);
    
    return (
      <div>
        <div style={styles.sectionHeader}>
          <h3 style={styles.sectionTitle}>Contacts ({contacts.length})</h3>
          <button
            onClick={() => setShowAddContact(true)}
            style={styles.addButton}
          >
            Add Contact
          </button>
        </div>
        
        {/* Debug Info */}
        <div style={{ 
          background: 'rgba(255,255,255,0.1)', 
          padding: '1rem', 
          marginBottom: '1rem', 
          borderRadius: '0.5rem',
          fontSize: '0.9rem',
          fontFamily: 'monospace'
        }}>
          <strong>Debug Info:</strong><br/>
          Total Contacts: {contacts.length}<br/>
          Loading: {loading ? 'Yes' : 'No'}<br/>
          Session ID: {sessionId || 'None'}<br/>
          {contacts.length === 0 && (
            <span style={{ color: '#ff6b6b' }}>
              ⚠️ No contacts found. Try using chat to add contacts or click "Refresh Data" button.
            </span>
          )}
        </div>
        
        <div style={styles.itemsList}>
          {contacts.length === 0 ? (
            <div style={{ 
              textAlign: 'center', 
              padding: '2rem',
              background: 'rgba(255,255,255,0.1)',
              borderRadius: '0.5rem',
              opacity: 0.7
            }}>
              <p>No contacts found. Use the chat to add contacts!</p>
              <p style={{ fontSize: '0.9rem', marginTop: '1rem' }}>
                Try saying: "Add contact John Smith with email john@example.com"
              </p>
            </div>
          ) : (
            contacts.map(contact => (
              <div key={contact.id} style={styles.contactCard}>
                <div style={styles.contactInfo}>
                  <div style={styles.contactName}>{contact.name}</div>
                  <div style={styles.contactDetails}>
                    {contact.email} • {contact.company} • {contact.position}
                  </div>
                  <div style={styles.contactTags}>
                    {contact.tags.map(tag => (
                      <span key={tag} style={styles.tag}>{tag}</span>
                    ))}
                  </div>
                </div>
                <div style={styles.contactActions}>
                  <span style={{
                    ...styles.priorityBadge,
                    backgroundColor: contact.priority === 'high' ? '#ff4757' : 
                                   contact.priority === 'medium' ? '#ffa502' : '#2ed573'
                  }}>
                    {contact.priority}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    );
  };

  const renderMemories = () => (
    <div>
      <div style={styles.sectionHeader}>
        <h3 style={styles.sectionTitle}>Memories</h3>
        <button
          onClick={() => setShowAddMemory(true)}
          style={styles.addButton}
        >
          Add Memory
        </button>
      </div>
      <div style={styles.itemsList}>
        {memories.map(memory => (
          <div key={memory.id} style={styles.memoryCard}>
            <div style={styles.memoryHeader}>
              <strong>{memory.contactName}</strong>
              {memory.date && <span style={styles.memoryDate}>{memory.date}</span>}
            </div>
            <div style={styles.memorySummary}>{memory.summary}</div>
            {memory.location && (
              <div style={styles.memoryLocation}>📍 {memory.location}</div>
            )}
            <div style={styles.memoryTags}>
              {memory.tags.map(tag => (
                <span key={tag} style={styles.tag}>{tag}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderInteractions = () => (
    <div>
      <div style={styles.sectionHeader}>
        <h3 style={styles.sectionTitle}>Interactions</h3>
        <button
          onClick={() => setShowAddInteraction(true)}
          style={styles.addButton}
        >
          Add Interaction
        </button>
      </div>
      <div style={styles.itemsList}>
        {interactions.map(interaction => (
          <div key={interaction.id} style={styles.interactionCard}>
            <div style={styles.interactionHeader}>
              <strong>{interaction.contactName || 'Unknown'}</strong>
              <span style={styles.interactionDate}>{interaction.date}</span>
            </div>
            <div style={styles.interactionType}>
              {interaction.type} • {interaction.sentiment}
            </div>
            <div style={styles.interactionDescription}>{interaction.description}</div>
            {interaction.followUpRequired && (
              <div style={styles.followUpRequired}>
                Follow-up needed: {interaction.followUpDate}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );

  const renderReminders = () => (
    <div>
      <div style={styles.sectionHeader}>
        <h3 style={styles.sectionTitle}>Reminders</h3>
        <button
          onClick={() => setShowAddReminder(true)}
          style={styles.addButton}
        >
          Add Reminder
        </button>
      </div>
      <div style={styles.itemsList}>
        {reminders.map(reminder => (
          <div key={reminder.id} style={styles.reminderCard}>
            <div style={styles.reminderHeader}>
              <strong>{reminder.title}</strong>
              <span style={styles.reminderDate}>{reminder.dueDate}</span>
            </div>
            <div style={styles.reminderDescription}>{reminder.description}</div>
            <div style={styles.reminderContact}>
              Contact: {reminder.contactName || contacts.find(c => c.id === reminder.contactId)?.name || 'Unknown'}
            </div>
            <button
              onClick={() => {
                setReminders(prev => 
                  prev.map(r => r.id === reminder.id ? {...r, completed: !r.completed} : r)
                );
              }}
              style={{
                ...styles.reminderToggle,
                backgroundColor: reminder.completed ? '#2ed573' : '#ffa502'
              }}
            >
              {reminder.completed ? 'Completed' : 'Mark Complete'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );

  const renderChat = () => (
    <div style={styles.chatContainer}>
      <div style={styles.chatBackgroundText}>
        💬 Relationship Memory Assistant<br/>
        Ask me about your contacts, memories, reminders, or interactions.<br/>
        I can help you manage your professional and personal relationships.<br/>
        ✨ Now with full markdown support for rich formatting!
      </div>
      <div style={styles.chatMessages}>
        {chatMessages.map(message => (
          <div
            key={message.id}
            style={{
              ...styles.message,
              ...(message.sender === 'user' ? styles.userMessage : styles.agentMessage)
            }}
          >
            <div style={styles.messageText}>
              <ReactMarkdown 
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeHighlight]}
                components={{
                  // Custom styling for markdown elements within messages
                  p: ({children}) => <p style={{margin: '0 0 0.5rem 0', lineHeight: '1.4'}}>{children}</p>,
                  ul: ({children}) => <ul style={{margin: '0.5rem 0', paddingLeft: '1rem'}}>{children}</ul>,
                  ol: ({children}) => <ol style={{margin: '0.5rem 0', paddingLeft: '1rem'}}>{children}</ol>,
                  li: ({children}) => <li style={{marginBottom: '0.25rem'}}>{children}</li>,
                  code: ({children}) => <code style={{
                    backgroundColor: message.sender === 'user' ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.1)',
                    padding: '0.2rem 0.4rem',
                    borderRadius: '0.25rem',
                    fontSize: '0.9em',
                    fontFamily: 'monospace'
                  }}>{children}</code>,
                  pre: ({children}) => <pre style={{
                    backgroundColor: message.sender === 'user' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
                    padding: '0.75rem',
                    borderRadius: '0.5rem',
                    overflow: 'auto',
                    fontSize: '0.9em',
                    fontFamily: 'monospace',
                    margin: '0.5rem 0'
                  }}>{children}</pre>,
                  blockquote: ({children}) => <blockquote style={{
                    borderLeft: `3px solid ${message.sender === 'user' ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.3)'}`,
                    paddingLeft: '1rem',
                    margin: '0.5rem 0',
                    fontStyle: 'italic',
                    opacity: 0.9
                  }}>{children}</blockquote>,
                  h1: ({children}) => <h1 style={{fontSize: '1.2em', margin: '0.5rem 0', fontWeight: 'bold'}}>{children}</h1>,
                  h2: ({children}) => <h2 style={{fontSize: '1.1em', margin: '0.5rem 0', fontWeight: 'bold'}}>{children}</h2>,
                  h3: ({children}) => <h3 style={{fontSize: '1.05em', margin: '0.5rem 0', fontWeight: 'bold'}}>{children}</h3>,
                  strong: ({children}) => <strong style={{fontWeight: 'bold'}}>{children}</strong>,
                  em: ({children}) => <em style={{fontStyle: 'italic'}}>{children}</em>,
                  table: ({children}) => <table style={{
                    borderCollapse: 'collapse',
                    width: '100%',
                    margin: '0.5rem 0',
                    fontSize: '0.9em'
                  }}>{children}</table>,
                  thead: ({children}) => <thead style={{
                    backgroundColor: message.sender === 'user' ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.1)'
                  }}>{children}</thead>,
                  th: ({children}) => <th style={{
                    border: `1px solid ${message.sender === 'user' ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.2)'}`,
                    padding: '0.5rem',
                    textAlign: 'left',
                    fontWeight: 'bold'
                  }}>{children}</th>,
                  td: ({children}) => <td style={{
                    border: `1px solid ${message.sender === 'user' ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.2)'}`,
                    padding: '0.5rem'
                  }}>{children}</td>,
                  hr: () => <hr style={{
                    border: 'none',
                    borderTop: `1px solid ${message.sender === 'user' ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.2)'}`,
                    margin: '1rem 0'
                  }} />,
                  a: ({href, children}) => <a 
                    href={href} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    style={{
                      color: message.sender === 'user' ? '#87ceeb' : '#4169e1',
                      textDecoration: 'underline'
                    }}
                  >{children}</a>
                }}
              >
                {message.text}
              </ReactMarkdown>
            </div>
            <div style={styles.messageTime}>
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}
      </div>
      
      {/* Quick Examples */}
      <div style={{ marginBottom: '1rem' }}>
        <small style={{ color: '#ccc', marginBottom: '0.5rem', display: 'block' }}>
          💡 Try these examples to see automatic data extraction & markdown formatting:
        </small>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {[
            "I met John Smith from TechCorp, his email is john@techcorp.com",
            "Remind me to call Sarah tomorrow",
            "Had a great meeting with the client today",
            "Remember that Mike mentioned he's getting married next month",
            "Show me markdown formatting examples"
          ].map((example, index) => (
            <button
              key={index}
              onClick={() => setChatInput(example)}
              style={{
                padding: '0.4rem 0.8rem',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '1rem',
                color: 'white',
                fontSize: '0.75rem',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
              }}
            >
              {example.length > 35 ? example.substring(0, 35) + '...' : example}
            </button>
          ))}
        </div>
      </div>
      
      <div style={styles.chatInput}>
        <input
          type="text"
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleChatSend()}
          placeholder="Ask me about your relationships..."
          style={styles.chatInputField}
        />
        <button
          onClick={handleChatSend}
          disabled={!chatInput.trim()}
          style={styles.chatSendButton}
        >
          Send
        </button>
      </div>
    </div>
  );

  // Main render
  return (
    <div style={styles.container}>
      <div style={styles.wrapper}>
        <div style={styles.header}>
          <button onClick={onBack} style={styles.backButton}>
            ← Back
          </button>
          <h1 style={styles.title}>🤝 Relationship Memory Agent</h1>
          <div style={styles.headerActions}>
            <button
              onClick={loadRealDataFromAgent}
              style={styles.detailsButton}
              disabled={loading}
            >
              {loading ? '🔄 Loading...' : '🔄 Refresh Data'}
            </button>
            <button
              onClick={resetVault}
              style={{...styles.detailsButton, backgroundColor: '#ff6b6b', color: 'white'}}
              disabled={loading}
            >
              🔧 Reset Vault
            </button>
            <button
              onClick={forceCompleteReset}
              style={{...styles.detailsButton, backgroundColor: '#dc3545', color: 'white'}}
              disabled={loading}
              title="Complete system reset - clears all data and starts fresh"
            >
              🔥 Complete Reset
            </button>
            <button
              onClick={() => setShowOverlay(true)}
              style={styles.detailsButton}
            >
              View Details
            </button>
          </div>
        </div>

        {/* Notification Banner */}
        {notification && (
          <div style={styles.notification}>
            {notification}
          </div>
        )}

        <div style={styles.tabContainer}>
          {['chat', 'dashboard', 'contacts', 'memories', 'interactions', 'reminders'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as any)}
              style={{
                ...styles.tab,
                ...(activeTab === tab ? styles.activeTab : {})
              }}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        <div style={styles.contentContainer}>
          {activeTab === 'chat' && renderChat()}
          {activeTab === 'dashboard' && renderDashboard()}
          {activeTab === 'contacts' && renderContacts()}
          {activeTab === 'memories' && renderMemories()}
          {activeTab === 'interactions' && renderInteractions()}
          {activeTab === 'reminders' && renderReminders()}
        </div>
      </div>

      {/* Modals */}
      {showAddContact && (
        <div style={styles.modal} onClick={() => setShowAddContact(false)}>
          <div style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <div style={styles.modalHeader}>
              <h3>Add New Contact</h3>
              <button onClick={() => setShowAddContact(false)} style={styles.closeButton}>✕</button>
            </div>
            <div style={styles.modalBody}>
              <input
                type="text"
                placeholder="Name *"
                value={newContact.name}
                onChange={(e) => setNewContact({...newContact, name: e.target.value})}
                style={styles.input}
              />
              <input
                type="email"
                placeholder="Email *"
                value={newContact.email}
                onChange={(e) => setNewContact({...newContact, email: e.target.value})}
                style={styles.input}
              />
              <input
                type="text"
                placeholder="Company"
                value={newContact.company}
                onChange={(e) => setNewContact({...newContact, company: e.target.value})}
                style={styles.input}
              />
              <textarea
                placeholder="Notes"
                value={newContact.notes}
                onChange={(e) => setNewContact({...newContact, notes: e.target.value})}
                style={styles.textarea}
              />
              <button onClick={addContact} style={styles.submitButton}>Add Contact</button>
            </div>
          </div>
        </div>
      )}

      {showAddMemory && (
        <div style={styles.modal} onClick={() => setShowAddMemory(false)}>
          <div style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <div style={styles.modalHeader}>
              <h3>Add Memory</h3>
              <button onClick={() => setShowAddMemory(false)} style={styles.closeButton}>✕</button>
            </div>
            <div style={styles.modalBody}>
              <input
                type="text"
                placeholder="Contact Name *"
                value={newMemory.contactName}
                onChange={(e) => setNewMemory({...newMemory, contactName: e.target.value})}
                style={styles.input}
              />
              <textarea
                placeholder="Memory Summary *"
                value={newMemory.summary}
                onChange={(e) => setNewMemory({...newMemory, summary: e.target.value})}
                style={styles.textarea}
              />
              <input
                type="text"
                placeholder="Location"
                value={newMemory.location}
                onChange={(e) => setNewMemory({...newMemory, location: e.target.value})}
                style={styles.input}
              />
              <input
                type="date"
                placeholder="Date"
                value={newMemory.date}
                onChange={(e) => setNewMemory({...newMemory, date: e.target.value})}
                style={styles.input}
              />
              <button onClick={addMemory} style={styles.submitButton}>Add Memory</button>
            </div>
          </div>
        </div>
      )}

      {showAddReminder && (
        <div style={styles.modal} onClick={() => setShowAddReminder(false)}>
          <div style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <div style={styles.modalHeader}>
              <h3>Add Reminder</h3>
              <button onClick={() => setShowAddReminder(false)} style={styles.closeButton}>✕</button>
            </div>
            <div style={styles.modalBody}>
              <select
                value={newReminder.contactId}
                onChange={(e) => setNewReminder({...newReminder, contactId: e.target.value})}
                style={styles.input}
              >
                <option value="">Select Contact</option>
                {contacts.map(contact => (
                  <option key={contact.id} value={contact.id}>{contact.name}</option>
                ))}
              </select>
              <input
                type="text"
                placeholder="Reminder Title *"
                value={newReminder.title}
                onChange={(e) => setNewReminder({...newReminder, title: e.target.value})}
                style={styles.input}
              />
              <input
                type="date"
                placeholder="Due Date *"
                value={newReminder.dueDate}
                onChange={(e) => setNewReminder({...newReminder, dueDate: e.target.value})}
                style={styles.input}
              />
              <textarea
                placeholder="Description"
                value={newReminder.description}
                onChange={(e) => setNewReminder({...newReminder, description: e.target.value})}
                style={styles.textarea}
              />
              <button onClick={addReminder} style={styles.submitButton}>Add Reminder</button>
            </div>
          </div>
        </div>
      )}

      {showAddInteraction && (
        <div style={styles.modal} onClick={() => setShowAddInteraction(false)}>
          <div style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <div style={styles.modalHeader}>
              <h3>Add Interaction</h3>
              <button onClick={() => setShowAddInteraction(false)} style={styles.closeButton}>✕</button>
            </div>
            <div style={styles.modalBody}>
              <select
                value={newInteraction.contactId}
                onChange={(e) => setNewInteraction({...newInteraction, contactId: e.target.value})}
                style={styles.input}
              >
                <option value="">Select Contact</option>
                {contacts.map(contact => (
                  <option key={contact.id} value={contact.id}>{contact.name}</option>
                ))}
              </select>
              <select
                value={newInteraction.type}
                onChange={(e) => setNewInteraction({...newInteraction, type: e.target.value as any})}
                style={styles.input}
              >
                <option value="meeting">Meeting</option>
                <option value="call">Call</option>
                <option value="email">Email</option>
                <option value="message">Message</option>
                <option value="social">Social</option>
              </select>
              <textarea
                placeholder="Description *"
                value={newInteraction.description}
                onChange={(e) => setNewInteraction({...newInteraction, description: e.target.value})}
                style={styles.textarea}
              />
              <button onClick={addInteraction} style={styles.submitButton}>Add Interaction</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Styles
const styles = {
  container: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    minHeight: '100vh',
    width: '100%',
    maxWidth: '100vw',
    color: 'white',
    padding: 'clamp(1rem, 4vw, 2rem)',
    boxSizing: 'border-box' as const,
    overflow: 'auto',
  },
  wrapper: {
    maxWidth: '1400px',
    margin: '0 auto',
    width: '100%',
    height: '100%',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '2rem',
    width: '100%',
    flexWrap: 'wrap' as const,
    gap: '1rem',
  },
  backButton: {
    padding: '0.75rem 1.5rem',
    background: 'rgba(255, 255, 255, 0.2)',
    border: 'none',
    borderRadius: '0.5rem',
    color: 'white',
    cursor: 'pointer',
    fontSize: '0.9rem',
  },
  title: {
    fontSize: 'clamp(1.5rem, 4vw, 2rem)',
    fontWeight: 'bold',
    margin: 0,
    flex: '1 1 auto',
    textAlign: 'center' as const,
    minWidth: '200px',
  },
  headerActions: {
    display: 'flex',
    gap: '1rem',
    flexWrap: 'wrap' as const,
    alignItems: 'center',
  },
  detailsButton: {
    padding: '0.75rem 1.5rem',
    background: 'rgba(255, 255, 255, 0.2)',
    border: 'none',
    borderRadius: '0.5rem',
    color: 'white',
    cursor: 'pointer',
    fontSize: '0.9rem',
  },
  notification: {
    background: 'rgba(76, 175, 80, 0.9)',
    color: 'white',
    padding: '1rem',
    borderRadius: '0.5rem',
    marginBottom: '1rem',
    textAlign: 'center' as const,
    fontSize: '0.9rem',
    fontWeight: 'bold',
    boxShadow: '0 2px 10px rgba(0, 0, 0, 0.2)',
  },
  tabContainer: {
    display: 'flex',
    gap: '0.5rem',
    marginBottom: '2rem',
    flexWrap: 'wrap' as const,
  },
  tab: {
    padding: '0.75rem 1.5rem',
    background: 'rgba(255, 255, 255, 0.1)',
    border: 'none',
    borderRadius: '0.5rem',
    color: 'white',
    cursor: 'pointer',
    fontSize: '0.9rem',
    transition: 'all 0.3s ease',
  },
  activeTab: {
    background: 'rgba(255, 255, 255, 0.3)',
    transform: 'translateY(-2px)',
  },
  contentContainer: {
    background: 'rgba(255, 255, 255, 0.1)',
    borderRadius: '1rem',
    padding: 'clamp(1rem, 3vw, 2rem)',
    minHeight: 'clamp(400px, 60vh, 500px)',
    width: '100%',
    maxWidth: '100%',
    boxSizing: 'border-box' as const,
    overflow: 'auto',
  },
  dashboardGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(min(200px, 100%), 1fr))',
    gap: '1rem',
    width: '100%',
    maxWidth: '100%',
  },
  statCard: {
    background: 'rgba(255, 255, 255, 0.15)',
    borderRadius: '0.75rem',
    padding: '1.5rem',
    textAlign: 'center' as const,
  },
  statTitle: {
    fontSize: '0.9rem',
    opacity: 0.8,
    margin: '0 0 0.5rem 0',
  },
  statValue: {
    fontSize: '2rem',
    fontWeight: 'bold',
    margin: '0.5rem 0',
  },
  statSubtext: {
    fontSize: '0.8rem',
    opacity: 0.7,
  },
  sectionHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '1.5rem',
  },
  sectionTitle: {
    fontSize: '1.5rem',
    margin: 0,
  },
  addButton: {
    padding: '0.75rem 1.5rem',
    background: 'linear-gradient(135deg, #505081, #0F0E47)',
    border: 'none',
    borderRadius: '0.5rem',
    color: 'white',
    cursor: 'pointer',
    fontSize: '0.9rem',
  },
  itemsList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '1rem',
  },
  contactCard: {
    background: 'rgba(255, 255, 255, 0.1)',
    borderRadius: '0.75rem',
    padding: 'clamp(1rem, 3vw, 1.5rem)',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    flexWrap: 'wrap' as const,
    gap: '1rem',
  },
  contactInfo: {
    flex: '1 1 auto',
    minWidth: '250px',
  },
  contactName: {
    fontSize: '1.1rem',
    fontWeight: 'bold',
    marginBottom: '0.5rem',
  },
  contactDetails: {
    opacity: 0.8,
    marginBottom: '0.5rem',
  },
  contactTags: {
    display: 'flex',
    gap: '0.25rem',
    flexWrap: 'wrap' as const,
  },
  tag: {
    background: 'rgba(255, 255, 255, 0.2)',
    padding: '0.25rem 0.5rem',
    borderRadius: '1rem',
    fontSize: '0.75rem',
  },
  contactActions: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
  priorityBadge: {
    padding: '0.25rem 0.75rem',
    borderRadius: '1rem',
    fontSize: '0.75rem',
    color: 'white',
    fontWeight: 'bold',
  },
  memoryCard: {
    background: 'rgba(255, 255, 255, 0.1)',
    borderRadius: '0.75rem',
    padding: 'clamp(1rem, 3vw, 1.5rem)',
    width: '100%',
    boxSizing: 'border-box' as const,
  },
  memoryHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '0.75rem',
  },
  memoryDate: {
    opacity: 0.7,
    fontSize: '0.9rem',
  },
  memorySummary: {
    marginBottom: '0.75rem',
    lineHeight: '1.5',
  },
  memoryLocation: {
    opacity: 0.8,
    fontSize: '0.9rem',
    marginBottom: '0.75rem',
  },
  memoryTags: {
    display: 'flex',
    gap: '0.25rem',
    flexWrap: 'wrap' as const,
  },
  interactionCard: {
    background: 'rgba(255, 255, 255, 0.1)',
    borderRadius: '0.75rem',
    padding: 'clamp(1rem, 3vw, 1.5rem)',
    width: '100%',
    boxSizing: 'border-box' as const,
  },
  interactionHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '0.5rem',
  },
  interactionDate: {
    opacity: 0.7,
    fontSize: '0.9rem',
  },
  interactionType: {
    opacity: 0.8,
    fontSize: '0.9rem',
    marginBottom: '0.5rem',
    textTransform: 'capitalize' as const,
  },
  interactionDescription: {
    marginBottom: '0.5rem',
    lineHeight: '1.5',
  },
  followUpRequired: {
    background: 'rgba(255, 165, 0, 0.3)',
    padding: '0.5rem',
    borderRadius: '0.5rem',
    fontSize: '0.9rem',
  },
  reminderCard: {
    background: 'rgba(255, 255, 255, 0.1)',
    borderRadius: '0.75rem',
    padding: 'clamp(1rem, 3vw, 1.5rem)',
    width: '100%',
    boxSizing: 'border-box' as const,
  },
  reminderHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '0.75rem',
  },
  reminderDate: {
    opacity: 0.7,
    fontSize: '0.9rem',
  },
  reminderDescription: {
    marginBottom: '0.75rem',
    lineHeight: '1.5',
  },
  reminderContact: {
    opacity: 0.8,
    fontSize: '0.9rem',
    marginBottom: '1rem',
  },
  reminderToggle: {
    padding: '0.5rem 1rem',
    border: 'none',
    borderRadius: '0.5rem',
    color: 'white',
    cursor: 'pointer',
    fontSize: '0.8rem',
    fontWeight: 'bold',
  },
  chatContainer: {
    background: 'rgba(255, 255, 255, 0.05)',
    borderRadius: '1rem',
    padding: 'clamp(1rem, 3vw, 1.5rem)',
    height: 'clamp(400px, 60vh, 500px)',
    maxHeight: '70vh',
    display: 'flex',
    flexDirection: 'column' as const,
    position: 'relative' as const,
    width: '100%',
    boxSizing: 'border-box' as const,
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
    background: 'white',
    borderRadius: '1rem',
    padding: 0,
    width: '90%',
    maxWidth: '500px',
    maxHeight: '90vh',
    overflow: 'auto',
    color: '#333',
  },
  modalHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1.5rem',
    borderBottom: '1px solid #eee',
  },
  modalBody: {
    padding: '1.5rem',
  },
  closeButton: {
    background: 'none',
    border: 'none',
    fontSize: '1.2rem',
    cursor: 'pointer',
    color: '#666',
  },
  input: {
    width: '100%',
    padding: '0.75rem',
    borderRadius: '0.5rem',
    border: '1px solid #ddd',
    marginBottom: '1rem',
    fontSize: '1rem',
  },
  textarea: {
    width: '100%',
    padding: '0.75rem',
    borderRadius: '0.5rem',
    border: '1px solid #ddd',
    marginBottom: '1rem',
    fontSize: '1rem',
    minHeight: '100px',
    resize: 'vertical' as const,
  },
  submitButton: {
    width: '100%',
    padding: '0.75rem',
    background: 'linear-gradient(135deg, #505081, #0F0E47)',
    border: 'none',
    borderRadius: '0.5rem',
    color: 'white',
    cursor: 'pointer',
    fontSize: '1rem',
    fontWeight: 'bold',
  }
};

export default RelationshipAgent;