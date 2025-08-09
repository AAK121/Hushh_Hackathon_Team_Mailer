// Frontend Integration Example for Access Token Authentication
// This shows how the frontend team can integrate with the new access token system

class HushhCalendarIntegration {
  constructor(apiBaseUrl) {
    this.apiBaseUrl = apiBaseUrl;
    this.googleAuth = null;
    this.hushhTokens = {};
  }

  // Step 1: Initialize Google OAuth
  async initializeGoogleAuth() {
    // Standard Google OAuth2 initialization
    this.googleAuth = google.accounts.oauth2.initTokenClient({
      client_id: 'your-google-client-id',
      scope: 'https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/calendar',
      callback: (response) => {
        this.googleAccessToken = response.access_token;
        console.log('Google OAuth token obtained');
      }
    });
  }

  // Step 2: Generate HushhMCP consent tokens
  async generateConsentTokens(userId) {
    try {
      // Generate email consent token
      const emailTokenResponse = await fetch(`${this.apiBaseUrl}/frontend/consent/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          scope: 'vault_read_email',
          data_summary: 'Email reading for calendar event extraction'
        })
      });
      
      // Generate calendar consent token
      const calendarTokenResponse = await fetch(`${this.apiBaseUrl}/frontend/consent/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          scope: 'vault_write_calendar',
          data_summary: 'Calendar event creation from email analysis'
        })
      });

      this.hushhTokens = {
        email_token: (await emailTokenResponse.json()).consent_token,
        calendar_token: (await calendarTokenResponse.json()).consent_token
      };

      console.log('HushhMCP consent tokens generated');
    } catch (error) {
      console.error('Failed to generate consent tokens:', error);
      throw error;
    }
  }

  // Step 3: Request Google OAuth access token
  async requestGoogleAccess() {
    return new Promise((resolve, reject) => {
      if (!this.googleAuth) {
        reject(new Error('Google Auth not initialized'));
        return;
      }

      this.googleAuth.requestAccessToken();
      
      // Wait for token (simplified - in real app you'd handle this better)
      const checkToken = setInterval(() => {
        if (this.googleAccessToken) {
          clearInterval(checkToken);
          resolve(this.googleAccessToken);
        }
      }, 100);

      // Timeout after 30 seconds
      setTimeout(() => {
        clearInterval(checkToken);
        reject(new Error('Google OAuth timeout'));
      }, 30000);
    });
  }

  // Step 4: Execute comprehensive email analysis
  async analyzeEmailsAndCreateEvents(userId) {
    try {
      // Ensure we have all required tokens
      if (!this.googleAccessToken) {
        await this.requestGoogleAccess();
      }
      
      if (!this.hushhTokens.email_token) {
        await this.generateConsentTokens(userId);
      }

      // Make API request with both token types
      const response = await fetch(`${this.apiBaseUrl}/agents/addtocalendar/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          agent_id: 'addtocalendar',
          consent_tokens: this.hushhTokens,
          parameters: {
            google_access_token: this.googleAccessToken,
            action: 'comprehensive_analysis'
          }
        })
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }

      const result = await response.json();
      console.log('Email analysis completed:', result);
      
      return result;
    } catch (error) {
      console.error('Email analysis failed:', error);
      throw error;
    }
  }

  // Step 5: Analyze emails only (without calendar creation)
  async analyzeEmailsOnly(userId) {
    try {
      await this.requestGoogleAccess();
      
      const response = await fetch(`${this.apiBaseUrl}/agents/addtocalendar/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          agent_id: 'addtocalendar',
          consent_tokens: {
            email_token: this.hushhTokens.email_token
            // No calendar token needed for analyze_only
          },
          parameters: {
            google_access_token: this.googleAccessToken,
            action: 'analyze_only'
          }
        })
      });

      return await response.json();
    } catch (error) {
      console.error('Email analysis failed:', error);
      throw error;
    }
  }

  // Step 6: Create manual event with AI assistance
  async createManualEvent(userId, eventDescription) {
    try {
      await this.requestGoogleAccess();
      await this.generateConsentTokens(userId);

      const response = await fetch(`${this.apiBaseUrl}/agents/addtocalendar/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          agent_id: 'addtocalendar',
          consent_tokens: this.hushhTokens,
          parameters: {
            google_access_token: this.googleAccessToken,
            action: 'manual_event',
            event_description: eventDescription,
            add_to_calendar: true
          }
        })
      });

      return await response.json();
    } catch (error) {
      console.error('Manual event creation failed:', error);
      throw error;
    }
  }

  // Helper: Check token expiration and refresh
  async refreshTokensIfNeeded() {
    // Check Google token expiration
    if (this.isGoogleTokenExpired()) {
      await this.requestGoogleAccess();
    }

    // Check HushhMCP token expiration
    if (this.areHushhTokensExpired()) {
      await this.generateConsentTokens(this.currentUserId);
    }
  }

  // Helper methods
  isGoogleTokenExpired() {
    // Implement token expiration check
    // Google access tokens typically expire in 1 hour
    return false; // Simplified
  }

  areHushhTokensExpired() {
    // Implement HushhMCP token expiration check
    return false; // Simplified
  }
}

// Usage Example
async function exampleUsage() {
  const integration = new HushhCalendarIntegration('https://your-api-server.com');
  
  try {
    // Initialize
    await integration.initializeGoogleAuth();
    
    const userId = 'user_123';
    
    // Generate consent tokens
    await integration.generateConsentTokens(userId);
    
    // Analyze emails and create calendar events
    const result = await integration.analyzeEmailsAndCreateEvents(userId);
    
    console.log('Success!', result);
    console.log(`Processed ${result.data.analysis_summary.total_emails_processed} emails`);
    console.log(`Created ${result.data.analysis_summary.events_created} calendar events`);
    
  } catch (error) {
    console.error('Integration failed:', error);
  }
}

// React Component Example
function CalendarIntegrationComponent() {
  const [integration] = useState(new HushhCalendarIntegration('/api'));
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const handleAnalyzeEmails = async () => {
    setLoading(true);
    try {
      await integration.initializeGoogleAuth();
      const result = await integration.analyzeEmailsAndCreateEvents('current_user');
      setResults(result);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Email Calendar Integration</h2>
      <button onClick={handleAnalyzeEmails} disabled={loading}>
        {loading ? 'Analyzing...' : 'Analyze Emails & Create Events'}
      </button>
      
      {results && (
        <div>
          <h3>Results:</h3>
          <p>Emails Processed: {results.data?.analysis_summary?.total_emails_processed}</p>
          <p>Events Created: {results.data?.analysis_summary?.events_created}</p>
          <p>High Priority Emails: {results.data?.analysis_summary?.high_priority_emails}</p>
        </div>
      )}
    </div>
  );
}

export { HushhCalendarIntegration, exampleUsage, CalendarIntegrationComponent };
