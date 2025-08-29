import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { supabase } from '../lib/supabase';
import AgentAdmin from './AgentAdmin';

interface Agent {
  id: string;
  name: string;
  description: string;
  short_description: string;
  category: string;
  price: number;
  rating: number;
  downloads: number;
  icon: string;
  screenshots: string[];
  features: string[];
  developer: string;
  version: string;
  created_at: string;
  updated_at: string;
  tags: string[];
  is_featured: boolean;
  is_premium: boolean;
  isActive?: boolean;
}

interface AgentStoreProps {
  onBack: () => void;
  onSelectAgent?: (agentId: string) => void;
}

const AgentStore: React.FC<AgentStoreProps> = ({ onBack, onSelectAgent }) => {
  const { user } = useAuth();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('featured');
  const [showAdmin, setShowAdmin] = useState(false);
  const [showActiveOnly, setShowActiveOnly] = useState(false);
  const [activeAgents, setActiveAgents] = useState<Set<string>>(new Set([
    'agent_mailerpanda', 
    'agent_addtocalendar', 
    'agent_finance', 
    'agent_relationship',
    'agent_research'
  ])); // Default active agents

  const categories = ['All', 'Productivity', 'Communication', 'Analytics', 'Marketing', 'Development', 'Creative', 'Finance', 'Relationship'];

  // Function to toggle agent active status
  const toggleAgentStatus = (agentId: string) => {
    setActiveAgents(prev => {
      const newSet = new Set(prev);
      if (newSet.has(agentId)) {
        newSet.delete(agentId);
      } else {
        newSet.add(agentId);
      }
      return newSet;
    });
  };

  // Mock data for initial display (includes your existing agents)
  const mockAgents: Agent[] = [
    // HushMCP Production Agents - API v2.0.0
    {
      id: 'agent_mailerpanda',
      name: 'MailerPanda Agent',
      description: 'AI-powered email campaign creation with human-in-the-loop approval workflows and mass distribution capabilities. Create personalized marketing emails, newsletters, and automated campaigns with advanced AI generation and consent management. Features interactive approval mode for enhanced control.',
      short_description: 'AI email campaigns with approval workflows',
      category: 'Communication',
      price: 0.00,
      rating: 4.9,
      downloads: 78900,
      icon: '🐼',
      screenshots: [],
      features: ['AI Content Generation', 'Human-in-Loop Approval', 'Mass Distribution', 'Campaign Analytics', 'Template Library', 'Consent Management', 'Interactive Mode'],
      developer: 'HushMCP',
      version: '3.0.0',
      created_at: '2024-02-15',
      updated_at: '2025-01-19',
      tags: ['email', 'campaigns', 'ai', 'marketing', 'automation', 'privacy'],
      is_featured: true,
      is_premium: false,
      isActive: true
    },
    {
      id: 'agent_addtocalendar',
      name: 'AddToCalendar Agent',
      description: 'Advanced email-to-calendar automation agent that processes emails to extract event information and creates Google Calendar events automatically. Features comprehensive email analysis, confidence scoring, and seamless Google OAuth integration with privacy-first design.',
      short_description: 'Email→Calendar event extraction and automation',
      category: 'Productivity',
      price: 0.00,
      rating: 4.8,
      downloads: 65400,
      icon: '📅',
      screenshots: [],
      features: ['Email Event Extraction', 'Google Calendar Integration', 'Confidence Scoring', 'Batch Processing', 'OAuth 2.0 Support', 'Real-time Sync', 'Privacy-First Design'],
      developer: 'HushMCP',
      version: '1.1.0',
      created_at: '2024-03-10',
      updated_at: '2025-01-19',
      tags: ['calendar', 'email', 'automation', 'google', 'events', 'productivity'],
      is_featured: true,
      is_premium: false,
      isActive: true
    },
    {
      id: 'hush-hitl',
      name: 'HITL Chat Agent',
      description: 'Human-in-the-Loop conversational AI agent for complex problem solving, research assistance, and intelligent task automation with human oversight. Enhanced with approval workflows and context awareness.',
      short_description: 'AI assistant with human oversight',
      category: 'Communication',
      price: 0.00,
      rating: 4.7,
      downloads: 32400,
      icon: '💬',
      screenshots: [],
      features: ['Conversational AI', 'Human Oversight', 'Approval Workflows', 'Task Automation', 'Research Assistant', 'Context Awareness'],
      developer: 'HushMCP',
      version: '1.5.0',
      created_at: '2024-01-20',
      updated_at: '2024-08-19',
      tags: ['chat', 'ai', 'assistant', 'automation', 'research'],
      is_featured: false,
      is_premium: false
    },
    // New specialized agents with HITL integration
    {
      id: 'agent_finance',
      name: 'Personal Finance Manager',
      description: 'Intelligent financial management system with AI-powered insights and HITL integration. Track expenses, manage budgets, set financial goals, and receive personalized recommendations. Features transaction categorization, budget analysis, goal tracking, and seamless integration with HITL chat for financial guidance.',
      short_description: 'AI financial management with intelligent insights',
      category: 'Finance',
      price: 0.00,
      rating: 4.9,
      downloads: 1200,
      icon: '💰',
      screenshots: [],
      features: ['Transaction Tracking', 'Budget Management', 'Goal Setting', 'AI Insights', 'HITL Integration', 'Financial Reports', 'Expense Categorization'],
      developer: 'HushMCP',
      version: '1.0.0',
      created_at: '2024-01-20',
      updated_at: '2024-01-20',
      tags: ['finance', 'budgeting', 'ai', 'insights', 'hitl', 'money'],
      is_featured: true,
      is_premium: false,
      isActive: true
    },
    {
      id: 'agent_relationship',
      name: 'Relationship Manager',
      description: 'Comprehensive relationship management platform with AI-powered networking insights. Track contacts, manage interactions, set reminders, and get personalized relationship building strategies. Features contact profiling, interaction history, automated follow-ups, and HITL integration for relationship advice.',
      short_description: 'AI relationship management and networking insights',
      category: 'Relationship',
      price: 0.00,
      rating: 4.8,
      downloads: 890,
      icon: '🤝',
      screenshots: [],
      features: ['Contact Management', 'Interaction Tracking', 'Smart Reminders', 'Relationship Insights', 'HITL Integration', 'Network Analysis', 'Follow-up Automation'],
      developer: 'HushMCP',
      version: '2.0.0',
      created_at: '2024-01-20',
      updated_at: '2025-01-23',
      tags: ['relationships', 'networking', 'crm', 'ai', 'hitl', 'contacts'],
      is_featured: true,
      is_premium: false,
      isActive: true
    },
    {
      id: 'agent_research',
      name: 'Research Assistant',
      description: 'AI-powered academic research assistant with arXiv integration, PDF processing, and intelligent note-taking. Search and analyze research papers, generate AI summaries, process text snippets with custom instructions, and manage research notes with tags. Perfect for academics, students, and researchers.',
      short_description: 'AI research companion for academic papers',
      category: 'Productivity',
      price: 0.00,
      rating: 4.9,
      downloads: 450,
      icon: '🔬',
      screenshots: [],
      features: ['ArXiv Search', 'PDF Upload & Processing', 'AI Paper Summaries', 'Snippet Processing', 'Note Management', 'Tag System', 'HITL Integration'],
      developer: 'HushMCP',
      version: '1.0.0',
      created_at: '2025-01-23',
      updated_at: '2025-01-23',
      tags: ['research', 'academic', 'arxiv', 'ai', 'notes', 'pdf'],
      is_featured: true,
      is_premium: false,
      isActive: true
    },
    // Third-party marketplace agents
    {
      id: '1',
      name: 'EmailBot Pro',
      description: 'Advanced email automation and response management system with AI-powered insights.',
      short_description: 'Automate your email workflow with AI',
      category: 'Communication',
      price: 29.99,
      rating: 4.8,
      downloads: 15420,
      icon: '📧',
      screenshots: [],
      features: ['AI Response Generation', 'Smart Filtering', 'Analytics Dashboard', 'Multi-account Support'],
      developer: 'HushTech',
      version: '2.1.0',
      created_at: '2024-01-15',
      updated_at: '2024-08-01',
      tags: ['email', 'automation', 'ai', 'productivity'],
      is_featured: true,
      is_premium: true
    },
    {
      id: '2',
      name: 'DataViz Master',
      description: 'Create stunning data visualizations and interactive dashboards with ease.',
      short_description: 'Beautiful data visualization made simple',
      category: 'Analytics',
      price: 49.99,
      rating: 4.9,
      downloads: 8750,
      icon: '📊',
      screenshots: [],
      features: ['Interactive Charts', 'Real-time Data', 'Export Options', 'Team Collaboration'],
      developer: 'ChartCorp',
      version: '1.5.2',
      created_at: '2024-02-20',
      updated_at: '2024-07-15',
      tags: ['charts', 'analytics', 'visualization', 'data'],
      is_featured: true,
      is_premium: true
    },
    {
      id: '3',
      name: 'Social Scheduler',
      description: 'Schedule and manage your social media posts across multiple platforms.',
      short_description: 'Schedule posts across all platforms',
      category: 'Marketing',
      price: 19.99,
      rating: 4.6,
      downloads: 23100,
      icon: '📱',
      screenshots: [],
      features: ['Multi-platform Support', 'Content Calendar', 'Analytics', 'Team Management'],
      developer: 'SocialTech',
      version: '3.0.1',
      created_at: '2024-01-10',
      updated_at: '2024-08-10',
      tags: ['social media', 'scheduling', 'marketing', 'automation'],
      is_featured: false,
      is_premium: false
    },
    {
      id: '4',
      name: 'Code Assistant',
      description: 'AI-powered coding companion that helps with code generation, debugging, and optimization.',
      short_description: 'Your AI coding companion',
      category: 'Development',
      price: 39.99,
      rating: 4.7,
      downloads: 12300,
      icon: '💻',
      screenshots: [],
      features: ['Code Generation', 'Bug Detection', 'Performance Optimization', 'Multiple Languages'],
      developer: 'DevTools Inc',
      version: '1.8.0',
      created_at: '2024-03-01',
      updated_at: '2024-08-05',
      tags: ['coding', 'ai', 'development', 'debugging'],
      is_featured: true,
      is_premium: true
    },
    {
      id: '5',
      name: 'Task Organizer',
      description: 'Smart task management with AI-powered prioritization and scheduling.',
      short_description: 'Organize tasks with AI intelligence',
      category: 'Productivity',
      price: 15.99,
      rating: 4.5,
      downloads: 18900,
      icon: '✅',
      screenshots: [],
      features: ['Smart Prioritization', 'Calendar Integration', 'Team Collaboration', 'Progress Tracking'],
      developer: 'ProductiveTech',
      version: '2.3.1',
      created_at: '2024-01-25',
      updated_at: '2024-07-20',
      tags: ['tasks', 'productivity', 'organization', 'ai'],
      is_featured: false,
      is_premium: false
    },
    {
      id: '6',
      name: 'Creative Studio',
      description: 'AI-powered design tool for creating stunning graphics, logos, and marketing materials.',
      short_description: 'Create stunning designs with AI',
      category: 'Creative',
      price: 34.99,
      rating: 4.8,
      downloads: 9650,
      icon: '🎨',
      screenshots: [],
      features: ['AI Design Generation', 'Template Library', 'Brand Kit', 'Export Options'],
      developer: 'CreativeAI',
      version: '1.2.0',
      created_at: '2024-04-01',
      updated_at: '2024-08-12',
      tags: ['design', 'creative', 'ai', 'graphics'],
      is_featured: true,
      is_premium: true
    }
  ];

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    setLoading(true);
    try {
      // Try to load from Supabase first
      if (supabase) {
        const { data, error } = await supabase
          .from('agents')
          .select('*')
          .order('created_at', { ascending: false });
        
        if (error) {
          console.warn('Supabase error, using mock data:', error);
          // Fall back to mock data if Supabase fails
          setTimeout(() => {
            setAgents(mockAgents);
            setLoading(false);
          }, 1000);
        } else if (data && data.length > 0) {
          // Use Supabase data if available
          setAgents(data);
          setLoading(false);
        } else {
          // No data in Supabase, use mock data
          setTimeout(() => {
            setAgents(mockAgents);
            setLoading(false);
          }, 1000);
        }
      } else {
        // Supabase not configured, use mock data
        console.warn('Supabase not configured, using mock data');
        setTimeout(() => {
          setAgents(mockAgents);
          setLoading(false);
        }, 1000);
      }
    } catch (error) {
      console.error('Error loading agents:', error);
      // Fall back to mock data on any error
      setTimeout(() => {
        setAgents(mockAgents);
        setLoading(false);
      }, 1000);
    }
  };

  const filteredAgents = agents.filter(agent => {
    const matchesCategory = selectedCategory === 'All' || agent.category === selectedCategory;
    const matchesSearch = agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         agent.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         agent.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesActiveFilter = !showActiveOnly || activeAgents.has(agent.id);
    return matchesCategory && matchesSearch && matchesActiveFilter;
  });

  const sortedAgents = [...filteredAgents].sort((a, b) => {
    switch (sortBy) {
      case 'featured':
        if (a.is_featured && !b.is_featured) return -1;
        if (!a.is_featured && b.is_featured) return 1;
        return b.rating - a.rating;
      case 'rating':
        return b.rating - a.rating;
      case 'downloads':
        return b.downloads - a.downloads;
      case 'price_low':
        return a.price - b.price;
      case 'price_high':
        return b.price - a.price;
      case 'newest':
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      default:
        return 0;
    }
  });

  const handlePurchase = async (agent: Agent) => {
    if (!user) {
      alert('Please sign in to purchase agents');
      return;
    }

    try {
      // Check if user already owns this agent
      if (supabase) {
        const { data: existingPurchase } = await supabase
          .from('agent_purchases')
          .select('id')
          .eq('user_id', user.id)
          .eq('agent_id', agent.id)
          .single();

        if (existingPurchase) {
          alert('You already own this agent!');
          return;
        }

        // Simulate payment process (in real app, integrate with Stripe/PayPal)
        const confirmed = confirm(
          agent.price === 0 
            ? `Get ${agent.name} for free?\n\nThis will add the agent to your collection.`
            : `Purchase ${agent.name} for $${agent.price}?\n\nThis will add the agent to your collection.`
        );

        if (!confirmed) return;

        // Record the purchase
        const { error: purchaseError } = await supabase
          .from('agent_purchases')
          .insert({
            user_id: user.id,
            agent_id: agent.id,
            purchase_price: agent.price
          });

        if (purchaseError) {
          console.error('Purchase error:', purchaseError);
          alert('Failed to complete purchase. Please try again.');
          return;
        }

        // Update agent download count
        const { error: updateError } = await supabase
          .from('agents')
          .update({ downloads: agent.downloads + 1 })
          .eq('id', agent.id);

        if (updateError) {
          console.warn('Failed to update download count:', updateError);
        }

        alert(`Successfully purchased ${agent.name}! 🎉`);
        
        // Refresh agents to update download count
        loadAgents();
        
        // Navigate to the agent if it's implemented
        if (onSelectAgent && (agent.id === 'agent_mailerpanda' || agent.id === 'agent_addtocalendar' || agent.id === 'agent_finance' || agent.id === 'agent_relationship')) {
          setTimeout(() => {
            onSelectAgent(agent.id);
          }, 1000);
        }
      } else {
        // Fallback for when Supabase is not configured
        const confirmed = confirm(
          agent.price === 0 
            ? `Get ${agent.name} for free?\n\n(Demo mode - no actual payment required)`
            : `Purchase ${agent.name} for $${agent.price}?\n\n(Demo mode - no actual payment required)`
        );
        
        if (confirmed) {
          alert(`Successfully ${agent.price === 0 ? 'got' : 'purchased'} ${agent.name}! 🎉\n\n(This is a demo - no actual payment was processed)`);
          
          // Navigate to the agent if it's implemented
          if (onSelectAgent && (agent.id === 'agent_mailerpanda' || agent.id === 'agent_addtocalendar' || agent.id === 'agent_finance' || agent.id === 'agent_relationship')) {
            setTimeout(() => {
              onSelectAgent(agent.id);
            }, 1000);
          }
        }
      }
    } catch (error) {
      console.error('Error during purchase:', error);
      alert('An error occurred during purchase. Please try again.');
    }
  };

  const styles = {
    container: {
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      minHeight: '100vh',
      width: '100%',
      maxWidth: '100vw',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: 'clamp(1rem, 4vw, 2rem)',
      paddingTop: 'clamp(4rem, 8vh, 8rem)',
      boxSizing: 'border-box' as const,
      overflow: 'auto',
    },
    header: {
      textAlign: 'center' as const,
      marginBottom: '3rem',
      color: 'white',
      maxWidth: '1200px',
      margin: '0 auto 3rem auto',
    },
    title: {
      fontSize: 'clamp(2rem, 6vw, 3rem)',
      fontWeight: '700',
      marginBottom: '1rem',
      background: 'linear-gradient(45deg, #fff, #f0f8ff)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      backgroundClip: 'text',
    },
    subtitle: {
      fontSize: 'clamp(1rem, 3vw, 1.2rem)',
      opacity: 0.9,
      maxWidth: '600px',
      margin: '0 auto',
      lineHeight: '1.5',
    },
    controls: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: '2rem',
      flexWrap: 'wrap' as const,
      gap: '1rem',
      background: 'rgba(255, 255, 255, 0.1)',
      backdropFilter: 'blur(10px)',
      padding: 'clamp(1rem, 3vw, 1.5rem)',
      borderRadius: '1rem',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      maxWidth: '100%',
      boxSizing: 'border-box' as const,
    },
    searchContainer: {
      position: 'relative' as const,
      minWidth: 'min(300px, 100%)',
      flex: '1 1 300px',
      maxWidth: '400px',
    },
    searchInput: {
      width: '100%',
      padding: '0.75rem 1rem 0.75rem 3rem',
      borderRadius: '0.75rem',
      border: 'none',
      background: 'rgba(255, 255, 255, 0.9)',
      fontSize: '1rem',
      outline: 'none',
      transition: 'all 0.3s ease',
    },
    searchIcon: {
      position: 'absolute' as const,
      left: '1rem',
      top: '50%',
      transform: 'translateY(-50%)',
      color: '#666',
      fontSize: '1.2rem',
    },
    categories: {
      display: 'flex',
      gap: '0.5rem',
      flexWrap: 'wrap' as const,
      flex: '1 1 auto',
      justifyContent: 'center',
    },
    categoryButton: {
      padding: '0.5rem 1rem',
      borderRadius: '1.5rem',
      border: 'none',
      background: 'rgba(255, 255, 255, 0.2)',
      color: 'white',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      fontSize: '0.9rem',
      fontWeight: '500',
    },
    categoryButtonActive: {
      background: 'rgba(255, 255, 255, 0.9)',
      color: '#667eea',
    },
    sortSelect: {
      padding: '0.75rem',
      borderRadius: '0.5rem',
      border: 'none',
      background: 'rgba(255, 255, 255, 0.9)',
      outline: 'none',
      cursor: 'pointer',
    },
    grid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill, minmax(min(350px, 100%), 1fr))',
      gap: 'clamp(1rem, 3vw, 2rem)',
      marginBottom: '3rem',
      maxWidth: '100%',
      width: '100%',
    },
    agentCard: {
      background: 'rgba(255, 255, 255, 0.95)',
      borderRadius: '1.5rem',
      padding: 'clamp(1.5rem, 4vw, 2rem)',
      boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
      transition: 'all 0.3s ease',
      cursor: 'pointer',
      border: '1px solid rgba(255, 255, 255, 0.3)',
      width: '100%',
      boxSizing: 'border-box' as const,
      maxWidth: '100%',
    },
    agentCardHover: {
      transform: 'translateY(-10px)',
      boxShadow: '0 30px 60px rgba(0, 0, 0, 0.15)',
    },
    agentIcon: {
      fontSize: '3rem',
      marginBottom: '1rem',
      display: 'block',
    },
    agentName: {
      fontSize: 'clamp(1.2rem, 3vw, 1.5rem)',
      fontWeight: '700',
      marginBottom: '0.5rem',
      color: '#333',
      wordWrap: 'break-word' as const,
    },
    agentDescription: {
      fontSize: '0.9rem',
      color: '#666',
      marginBottom: '1rem',
      lineHeight: '1.5',
    },
    agentMeta: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: '1rem',
      flexWrap: 'wrap' as const,
      gap: '0.5rem',
    },
    rating: {
      display: 'flex',
      alignItems: 'center',
      gap: '0.25rem',
      color: '#ffa500',
      fontSize: '0.9rem',
    },
    downloads: {
      fontSize: '0.8rem',
      color: '#888',
    },
    price: {
      fontSize: '1.2rem',
      fontWeight: '700',
      color: '#667eea',
    },
    features: {
      display: 'flex',
      flexWrap: 'wrap' as const,
      gap: '0.5rem',
      marginBottom: '1rem',
    },
    featureTag: {
      background: 'linear-gradient(45deg, #667eea, #764ba2)',
      color: 'white',
      padding: '0.25rem 0.75rem',
      borderRadius: '1rem',
      fontSize: '0.8rem',
      fontWeight: '500',
    },
    purchaseButton: {
      width: '100%',
      padding: '0.75rem',
      borderRadius: '0.75rem',
      border: 'none',
      background: 'linear-gradient(45deg, #667eea, #764ba2)',
      color: 'white',
      fontSize: '1rem',
      fontWeight: '600',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
    },
    backButton: {
      position: 'absolute' as const,
      top: 'clamp(1rem, 3vh, 2rem)',
      left: 'clamp(1rem, 3vw, 2rem)',
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
      padding: '0.75rem 1.5rem',
      background: 'rgba(255, 255, 255, 0.2)',
      backdropFilter: 'blur(10px)',
      border: '1px solid rgba(255, 255, 255, 0.3)',
      borderRadius: '2rem',
      color: 'white',
      textDecoration: 'none',
      fontSize: '0.9rem',
      fontWeight: '500',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      zIndex: 10,
    },
    loadingContainer: {
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '400px',
    },
    loadingSpinner: {
      width: '3rem',
      height: '3rem',
      border: '3px solid rgba(255, 255, 255, 0.3)',
      borderTop: '3px solid white',
      borderRadius: '50%',
      animation: 'spin 1s linear infinite',
    },
    toggleContainer: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: '1rem',
      padding: '0.75rem',
      borderRadius: '0.75rem',
      background: 'rgba(102, 126, 234, 0.1)',
      border: '1px solid rgba(102, 126, 234, 0.2)',
      width: '100%',
      boxSizing: 'border-box' as const,
    },
    toggleLabel: {
      fontSize: '0.9rem',
      fontWeight: '600',
      color: '#667eea',
    },
    toggleSwitch: {
      position: 'relative' as const,
      width: '50px',
      height: '24px',
      background: '#ccc',
      borderRadius: '24px',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
    },
    toggleSwitchActive: {
      background: '#667eea',
    },
    toggleSlider: {
      position: 'absolute' as const,
      top: '2px',
      left: '2px',
      width: '20px',
      height: '20px',
      background: 'white',
      borderRadius: '50%',
      transition: 'all 0.3s ease',
      transform: 'translateX(0)',
    },
    toggleSliderActive: {
      transform: 'translateX(26px)',
    },
    featuredBadge: {
      position: 'absolute' as const,
      top: '1rem',
      right: '1rem',
      background: 'linear-gradient(45deg, #ffa500, #ff6b35)',
      color: 'white',
      padding: '0.25rem 0.75rem',
      borderRadius: '1rem',
      fontSize: '0.7rem',
      fontWeight: '600',
      textTransform: 'uppercase' as const,
    },
    premiumBadge: {
      position: 'absolute' as const,
      top: '1rem',
      left: '1rem',
      background: 'linear-gradient(45deg, #gold, #darkgoldenrod)',
      color: 'white',
      padding: '0.25rem 0.75rem',
      borderRadius: '1rem',
      fontSize: '0.7rem',
      fontWeight: '600',
      textTransform: 'uppercase' as const,
    },
    // Modal styles
    modalOverlay: {
      position: 'fixed' as const,
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.8)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: 1000,
      padding: 'clamp(1rem, 4vw, 2rem)',
    },
    modalContent: {
      background: 'white',
      borderRadius: '1.5rem',
      maxWidth: 'min(600px, 90vw)',
      width: '100%',
      maxHeight: '90vh',
      overflow: 'auto',
      boxShadow: '0 25px 50px rgba(0, 0, 0, 0.25)',
    },
    modalHeader: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'flex-start',
      padding: 'clamp(1.5rem, 4vw, 2rem) clamp(1.5rem, 4vw, 2rem) clamp(0.5rem, 2vw, 1rem)',
      borderBottom: '1px solid #e5e5e5',
      flexWrap: 'wrap' as const,
      gap: '1rem',
    },
    modalTitle: {
      fontSize: 'clamp(1.4rem, 4vw, 1.8rem)',
      fontWeight: '700',
      color: '#333',
      margin: 0,
      wordWrap: 'break-word' as const,
    },
    modalDeveloper: {
      color: '#666',
      fontSize: '1rem',
      margin: '0.25rem 0 0 0',
    },
    modalCloseButton: {
      background: 'none',
      border: 'none',
      fontSize: '2rem',
      color: '#999',
      cursor: 'pointer',
      padding: '0.5rem',
      borderRadius: '50%',
      transition: 'all 0.2s ease',
    },
    modalBody: {
      padding: 'clamp(1.5rem, 4vw, 2rem)',
    },
    modalMeta: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: '1.5rem',
      padding: '1rem',
      background: '#f8f9fa',
      borderRadius: '0.75rem',
    },
    modalRating: {
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
      color: '#ffa500',
      fontSize: '1.1rem',
      fontWeight: '600',
    },
    modalPrice: {
      fontSize: '1.5rem',
      fontWeight: '700',
      color: '#667eea',
    },
    modalDescription: {
      fontSize: '1rem',
      lineHeight: '1.6',
      color: '#555',
      marginBottom: '2rem',
    },
    modalSection: {
      marginBottom: '2rem',
    },
    modalSectionTitle: {
      fontSize: '1.2rem',
      fontWeight: '600',
      color: '#333',
      marginBottom: '1rem',
    },
    modalFeatures: {
      display: 'flex',
      flexDirection: 'column' as const,
      gap: '0.75rem',
    },
    modalFeatureItem: {
      display: 'flex',
      alignItems: 'center',
      gap: '0.75rem',
      fontSize: '1rem',
      color: '#555',
    },
    modalDetails: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
      gap: '0.75rem',
      fontSize: '0.95rem',
      color: '#666',
    },
    modalActions: {
      marginTop: '2rem',
      paddingTop: '1.5rem',
      borderTop: '1px solid #e5e5e5',
      textAlign: 'center' as const,
    },
    addAgentButton: {
      padding: '0.75rem 1.5rem',
      borderRadius: '0.75rem',
      border: 'none',
      background: 'linear-gradient(45deg, #10b981, #059669)',
      color: 'white',
      fontSize: '0.9rem',
      fontWeight: '600',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      whiteSpace: 'nowrap' as const,
    },
  };

  return (
    <div style={styles.container}>
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
      
      <div style={{ maxWidth: '1400px', margin: '0 auto', width: '100%' }}>
        {showAdmin ? (
          <AgentAdmin onBack={() => setShowAdmin(false)} />
        ) : (
          <>
            <button onClick={onBack} style={styles.backButton}>
              ← Back to Dashboard
            </button>

            <div style={styles.header}>
              <h1 style={styles.title}>🤖 Agent Store</h1>
              <p style={styles.subtitle}>
                Discover powerful AI agents to supercharge your workflow. Browse, purchase, and deploy intelligent automation tools.
              </p>
            </div>

          <div style={styles.controls}>
            <div style={styles.searchContainer}>
              <span style={styles.searchIcon}>🔍</span>
              <input
                type="text"
                placeholder="Search agents..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={styles.searchInput}
              />
            </div>

            <div style={styles.categories}>
              {categories.map(category => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  style={{
                    ...styles.categoryButton,
                    ...(selectedCategory === category ? styles.categoryButtonActive : {})
                  }}
                >
                  {category}
                </button>
              ))}
            </div>

            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                style={styles.sortSelect}
              >
                <option value="featured">Featured</option>
                <option value="rating">Highest Rated</option>
                <option value="downloads">Most Downloaded</option>
                <option value="price_low">Price: Low to High</option>
                <option value="price_high">Price: High to Low</option>
                <option value="newest">Newest</option>
              </select>
              
              <button
                onClick={() => setShowActiveOnly(!showActiveOnly)}
                style={{
                  ...styles.categoryButton,
                  ...(showActiveOnly ? styles.categoryButtonActive : {}),
                  minWidth: '120px'
                }}
              >
                {showActiveOnly ? 'Active Only ✓' : 'Show Active Only'}
              </button>
              
              {user && (
                <button
                  onClick={() => setShowAdmin(true)}
                  style={styles.addAgentButton}
                >
                  + Add Agent
                </button>
              )}
            </div>
          </div>

          {loading ? (
        <div style={styles.loadingContainer}>
          <div style={styles.loadingSpinner}></div>
        </div>
      ) : (
        <div style={styles.grid}>
          {sortedAgents.map((agent) => (
            <div
              key={agent.id}
              style={{
                ...styles.agentCard,
                ...(activeAgents.has(agent.id) 
                  ? { 
                      border: '2px solid #667eea',
                      background: 'rgba(102, 126, 234, 0.05)',
                      boxShadow: '0 20px 40px rgba(102, 126, 234, 0.2)'
                    } 
                  : {}
                )
              }}
              onMouseEnter={(e) => {
                Object.assign(e.currentTarget.style, styles.agentCardHover);
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = activeAgents.has(agent.id)
                  ? '0 20px 40px rgba(102, 126, 234, 0.2)'
                  : '0 20px 40px rgba(0, 0, 0, 0.1)';
              }}
              onClick={() => setSelectedAgent(agent)}
            >
              <div style={{ position: 'relative' }}>
                {agent.is_featured && (
                  <span style={styles.featuredBadge}>Featured</span>
                )}
                {agent.is_premium && (
                  <span style={styles.premiumBadge}>Premium</span>
                )}
                {activeAgents.has(agent.id) && (
                  <span style={{
                    ...styles.featuredBadge,
                    top: agent.is_featured ? '3.5rem' : '1rem',
                    background: 'linear-gradient(45deg, #4CAF50, #45a049)',
                  }}>
                    Active
                  </span>
                )}
                
                <span style={styles.agentIcon}>{agent.icon}</span>
                <h3 style={styles.agentName}>{agent.name}</h3>
                <p style={styles.agentDescription}>{agent.short_description}</p>
                
                <div style={styles.agentMeta}>
                  <div style={styles.rating}>
                    <span>⭐</span>
                    <span>{agent.rating}</span>
                  </div>
                  <div style={styles.downloads}>
                    {agent.downloads.toLocaleString()} downloads
                  </div>
                  <div style={styles.price}>
                    {agent.price === 0 ? 'Free' : `$${agent.price}`}
                  </div>
                </div>

                <div style={styles.features}>
                  {agent.features.slice(0, 3).map((feature, index) => (
                    <span key={index} style={styles.featureTag}>
                      {feature}
                    </span>
                  ))}
                </div>

                <div style={styles.toggleContainer}>
                  <span style={styles.toggleLabel}>
                    {activeAgents.has(agent.id) ? 'Active' : 'Inactive'}
                  </span>
                  <div 
                    style={{
                      ...styles.toggleSwitch,
                      ...(activeAgents.has(agent.id) ? styles.toggleSwitchActive : {})
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleAgentStatus(agent.id);
                    }}
                  >
                    <div 
                      style={{
                        ...styles.toggleSlider,
                        ...(activeAgents.has(agent.id) ? styles.toggleSliderActive : {})
                      }}
                    />
                  </div>
                </div>

                <button
                  style={styles.purchaseButton}
                  onClick={(e) => {
                    e.stopPropagation();
                    handlePurchase(agent);
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'scale(1.05)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'scale(1)';
                  }}
                >
                  {agent.price === 0 ? 'Get Free Agent' : 'Get Agent'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {sortedAgents.length === 0 && !loading && (
        <div style={{ textAlign: 'center', color: 'white', padding: '3rem' }}>
          <h3>No agents found</h3>
          <p>Try adjusting your search or category filters.</p>
        </div>
      )}

      {/* Agent Detail Modal */}
      {selectedAgent && (
        <div style={styles.modalOverlay} onClick={() => setSelectedAgent(null)}>
          <div style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <div style={styles.modalHeader}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <span style={{ fontSize: '3rem' }}>{selectedAgent.icon}</span>
                <div>
                  <h2 style={styles.modalTitle}>{selectedAgent.name}</h2>
                  <p style={styles.modalDeveloper}>by {selectedAgent.developer}</p>
                </div>
              </div>
              <button style={styles.modalCloseButton} onClick={() => setSelectedAgent(null)}>
                ×
              </button>
            </div>
            
            <div style={styles.modalBody}>
              <div style={styles.modalMeta}>
                <div style={styles.modalRating}>
                  <span>⭐</span>
                  <span>{selectedAgent.rating}</span>
                  <span style={{ color: '#666', fontSize: '0.9rem' }}>
                    ({selectedAgent.downloads.toLocaleString()} downloads)
                  </span>
                </div>
                <div style={styles.modalPrice}>
                  {selectedAgent.price === 0 ? 'Free' : `$${selectedAgent.price}`}
                </div>
              </div>

              <p style={styles.modalDescription}>{selectedAgent.description}</p>

              <div style={styles.modalSection}>
                <h4 style={styles.modalSectionTitle}>Features</h4>
                <div style={styles.modalFeatures}>
                  {selectedAgent.features.map((feature, index) => (
                    <div key={index} style={styles.modalFeatureItem}>
                      <span style={{ color: '#667eea' }}>✓</span>
                      <span>{feature}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div style={styles.modalSection}>
                <h4 style={styles.modalSectionTitle}>Details</h4>
                <div style={styles.modalDetails}>
                  <div><strong>Version:</strong> {selectedAgent.version}</div>
                  <div><strong>Category:</strong> {selectedAgent.category}</div>
                  <div><strong>Developer:</strong> {selectedAgent.developer}</div>
                  <div><strong>Last Updated:</strong> {new Date(selectedAgent.updated_at).toLocaleDateString()}</div>
                </div>
              </div>

              <div style={styles.modalActions}>
                <button
                  style={{...styles.purchaseButton, fontSize: '1.1rem', padding: '1rem 2rem'}}
                  onClick={() => handlePurchase(selectedAgent)}
                >
                  {selectedAgent.price === 0 ? 'Get Free Agent' : `Get Agent for $${selectedAgent.price}`}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
          </>
        )}
      </div>
    </div>
  );
};

export default AgentStore;
