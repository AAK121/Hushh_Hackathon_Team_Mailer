import React, { useState, useEffect } from 'react';
import { StarIcon } from '@heroicons/react/24/outline';
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid';
import type { Email } from '../types/email';

interface EmailListProps {
  emails: Email[];
  selectedEmailId: string | null;
  onEmailSelect: (email: Email) => void;
  onToggleStar: (emailId: string) => void;
  loading?: boolean;
}

const EmailList: React.FC<EmailListProps> = ({ 
  emails, 
  selectedEmailId, 
  onEmailSelect, 
  onToggleStar,
  loading = false 
}) => {
  const [emailHeight, setEmailHeight] = useState(80); // Default height

  // Load settings from localStorage
  useEffect(() => {
    const loadSettings = () => {
      const savedSettings = localStorage.getItem('email-app-settings');
      if (savedSettings) {
        try {
          const parsed = JSON.parse(savedSettings);
          setEmailHeight(parsed.emailHeight || 80);
        } catch (error) {
          console.error('Failed to parse saved settings:', error);
        }
      }
    };

    // Load initial settings
    loadSettings();

    // Listen for settings changes
    const handleSettingsChange = (event: CustomEvent) => {
      setEmailHeight(event.detail.emailHeight || 80);
    };

    window.addEventListener('settingsChanged', handleSettingsChange as EventListener);

    return () => {
      window.removeEventListener('settingsChanged', handleSettingsChange as EventListener);
    };
  }, []);

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) {
      return 'Just now';
    } else if (diffInHours < 24) {
      return `${diffInHours}h ago`;
    } else if (diffInHours < 168) { // 7 days
      return `${Math.floor(diffInHours / 24)}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '...';
  };

  if (loading) {
    return (
      <div className="flex-1 bg-transparent p-4">
        <div className="space-y-2">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="bg-white/40 backdrop-blur-lg rounded-lg p-4 animate-pulse border border-white/40">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-white/40 rounded-full"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-white/40 rounded w-3/4"></div>
                  <div className="h-3 bg-white/40 rounded w-1/2"></div>
                </div>
                <div className="w-12 h-3 bg-white/40 rounded"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (emails.length === 0) {
    return (
      <div className="flex-1 bg-transparent flex items-center justify-center">
        <div className="text-center text-white">
          <div className="text-4xl mb-4">📭</div>
          <h3 className="text-lg font-medium mb-2">No emails found</h3>
          <p className="text-white/70">Your inbox is empty or no emails match the current filter.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 bg-transparent overflow-y-auto">
      <div className="p-4 space-y-1">
        {emails.map((email) => {
          const isSelected = selectedEmailId === email.id;
          
          return (
            <div
              key={email.id}
              onClick={() => onEmailSelect(email)}
              style={{ minHeight: `${emailHeight}px` }}
              className={`bg-black backdrop-blur-lg rounded-lg p-4 cursor-pointer transition-all hover:bg-white/50 border border-white/40 ${
                isSelected 
                  ? 'border-white/60 bg-white/50 shadow-lg' 
                  : email.isRead 
                    ? 'border-white/40' 
                    : 'border-white/50 bg-white/45'
              }`}
            >
              <div className="flex items-start gap-3">
                {/* Star button */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onToggleStar(email.id);
                  }}
                  className="flex-shrink-0 p-1 hover:bg-white/10 rounded"
                >
                  {email.isStarred ? (
                    <StarIconSolid className="w-5 h-5 text-yellow-400" />
                  ) : (
                    <StarIcon className="w-5 h-5 text-white/60 hover:text-yellow-400" />
                  )}
                </button>

                {/* Email content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      <span className={`font-medium text-white ${!email.isRead ? 'font-bold' : ''}`}>
                        {email.from.name}
                      </span>
                      {!email.isRead && (
                        <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                      )}
                    </div>
                    <span className="text-sm text-white/70 flex-shrink-0">
                      {formatTime(email.timestamp)}
                    </span>
                  </div>
                  
                  <div className={`text-sm mb-1 text-white ${!email.isRead ? 'font-semibold' : ''}`}>
                    {truncateText(email.subject, 60)}
                  </div>
                  
                  <div className="text-sm text-white/70">
                    {truncateText(email.body.replace(/\n/g, ' '), 100)}
                  </div>

                  {/* Labels */}
                  {email.labels.length > 0 && (
                    <div className="flex gap-1 mt-2">
                      {email.labels.map((label, index) => (
                        <span
                          key={index}
                          className="text-xs px-2 py-1 bg-white/40 text-white rounded-full backdrop-blur-sm"
                        >
                          {label}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default EmailList;
