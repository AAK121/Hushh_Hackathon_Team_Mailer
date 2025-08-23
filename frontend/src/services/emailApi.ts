import type { Email, AIGeneratedEmail } from '../types/email';

// Mock API functions - replace with actual API calls
export const emailApi = {
  // Fetch emails from server
  getEmails: async (): Promise<Email[]> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return [
      {
        id: '1',
        from: { email: 'john.doe@company.com', name: 'John Doe' },
        to: [{ email: 'me@company.com', name: 'Me' }],
        subject: 'Project Update - Q4 Results',
        body: 'Hi there,\n\nI wanted to share the latest updates on our Q4 project. The results have been outstanding and we\'ve exceeded our initial targets by 15%.\n\nKey highlights:\n- Revenue increased by 25%\n- Customer satisfaction up 18%\n- New features deployed successfully\n\nLet me know if you have any questions.\n\nBest regards,\nJohn',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
        isRead: false,
        isStarred: false,
        labels: ['Work', 'Important']
      },
      {
        id: '2',
        from: { email: 'sarah.wilson@design.com', name: 'Sarah Wilson' },
        to: [{ email: 'me@company.com', name: 'Me' }],
        cc: [{ email: 'team@company.com', name: 'Team' }],
        subject: 'Design Review Meeting Tomorrow',
        body: 'Hello,\n\nReminder about our design review meeting scheduled for tomorrow at 2 PM.\n\nAgenda:\n- Review new UI mockups\n- Discuss user feedback\n- Plan next iteration\n\nMeeting link: https://meet.example.com/design-review\n\nSee you there!\nSarah',
        timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(), // 5 hours ago
        isRead: true,
        isStarred: true,
        labels: ['Meetings']
      },
      {
        id: '3',
        from: { email: 'notifications@service.com', name: 'Service Notifications' },
        to: [{ email: 'me@company.com', name: 'Me' }],
        subject: 'Weekly Report - System Performance',
        body: 'Weekly System Performance Report\n\nSystem uptime: 99.9%\nAverage response time: 120ms\nTotal requests processed: 1,234,567\n\nNo critical issues reported this week.\n\nBest regards,\nSystem Monitoring Team',
        timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
        isRead: true,
        isStarred: false,
        labels: ['Reports', 'System']
      }
    ];
  },

  // Send email
  sendEmail: async (email: {
    to: string[];
    cc: string[];
    bcc: string[];
    subject: string;
    body: string;
  }): Promise<boolean> => {
    console.log('Sending email:', email);
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    return true;
  },

  // Generate AI email
  generateAIEmail: async (prompt: string): Promise<AIGeneratedEmail> => {
    console.log('Generating AI email for prompt:', prompt);
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Mock AI response based on prompt
    const responses = {
      'meeting': {
        subject: 'Meeting Request - Project Discussion',
        body: 'Hi,\n\nI hope this email finds you well. I would like to schedule a meeting to discuss our upcoming project.\n\nWould you be available next week for a 30-minute discussion? I\'m flexible with timing and can accommodate your schedule.\n\nPlease let me know what works best for you.\n\nBest regards,',
        reasoning: 'Generated a professional meeting request email with flexible scheduling options.'
      },
      'follow up': {
        subject: 'Following Up on Our Previous Discussion',
        body: 'Hi,\n\nI wanted to follow up on our conversation from last week regarding the project timeline.\n\nAs discussed, I\'ve prepared the initial requirements document and would appreciate your feedback. Please let me know if you need any additional information or if you\'d like to schedule another call to discuss further.\n\nLooking forward to hearing from you.\n\nBest regards,',
        reasoning: 'Created a polite follow-up email that references previous discussions and next steps.'
      },
      default: {
        subject: 'Important Update',
        body: 'Hi,\n\nI hope you\'re doing well. I wanted to reach out regarding an important update that I believe will be of interest to you.\n\nPlease let me know if you have any questions or if you\'d like to discuss this further.\n\nBest regards,',
        reasoning: 'Generated a general professional email template that can be customized for various purposes.'
      }
    };

    const promptLower = prompt.toLowerCase();
    if (promptLower.includes('meeting')) {
      return responses.meeting;
    } else if (promptLower.includes('follow')) {
      return responses['follow up'];
    } else {
      return responses.default;
    }
  },

  // Mark email as read
  markAsRead: async (emailId: string): Promise<boolean> => {
    console.log('Marking email as read:', emailId);
    await new Promise(resolve => setTimeout(resolve, 500));
    return true;
  },

  // Star/unstar email
  toggleStar: async (emailId: string): Promise<boolean> => {
    console.log('Toggling star for email:', emailId);
    await new Promise(resolve => setTimeout(resolve, 500));
    return true;
  }
};
