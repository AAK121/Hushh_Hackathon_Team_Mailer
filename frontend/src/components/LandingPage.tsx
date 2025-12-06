import React, { useState, useEffect, useCallback } from 'react';
import { Mail, Brain, Calendar, Search, Shield, Zap, Users, Lock, ChevronRight, Github, Play, Check, ArrowRight, Sparkles, Clock, Star } from 'lucide-react';
import './LandingPage.css';

interface LandingPageProps {
  onGetStarted: () => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ onGetStarted }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [activeAgent, setActiveAgent] = useState(0);

  // Smooth scroll handler for navigation links
  const handleSmoothScroll = useCallback((e: React.MouseEvent<HTMLAnchorElement>, targetId: string) => {
    e.preventDefault();
    const element = document.getElementById(targetId);
    if (element) {
      const navHeight = 100; // Account for fixed navigation
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - navHeight;
      
      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    }
  }, []);

  useEffect(() => {
    setIsVisible(true);
    const interval = setInterval(() => {
      setActiveAgent((prev) => (prev + 1) % 4);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const agents = [
    {
      id: 'mailerpanda',
      name: 'MailerPanda',
      tagline: 'Email Marketing That Feels Human',
      description: 'Creates personalized emails that reference what each person actually cares about. You approve every message.',
      icon: Mail,
      color: 'from-rosy-taupe to-reddish-brown',
      bgColor: 'bg-rosy-taupe/10',
      borderColor: 'border-rosy-taupe/30',
      stats: '100 emails/min',
      features: ['AI Personalization', 'Human Approval', 'Learning System']
    },
    {
      id: 'relationship',
      name: 'Relationship Memory',
      tagline: 'Never Forget What Matters',
      description: 'Remembers birthdays, preferences, past conversations. Shares context with other agents for better personalization.',
      icon: Brain,
      color: 'from-amethyst to-amethyst-700',
      bgColor: 'bg-amethyst/10',
      borderColor: 'border-amethyst/30',
      stats: 'Instant recall',
      features: ['Contact Memory', 'Shared Context', 'Privacy Control']
    },
    {
      id: 'calendar',
      name: 'AddToCalendar',
      tagline: 'Your Calendar on Autopilot',
      description: 'Reads your emails, finds events automatically, and adds them to Google Calendar in seconds.',
      icon: Calendar,
      color: 'from-golden-earth to-golden-earth-700',
      bgColor: 'bg-golden-earth/10',
      borderColor: 'border-golden-earth/30',
      stats: '150 events/min',
      features: ['Auto-Detection', 'Natural Language', 'Google Sync']
    },
    {
      id: 'research',
      name: 'Research Agent',
      tagline: 'Google on Steroids',
      description: 'Searches academic papers, news, and verified sources. Delivers clear summaries with citations.',
      icon: Search,
      color: 'from-reddish-brown to-rosy-taupe',
      bgColor: 'bg-reddish-brown/10',
      borderColor: 'border-reddish-brown/30',
      stats: '50 queries/min',
      features: ['Multi-Source', 'Verified Info', 'Clear Summaries']
    }
  ];

  const stats = [
    { value: '23+', label: 'Hours Saved Weekly', icon: Clock },
    { value: '100%', label: 'Privacy Focused', icon: Shield },
    { value: '4', label: 'AI Agents', icon: Users },
    { value: '∞', label: 'Possibilities', icon: Sparkles }
  ];

  return (
    <div className="landing-page" style={{ 
      position: 'relative', 
      zIndex: 1,
      overflowX: 'hidden',
      overflowY: 'visible',
      minHeight: '100vh'
    }}>
      {/* Animated Background */}
      <div className="landing-bg" style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, zIndex: 0, pointerEvents: 'none' }}>
        <div className="landing-bg-gradient"></div>
        <div className="landing-bg-pattern"></div>
        <div className="landing-bg-glow landing-bg-glow-1"></div>
        <div className="landing-bg-glow landing-bg-glow-2"></div>
        <div className="landing-bg-glow landing-bg-glow-3"></div>
      </div>

      {/* Navigation */}
      <nav className={`landing-nav ${isVisible ? 'landing-nav-visible' : ''}`} style={{ position: 'fixed', zIndex: 100 }}>
        <div className="landing-nav-container">
          <div className="landing-nav-brand">
            <div className="landing-logo">
              <Sparkles className="landing-logo-icon" />
              <span className="landing-logo-text">Hushh AI</span>
            </div>
          </div>
          <div className="landing-nav-links">
            <a href="#agents" onClick={(e) => handleSmoothScroll(e, 'agents')} className="landing-nav-link">Agents</a>
            <a href="#features" onClick={(e) => handleSmoothScroll(e, 'features')} className="landing-nav-link">Features</a>
            <a href="#privacy" onClick={(e) => handleSmoothScroll(e, 'privacy')} className="landing-nav-link">Privacy</a>
            <a href="https://github.com/AAK121/Hushh_Hackathon_Team_Mailer" target="_blank" rel="noopener noreferrer" className="landing-nav-link">
              <Github size={18} />
              <span>GitHub</span>
            </a>
          </div>
          <button onClick={onGetStarted} className="landing-nav-cta">
            Get Started
            <ArrowRight size={16} />
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className={`landing-hero ${isVisible ? 'landing-hero-visible' : ''}`} style={{ position: 'relative', zIndex: 10, minHeight: '100vh', padding: '8rem 4rem 4rem' }}>
        <div className="landing-hero-content" style={{ color: 'white' }}>
          <div className="landing-hero-badge">
            <Sparkles size={14} />
            <span>Privacy-First AI Agents</span>
          </div>
          
          <h1 className="landing-hero-title" style={{ fontSize: '3.5rem', fontWeight: 800 }}>
            Your Personal <span className="landing-gradient-text">AI Team</span>
            <br />That Actually Respects
            <br /><span className="landing-gradient-text-alt">Your Privacy</span>
          </h1>
          
          <p className="landing-hero-subtitle" style={{ fontSize: '1.25rem', color: 'rgba(255, 255, 255, 0.8)' }}>
            Four intelligent AI agents that handle your emails, research, calendar, 
            and relationships—while keeping your data 100% private and encrypted.
          </p>

          <div className="landing-hero-actions">
            <button onClick={onGetStarted} className="landing-btn-primary">
              <Play size={20} />
              Try It Free
            </button>
            <a href="https://drive.google.com/drive/folders/1RyGEkpi7KWCgS9ABf774KpVJNjQ8FRQ0?usp=sharing" target="_blank" rel="noopener noreferrer" className="landing-btn-secondary">
              <Play size={18} />
              Watch Demo
            </a>
          </div>

          <div className="landing-hero-stats">
            {stats.map((stat, index) => (
              <div key={index} className="landing-stat">
                <stat.icon className="landing-stat-icon" size={20} />
                <div className="landing-stat-value">{stat.value}</div>
                <div className="landing-stat-label">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="landing-hero-visual">
          <div className="landing-agents-preview">
            {agents.map((agent, index) => (
              <div
                key={agent.id}
                className={`landing-agent-preview-card ${index === activeAgent ? 'active' : ''}`}
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className={`landing-agent-icon-wrapper bg-gradient-to-br ${agent.color}`}>
                  <agent.icon size={24} className="text-white" />
                </div>
                <div className="landing-agent-preview-info">
                  <h3>{agent.name}</h3>
                  <p>{agent.tagline}</p>
                </div>
                <div className="landing-agent-stat">{agent.stats}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Trust Badges */}
      <section className="landing-trust">
        <div className="landing-trust-container">
          <div className="landing-trust-item">
            <Lock size={24} />
            <span>End-to-End Encrypted</span>
          </div>
          <div className="landing-trust-divider"></div>
          <div className="landing-trust-item">
            <Shield size={24} />
            <span>No Data Selling</span>
          </div>
          <div className="landing-trust-divider"></div>
          <div className="landing-trust-item">
            <Github size={24} />
            <span>Open Source</span>
          </div>
          <div className="landing-trust-divider"></div>
          <div className="landing-trust-item">
            <Zap size={24} />
            <span>Production Ready</span>
          </div>
        </div>
      </section>

      {/* Agents Section */}
      <section id="agents" className="landing-agents-section">
        <div className="landing-section-header">
          <h2 className="landing-section-title">
            Meet Your <span className="landing-gradient-text">AI Agents</span>
          </h2>
          <p className="landing-section-subtitle">
            Four specialized assistants that work together seamlessly while keeping your data private
          </p>
        </div>

        <div className="landing-agents-grid">
          {agents.map((agent, index) => (
            <div
              key={agent.id}
              className="landing-agent-card"
              style={{ animationDelay: `${index * 0.15}s` }}
            >
              <div className={`landing-agent-card-header bg-gradient-to-br ${agent.color}`}>
                <agent.icon size={32} className="text-white" />
                <div className="landing-agent-card-badge">{agent.stats}</div>
              </div>
              
              <div className="landing-agent-card-body">
                <h3 className="landing-agent-card-title">{agent.name}</h3>
                <p className="landing-agent-card-tagline">{agent.tagline}</p>
                <p className="landing-agent-card-description">{agent.description}</p>
                
                <div className="landing-agent-features">
                  {agent.features.map((feature, i) => (
                    <div key={i} className="landing-agent-feature">
                      <Check size={14} />
                      <span>{feature}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="landing-features-section">
        <div className="landing-section-header">
          <h2 className="landing-section-title">
            Why <span className="landing-gradient-text">Hushh</span> Is Different
          </h2>
          <p className="landing-section-subtitle">
            Built from the ground up with privacy, collaboration, and user control in mind
          </p>
        </div>

        <div className="landing-features-grid">
          <div className="landing-feature-card landing-feature-large">
            <div className="landing-feature-icon-wrapper">
              <Users size={28} />
            </div>
            <h3>Agents Work Together</h3>
            <p>
              MailerPanda asks Relationship Memory about contacts. AddToCalendar coordinates 
              with emails. Your agents collaborate like a real team.
            </p>
            <div className="landing-feature-visual">
              <div className="landing-collaboration-diagram">
                <div className="landing-collab-node landing-collab-center">
                  <Sparkles size={20} />
                </div>
                <div className="landing-collab-node landing-collab-1"><Mail size={16} /></div>
                <div className="landing-collab-node landing-collab-2"><Brain size={16} /></div>
                <div className="landing-collab-node landing-collab-3"><Calendar size={16} /></div>
                <div className="landing-collab-node landing-collab-4"><Search size={16} /></div>
                <svg className="landing-collab-lines">
                  <line x1="50%" y1="50%" x2="20%" y2="20%" />
                  <line x1="50%" y1="50%" x2="80%" y2="20%" />
                  <line x1="50%" y1="50%" x2="20%" y2="80%" />
                  <line x1="50%" y1="50%" x2="80%" y2="80%" />
                </svg>
              </div>
            </div>
          </div>

          <div className="landing-feature-card">
            <div className="landing-feature-icon-wrapper">
              <Shield size={28} />
            </div>
            <h3>Privacy First</h3>
            <p>Your data is encrypted, you control permissions, and we never see or sell your information.</p>
          </div>

          <div className="landing-feature-card">
            <div className="landing-feature-icon-wrapper">
              <Lock size={28} />
            </div>
            <h3>You Stay In Control</h3>
            <p>Review and approve every action. AI assists, you decide. No surprise automations.</p>
          </div>

          <div className="landing-feature-card">
            <div className="landing-feature-icon-wrapper">
              <Github size={28} />
            </div>
            <h3>Open Source</h3>
            <p>See exactly how it works. Audit the code. Contribute improvements. Complete transparency.</p>
          </div>

          <div className="landing-feature-card">
            <div className="landing-feature-icon-wrapper">
              <Zap size={28} />
            </div>
            <h3>Production Ready</h3>
            <p>Not a demo. Real software built for real work. Deploy today, scale tomorrow.</p>
          </div>
        </div>
      </section>

      {/* Privacy Section */}
      <section id="privacy" className="landing-privacy-section">
        <div className="landing-privacy-container">
          <div className="landing-privacy-content">
            <div className="landing-privacy-badge">
              <Lock size={16} />
              <span>Privacy Manifesto</span>
            </div>
            <h2 className="landing-privacy-title">
              Your Privacy Is <span className="landing-gradient-text">Non-Negotiable</span>
            </h2>
            <div className="landing-privacy-points">
              <div className="landing-privacy-point">
                <div className="landing-privacy-point-icon">
                  <Check size={20} />
                </div>
                <div>
                  <h4>End-to-End Encryption</h4>
                  <p>All your data is encrypted at rest and in transit. Only you can access it.</p>
                </div>
              </div>
              <div className="landing-privacy-point">
                <div className="landing-privacy-point-icon">
                  <Check size={20} />
                </div>
                <div>
                  <h4>Granular Permissions</h4>
                  <p>You decide exactly what each agent can see and do. Complete control.</p>
                </div>
              </div>
              <div className="landing-privacy-point">
                <div className="landing-privacy-point-icon">
                  <Check size={20} />
                </div>
                <div>
                  <h4>No Data Selling</h4>
                  <p>We don't see your data, we can't sell it. Period. No hidden clauses.</p>
                </div>
              </div>
              <div className="landing-privacy-point">
                <div className="landing-privacy-point-icon">
                  <Check size={20} />
                </div>
                <div>
                  <h4>Delete Anytime</h4>
                  <p>Export your data, delete everything. Your data, your choice.</p>
                </div>
              </div>
            </div>
          </div>
          <div className="landing-privacy-visual">
            <div className="landing-shield-animation">
              <div className="landing-shield-outer"></div>
              <div className="landing-shield-middle"></div>
              <div className="landing-shield-inner">
                <Shield size={48} />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="landing-cta-section">
        <div className="landing-cta-container">
          <div className="landing-cta-content">
            <h2 className="landing-cta-title">
              Ready to Get Your <span className="landing-gradient-text">Time Back?</span>
            </h2>
            <p className="landing-cta-subtitle">
              Join developers who believe AI should work for you, not against you.
              Set up in 5 minutes. No credit card. No commitment.
            </p>
            <div className="landing-cta-actions">
              <button onClick={onGetStarted} className="landing-btn-primary landing-btn-large">
                <Sparkles size={20} />
                Get Started Free
                <ChevronRight size={20} />
              </button>
              <a href="https://github.com/AAK121/Hushh_Hackathon_Team_Mailer" target="_blank" rel="noopener noreferrer" className="landing-btn-ghost">
                <Github size={20} />
                Star on GitHub
              </a>
            </div>
            <div className="landing-cta-code">
              <code>
                <span className="landing-code-comment"># Get started in 60 seconds</span>
                <br />
                git clone https://github.com/AAK121/Hushh_Hackathon_Team_Mailer.git
                <br />
                cd Hushh_Hackathon_Team_Mailer && pip install -r requirements.txt
                <br />
                python api.py
              </code>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="landing-footer-container">
          <div className="landing-footer-brand">
            <div className="landing-logo">
              <Sparkles className="landing-logo-icon" />
              <span className="landing-logo-text">Hushh AI</span>
            </div>
            <p className="landing-footer-tagline">
              Building AI That Works For You, Not Against You.
            </p>
          </div>
          
          <div className="landing-footer-links">
            <div className="landing-footer-column">
              <h4>Product</h4>
              <a href="#agents" onClick={(e) => handleSmoothScroll(e, 'agents')}>AI Agents</a>
              <a href="#features" onClick={(e) => handleSmoothScroll(e, 'features')}>Features</a>
              <a href="#privacy" onClick={(e) => handleSmoothScroll(e, 'privacy')}>Privacy</a>
            </div>
            <div className="landing-footer-column">
              <h4>Resources</h4>
              <a href="https://github.com/AAK121/Hushh_Hackathon_Team_Mailer" target="_blank" rel="noopener noreferrer">Documentation</a>
              <a href="https://github.com/AAK121/Hushh_Hackathon_Team_Mailer" target="_blank" rel="noopener noreferrer">API Reference</a>
              <a href="https://github.com/AAK121/Hushh_Hackathon_Team_Mailer/issues" target="_blank" rel="noopener noreferrer">Support</a>
            </div>
            <div className="landing-footer-column">
              <h4>Community</h4>
              <a href="https://github.com/AAK121/Hushh_Hackathon_Team_Mailer" target="_blank" rel="noopener noreferrer">
                <Github size={16} />
                GitHub
              </a>
              <a href="https://github.com/AAK121/Hushh_Hackathon_Team_Mailer/issues" target="_blank" rel="noopener noreferrer">
                <Star size={16} />
                Contribute
              </a>
            </div>
          </div>
        </div>
        
        <div className="landing-footer-bottom">
          <p>Made with ❤️ for everyone who believes in privacy</p>
          <p className="landing-footer-quote">"Your data, your agents, your control."</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
