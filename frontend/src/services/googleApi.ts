// Google API integration service with refresh token support
export interface GoogleApiConfig {
  clientId: string;
  apiKey?: string;
  discoveryDocs: string[];
  scopes: string[];
}

export interface TokenInfo {
  accessToken: string;
  refreshToken?: string;
  expiresAt?: number;
}

export interface CalendarEvent {
  id: string;
  summary: string;
  description?: string;
  start: {
    dateTime?: string;
    date?: string;
    timeZone?: string;
  };
  end: {
    dateTime?: string;
    date?: string;
    timeZone?: string;
  };
  attendees?: Array<{
    email: string;
    displayName?: string;
    responseStatus?: 'needsAction' | 'declined' | 'tentative' | 'accepted';
  }>;
  location?: string;
  status?: 'confirmed' | 'tentative' | 'cancelled';
  htmlLink?: string;
  created?: string;
  updated?: string;
}

export interface GmailMessage {
  id: string;
  threadId: string;
  snippet: string;
  payload: {
    headers: Array<{
      name: string;
      value: string;
    }>;
    body?: {
      data?: string;
      size?: number;
    };
    parts?: Array<{
      mimeType: string;
      body: {
        data?: string;
        size?: number;
      };
    }>;
  };
  internalDate: string;
  labelIds: string[];
  sizeEstimate: number;
}

class GoogleApiService {
  private gapi: any = null;
  private isInitialized = false;
  private config: GoogleApiConfig;
  private currentToken: TokenInfo | null = null;
  private tokenRefreshCallback?: () => Promise<{ token: string | null; error: any }>;

  constructor() {
    this.config = {
      clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID || '',
      apiKey: import.meta.env.VITE_GOOGLE_API_KEY || '',
      discoveryDocs: [
        'https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest',
        'https://www.googleapis.com/discovery/v1/apis/gmail/v1/rest'
      ],
      scopes: [
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/calendar.events',
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
      ]
    };
  }

  // Set token refresh callback (typically from AuthContext)
  setTokenRefreshCallback(callback: () => Promise<{ token: string | null; error: any }>) {
    this.tokenRefreshCallback = callback;
  }

  // Set current token
  setToken(token: string, refreshToken?: string, expiresIn?: number) {
    this.currentToken = {
      accessToken: token,
      refreshToken,
      expiresAt: expiresIn ? Date.now() + (expiresIn * 1000) : undefined
    };
  }

  // Get valid token with automatic refresh
  async getValidToken(): Promise<string | null> {
    try {
      // Check if we have a token
      if (!this.currentToken) {
        // Try to get from session storage
        const storedToken = sessionStorage.getItem('google_access_token');
        const storedExpiry = sessionStorage.getItem('google_token_expiry');
        
        if (storedToken && storedExpiry) {
          this.currentToken = {
            accessToken: storedToken,
            expiresAt: parseInt(storedExpiry)
          };
        } else {
          console.log('No token available');
          return null;
        }
      }

      // Check if token is still valid (with 5-minute buffer)
      if (this.currentToken.expiresAt && this.currentToken.expiresAt - Date.now() < 300000) {
        console.log('Token expiring soon, refreshing...');
        
        if (this.tokenRefreshCallback) {
          const refreshResult = await this.tokenRefreshCallback();
          if (refreshResult.token) {
            this.currentToken.accessToken = refreshResult.token;
            return refreshResult.token;
          } else {
            console.error('Failed to refresh token:', refreshResult.error);
            return null;
          }
        } else {
          console.warn('No token refresh callback available');
          return null;
        }
      }

      return this.currentToken.accessToken;
    } catch (error) {
      console.error('Error getting valid token:', error);
      return null;
    }
  }

  // Initialize Google API
  async initialize(): Promise<boolean> {
    try {
      if (this.isInitialized) return true;

      // Load Google API script if not already loaded
      if (!window.gapi) {
        await this.loadGoogleApiScript();
      }

      this.gapi = window.gapi;

      // Initialize the API
      await new Promise((resolve, reject) => {
        this.gapi.load('client:auth2', {
          callback: resolve,
          onerror: reject
        });
      });

      // Initialize the client
      await this.gapi.client.init({
        apiKey: this.config.apiKey,
        clientId: this.config.clientId,
        discoveryDocs: this.config.discoveryDocs,
        scope: this.config.scopes.join(' ')
      });

      this.isInitialized = true;
      return true;
    } catch (error) {
      console.error('Failed to initialize Google API:', error);
      return false;
    }
  }

