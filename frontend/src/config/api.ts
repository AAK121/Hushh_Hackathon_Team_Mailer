// API Configuration
export const API_CONFIG = {
  BASE_URL: 'https://hush-backend-sepia.vercel.app',
  ENDPOINTS: {
    CONSENT_TOKEN: '/consent/token',
    MAILERPANDA_MASS_EMAIL: '/agents/mailerpanda/mass-email',
    MAILERPANDA_APPROVE: '/agents/mailerpanda/mass-email/approve',
    ADDTOCALENDAR_EXECUTE: '/agents/addtocalendar/execute',
    ADDTOCALENDAR_APPROVE: '/agents/addtocalendar/approve',
    CHAT: '/chat'
  }
};

export default API_CONFIG;