  private loadGoogleApiScript(): Promise<void> {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://apis.google.com/js/api.js';
      script.onload = () => resolve();
      script.onerror = () => reject(new Error('Failed to load Google API script'));
      document.head.appendChild(script);
    });
  }

  // Authentication methods
  async signIn(): Promise<any> {
    try {
      if (!this.isInitialized) {
        await this.initialize();
      }

      const authInstance = this.gapi.auth2.getAuthInstance();
      const user = await authInstance.signIn();
      
      return {
        user: user,
        profile: user.getBasicProfile(),
        accessToken: user.getAuthResponse().access_token
      };
    } catch (error) {
      console.error('Google sign-in failed:', error);
      throw error;
    }
  }

  async signOut(): Promise<void> {
    try {
      if (!this.isInitialized) return;
      
      const authInstance = this.gapi.auth2.getAuthInstance();
      await authInstance.signOut();
    } catch (error) {
      console.error('Google sign-out failed:', error);
      throw error;
    }
  }

  isSignedIn(): boolean {
    if (!this.isInitialized) return false;
    
    const authInstance = this.gapi.auth2.getAuthInstance();
    return authInstance.isSignedIn.get();
  }

  getCurrentUser(): any {
    if (!this.isSignedIn()) return null;
    
    const authInstance = this.gapi.auth2.getAuthInstance();
    return authInstance.currentUser.get();
  }

  // Calendar API methods with automatic token refresh
  async getCalendarEvents(calendarId = 'primary', timeMin?: string, timeMax?: string): Promise<CalendarEvent[]> {
    try {
      const token = await this.getValidToken();
      if (!token) {
        throw new Error('No valid authentication token available');
      }

      const request = {
        calendarId: calendarId,
        timeMin: timeMin || new Date().toISOString(),
        timeMax: timeMax,
        singleEvents: true,
        orderBy: 'startTime',
        maxResults: 50
      };

      // Use direct API call with token instead of gapi client
      const response = await fetch(
        `https://www.googleapis.com/calendar/v3/calendars/${calendarId}/events?` + 
        new URLSearchParams({
          timeMin: request.timeMin,
          ...(request.timeMax && { timeMax: request.timeMax }),
          singleEvents: 'true',
          orderBy: 'startTime',
          maxResults: '50'
        }), {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        throw new Error(`Calendar API request failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data.items || [];
    } catch (error) {
      console.error('Failed to fetch calendar events:', error);
      throw error;
    }
  }

  async createCalendarEvent(event: Partial<CalendarEvent>, calendarId = 'primary'): Promise<CalendarEvent> {
    try {
      const token = await this.getValidToken();
      if (!token) {
        throw new Error('No valid authentication token available');
      }

      const response = await fetch(
        `https://www.googleapis.com/calendar/v3/calendars/${calendarId}/events`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(event)
        }
      );

      if (!response.ok) {
        throw new Error(`Calendar API request failed: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to create calendar event:', error);
      throw error;
    }
  }

  async updateCalendarEvent(eventId: string, event: Partial<CalendarEvent>, calendarId = 'primary'): Promise<CalendarEvent> {
    try {
      const token = await this.getValidToken();
      if (!token) {
        throw new Error('No valid authentication token available');
      }

      const response = await fetch(
        `https://www.googleapis.com/calendar/v3/calendars/${calendarId}/events/${eventId}`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(event)
        }
      );

      if (!response.ok) {
        throw new Error(`Calendar API request failed: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to update calendar event:', error);
      throw error;
    }
  }

  async deleteCalendarEvent(eventId: string, calendarId = 'primary'): Promise<void> {
    try {
      const token = await this.getValidToken();
      if (!token) {
        throw new Error('No valid authentication token available');
      }

      const response = await fetch(
        `https://www.googleapis.com/calendar/v3/calendars/${calendarId}/events/${eventId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
          }
        }
      );

      if (!response.ok) {
        throw new Error(`Calendar API request failed: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('Failed to delete calendar event:', error);
      throw error;
    }
  }

  // Gmail API methods with automatic token refresh
  async getGmailMessages(query = '', maxResults = 50): Promise<GmailMessage[]> {
    try {
      const token = await this.getValidToken();
      if (!token) {
        throw new Error('No valid authentication token available');
      }

      // First, get the list of message IDs
      const listResponse = await fetch(
        `https://www.googleapis.com/gmail/v1/users/me/messages?` + 
        new URLSearchParams({
          q: query,
          maxResults: maxResults.toString()
        }), {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!listResponse.ok) {
        throw new Error(`Gmail API request failed: ${listResponse.status} ${listResponse.statusText}`);
      }

      const listData = await listResponse.json();

      if (!listData.messages) {
        return [];
      }

      // Then, get the full message details for each ID
      const messages = await Promise.all(
        listData.messages.map(async (message: any) => {
          const messageResponse = await fetch(
            `https://www.googleapis.com/gmail/v1/users/me/messages/${message.id}`, {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              }
            }
          );

          if (!messageResponse.ok) {
            throw new Error(`Gmail message fetch failed: ${messageResponse.status} ${messageResponse.statusText}`);
          }

          return await messageResponse.json();
        })
      );

      return messages;
    } catch (error) {
      console.error('Failed to fetch Gmail messages:', error);
      throw error;
    }
  }

  async sendGmailMessage(to: string, subject: string, body: string, cc?: string, bcc?: string): Promise<any> {
    try {
      const token = await this.getValidToken();
      if (!token) {
        throw new Error('No valid authentication token available');
      }

      // Create the email message
      const email = [
        `To: ${to}`,
        cc ? `Cc: ${cc}` : '',
        bcc ? `Bcc: ${bcc}` : '',
        `Subject: ${subject}`,
        '',
        body
      ].filter(line => line !== '').join('\n');

      // Base64 encode the email
      const encodedEmail = btoa(unescape(encodeURIComponent(email)))
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=+$/, '');

      const response = await fetch(
        'https://www.googleapis.com/gmail/v1/users/me/messages/send', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            raw: encodedEmail
          })
        }
      );

      if (!response.ok) {
        throw new Error(`Gmail send failed: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to send Gmail message:', error);
      throw error;
    }
  }

  async markGmailMessageAsRead(messageId: string): Promise<void> {
    try {
      if (!this.isSignedIn()) {
        throw new Error('User not authenticated');
      }

      await this.gapi.client.gmail.users.messages.modify({
        userId: 'me',
        id: messageId,
        resource: {
          removeLabelIds: ['UNREAD']
        }
      });
    } catch (error) {
      console.error('Failed to mark message as read:', error);
      throw error;
    }
  }

  async addGmailLabel(messageId: string, labelIds: string[]): Promise<void> {
    try {
      if (!this.isSignedIn()) {
        throw new Error('User not authenticated');
      }

      await this.gapi.client.gmail.users.messages.modify({
        userId: 'me',
        id: messageId,
        resource: {
          addLabelIds: labelIds
        }
      });
    } catch (error) {
      console.error('Failed to add label to message:', error);
      throw error;
    }
  }

  async removeGmailLabel(messageId: string, labelIds: string[]): Promise<void> {
    try {
      if (!this.isSignedIn()) {
        throw new Error('User not authenticated');
      }

      await this.gapi.client.gmail.users.messages.modify({
        userId: 'me',
        id: messageId,
        resource: {
          removeLabelIds: labelIds
        }
      });
    } catch (error) {
      console.error('Failed to remove label from message:', error);
      throw error;
    }
  }

  // Utility methods
  parseGmailMessage(message: GmailMessage): {
    from: string;
    to: string;
    subject: string;
    date: string;
    body: string;
  } {
    const headers = message.payload.headers;
    const getHeader = (name: string) => {
      const header = headers.find(h => h.name.toLowerCase() === name.toLowerCase());
      return header ? header.value : '';
    };

    let body = '';
    if (message.payload.body?.data) {
      body = atob(message.payload.body.data.replace(/-/g, '+').replace(/_/g, '/'));
    } else if (message.payload.parts) {
      const textPart = message.payload.parts.find(part => part.mimeType === 'text/plain');
      if (textPart?.body?.data) {
        body = atob(textPart.body.data.replace(/-/g, '+').replace(/_/g, '/'));
      }
    }

    return {
      from: getHeader('From'),
      to: getHeader('To'),
      subject: getHeader('Subject'),
      date: getHeader('Date'),
      body: body
    };
  }

  formatCalendarEvent(event: CalendarEvent): {
    title: string;
    startTime: Date;
    endTime: Date;
    description: string;
    location: string;
  } {
    const startTime = event.start.dateTime 
      ? new Date(event.start.dateTime)
      : new Date(event.start.date + 'T00:00:00');
    
    const endTime = event.end.dateTime 
      ? new Date(event.end.dateTime)
      : new Date(event.end.date + 'T23:59:59');

    return {
      title: event.summary || 'Untitled Event',
      startTime,
      endTime,
      description: event.description || '',
      location: event.location || ''
    };
  }
}

// Export singleton instance
export const googleApiService = new GoogleApiService();

// Type declarations for Google API
declare global {
  interface Window {
    gapi: any;
  }
}
