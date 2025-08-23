# 📧 MailerPanda Agent

**Version:** 3.1.0  
**Agent ID:** `agent_mailerpanda`  
**Framework:** HushhMCP v1.0  

> 🐼 Advanced AI-powered mass mailer agent with complete privacy-first architecture, consent validation, cross-agent communication capabilities, and intelligent description-based email personalization.

## 🔗 Frontend-Backend Integration

### 📡 **API Endpoint**
```
POST http://localhost:8002/agents/mailerpanda/execute
Content-Type: application/json
```

### 🔑 **Dynamic API Key Support**
MailerPanda agent supports **dynamic API keys** for secure, user-specific email and AI functionality:

```javascript
// Frontend API Call Example
const response = await fetch('http://localhost:8002/agents/mailerpanda/execute', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    user_id: "user_123",
    user_input: "Create a welcome email campaign for new customers",
    mode: "interactive",
    consent_tokens: {
      "vault.read.email": "HCT:user_read_email_token",
      "vault.write.email": "HCT:user_write_email_token",
      "vault.read.contacts": "HCT:user_contacts_token"
    },
    
    // Dynamic API keys passed from frontend
    google_api_key: userProvidedGoogleKey,     // User's Google/Gemini API key
    mailjet_api_key: userProvidedMailjetKey,   // User's Mailjet API key
    mailjet_api_secret: userProvidedMailjetSecret, // User's Mailjet secret
    api_keys: {
      custom_email_service: "additional_api_key"
    },
    
    // Campaign settings
    require_approval: true,
    use_ai_generation: true
  })
});
```

### 🎯 **Request Model**
```typescript
interface MailerPandaRequest {
  // Required fields
  user_id: string;
  user_input: string;  // Natural language campaign description
  mode: "interactive" | "headless" | "demo";
  consent_tokens: Record<string, string>;  // HushhMCP tokens
  
  // Email configuration
  sender_email?: string;
  recipient_emails?: string[];
  
  // Campaign settings
  require_approval?: boolean;
  use_ai_generation?: boolean;
  
  // Dynamic API keys (NEW!)
  google_api_key?: string;      // User's Google/Gemini API key
  mailjet_api_key?: string;     // User's Mailjet API key
  mailjet_api_secret?: string;  // User's Mailjet secret
  api_keys?: Record<string, string>;  // Additional service keys
}
```

### 📋 **Response Model**
```typescript
interface MailerPandaResponse {
  status: "success" | "completed" | "error";
  user_id: string;
  mode: string;
  
  // Campaign results
  campaign_id?: string;
  email_template?: Record<string, string>;
  
  // Human-in-the-loop
  requires_approval?: boolean;
  approval_status?: string;
  feedback_required?: boolean;
  
  // Email sending results
  emails_sent?: number;
  send_status?: Array<Record<string, any>>;
  
  // Vault and trust links
  vault_storage_key?: string;
  trust_links?: string[];
  
  // Error and processing info
  errors?: string[];
  processing_time: number;
}
```

### 🎮 **Frontend Integration Examples**

#### **React Email Campaign Manager**
```jsx
import React, { useState, useEffect } from 'react';

const EmailCampaignManager = ({ userApiKeys, userTokens }) => {
  const [campaignInput, setCampaignInput] = useState('');
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pendingApproval, setPendingApproval] = useState(null);

  const createCampaign = async (campaignDescription, mode = 'interactive') => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8002/agents/mailerpanda/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: "current_user",
          user_input: campaignDescription,
          mode: mode,
          consent_tokens: userTokens,
          
          // Dynamic API keys from user
          google_api_key: userApiKeys.google,
          mailjet_api_key: userApiKeys.mailjet.key,
          mailjet_api_secret: userApiKeys.mailjet.secret,
          
          require_approval: true,
          use_ai_generation: true
        })
      });
      
      const result = await response.json();
      
      if (result.status === 'completed' || result.status === 'success') {
        if (result.requires_approval) {
          setPendingApproval(result);
        } else {
          setCampaigns(prev => [...prev, result]);
        }
        return result;
      } else {
        throw new Error(result.errors?.join(', ') || 'Campaign creation failed');
      }
    } catch (error) {
      console.error('Campaign creation failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const approveCampaign = async (campaignId) => {
    const response = await fetch('http://localhost:8002/agents/mailerpanda/approve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: "current_user",
        campaign_id: campaignId,
        approval_decision: "approved"
      })
    });
    
    const result = await response.json();
    if (result.status === 'success') {
      setPendingApproval(null);
      setCampaigns(prev => [...prev, result]);
    }
  };

  return (
    <div className="email-campaign-manager">
      <div className="campaign-creator">
        <textarea
          value={campaignInput}
          onChange={(e) => setCampaignInput(e.target.value)}
          placeholder="Describe your email campaign (e.g., 'Create a welcome email for new subscribers')"
          rows={4}
        />
        <button 
          onClick={() => createCampaign(campaignInput)}
          disabled={loading || !campaignInput.trim()}
        >
          {loading ? 'Creating...' : 'Create Campaign'}
        </button>
      </div>

      {pendingApproval && (
        <div className="approval-required">
          <h3>Campaign Approval Required</h3>
          <div className="email-preview">
            <h4>{pendingApproval.email_template?.subject}</h4>
            <div dangerouslySetInnerHTML={{ 
              __html: pendingApproval.email_template?.html 
            }} />
          </div>
          <button onClick={() => approveCampaign(pendingApproval.campaign_id)}>
            Approve & Send
          </button>
          <button onClick={() => setPendingApproval(null)}>
            Reject
          </button>
        </div>
      )}

      <div className="campaigns-list">
        {campaigns.map(campaign => (
          <div key={campaign.campaign_id} className="campaign-card">
            <h3>Campaign: {campaign.campaign_id}</h3>
            <p>Emails sent: {campaign.emails_sent}</p>
            <p>Status: {campaign.status}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
```

#### **Vue.js Integration with Real-time Updates**
```vue
<template>
  <div class="mailerpanda-dashboard">
    <div class="campaign-controls">
      <select v-model="selectedMode">
        <option value="interactive">Interactive</option>
        <option value="demo">Demo</option>
        <option value="headless">Headless</option>
      </select>
      
      <input
        v-model="campaignDescription"
        placeholder="Describe your email campaign..."
        @keydown.enter="createCampaign"
      />
      
      <button @click="createCampaign" :disabled="loading">
        {{ loading ? 'Creating...' : 'Create Campaign' }}
      </button>
    </div>
    
    <div class="real-time-status" v-if="currentCampaign">
      <h3>Campaign in Progress</h3>
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: campaignProgress + '%' }"
        ></div>
      </div>
      <p>{{ currentCampaign.status_message }}</p>
    </div>
    
    <div class="campaign-history">
      <h3>Recent Campaigns</h3>
      <div 
        v-for="campaign in campaignHistory" 
        :key="campaign.campaign_id"
        class="campaign-item"
      >
        <span>{{ campaign.campaign_id }}</span>
        <span>{{ campaign.emails_sent }} emails</span>
        <span class="status" :class="campaign.status">
          {{ campaign.status }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      campaignDescription: '',
      selectedMode: 'interactive',
      loading: false,
      currentCampaign: null,
      campaignProgress: 0,
      campaignHistory: [],
      websocket: null
    };
  },
  mounted() {
    this.initWebSocket();
  },
  methods: {
    async createCampaign() {
      if (!this.campaignDescription.trim()) return;
      
      this.loading = true;
      try {
        const response = await this.$http.post('/agents/mailerpanda/execute', {
          user_id: this.$store.state.user.id,
          user_input: this.campaignDescription,
          mode: this.selectedMode,
          consent_tokens: this.$store.state.tokens.email,
          
          // Dynamic API keys
          google_api_key: this.$store.state.userApiKeys.google,
          mailjet_api_key: this.$store.state.userApiKeys.mailjet.key,
          mailjet_api_secret: this.$store.state.userApiKeys.mailjet.secret,
          
          require_approval: this.selectedMode === 'interactive'
        });
        
        if (response.data.status === 'completed') {
          this.campaignHistory.unshift(response.data);
          this.campaignDescription = '';
        }
        
      } catch (error) {
        this.$toast.error('Campaign creation failed: ' + error.message);
      } finally {
        this.loading = false;
      }
    },
    
    initWebSocket() {
      this.websocket = new WebSocket('ws://localhost:8002/ws/mailerpanda');
      
      this.websocket.onmessage = (event) => {
        const update = JSON.parse(event.data);
        
        if (update.type === 'campaign_progress') {
          this.campaignProgress = update.progress;
          this.currentCampaign = update.campaign;
        } else if (update.type === 'campaign_completed') {
          this.campaignHistory.unshift(update.campaign);
          this.currentCampaign = null;
          this.campaignProgress = 0;
        }
      };
    }
  },
  
  beforeDestroy() {
    if (this.websocket) {
      this.websocket.close();
    }
  }
};
</script>
```
- Ensures privacy compliance

### 2. 🤖 AI Content Generation
- Uses Gemini 2.0 Flash for intelligent composition
- Context-aware email generation
- Maintains brand consistency

### 2.1. ✨ NEW: Description-Based Email Personalization
**Version 3.1.0 Feature**

Intelligently customizes emails based on individual contact descriptions in Excel files:

#### 📊 **Excel File Enhancement**
```
| name     | email              | company_name | description                           |
|----------|-------------------|--------------|---------------------------------------|
| John     | john@company.com  | TechCorp     | Long-time customer, prefers technical details |
| Sarah    | sarah@startup.io  | StartupX     | New to our services, needs gentle introduction |
| Michael  | mike@enterprise.com| BigCorp      | Executive level, keep it brief and business-focused |
```

#### 🎯 **How It Works**
1. **Detection**: Automatically detects `description` column in Excel files
2. **AI Personalization**: Uses Gemini AI to customize base template for each contact
3. **Context Integration**: Incorporates individual descriptions naturally into emails
4. **Fallback**: Uses standard template for contacts without descriptions
5. **Consent Validation**: Full HushMCP consent validation for AI personalization

#### 🔧 **Frontend Integration**
```javascript
const response = await fetch('/agents/mailerpanda/execute', {
  method: 'POST',
  body: JSON.stringify({
    user_id: "user_123",
    user_input: "Create welcome emails for new customers",
    mode: "interactive",
    // Excel file with descriptions will be automatically detected
    consent_tokens: {
      "vault.read.email": "HCT:token",
      "vault.write.email": "HCT:token", 
      "content_generation": "HCT:token"  // Required for personalization
    }
  })
});
```

#### 📋 **Benefits**
- **Higher Engagement**: Personalized content increases open and click rates
- **Relevant Messaging**: Context-aware content for different customer types
- **Efficiency**: Automatic personalization without manual effort
- **Flexibility**: Works alongside existing placeholder system
- **Privacy-First**: Full consent validation for AI operations

### 3. 👥 Human Approval
- Interactive review and approval process
- Content modification capabilities
- Quality assurance workflow

### 4. 💾 Campaign Storage
- Secure vault storage with encryption
- Campaign metadata tracking
- Audit trail maintenance

### 5. 📧 Email Distribution
- Reliable Mailjet integration
- Delivery status tracking
- Error handling and retries

### 6. 🔗 Trust Link Creation
- Cross-agent delegation setup
- Resource sharing capabilities
- Secure inter-agent communication

---

## 🔧 Configuration

### Manifest Configuration

```python
{
    "id": "agent_mailerpanda",
    "name": "MailerPanda",
    "version": "3.0.0",
    "description": "AI-powered mass mailer with privacy controls",
    "required_scopes": {
        "content_generation": [ConsentScope.CUSTOM_TEMPORARY],
        "email_sending": [ConsentScope.VAULT_READ_EMAIL],
        "contact_management": [ConsentScope.VAULT_READ_FILE],
        "campaign_storage": [ConsentScope.VAULT_WRITE_FILE]
    }
}
```

### Workflow Configuration

The agent uses LangGraph for state management with the following nodes:
- `validate_consent`: Initial consent validation
- `llm_writer`: AI content generation
- `get_feedback`: Human approval workflow
- `store_campaign`: Vault storage
- `send_emails`: Email distribution
- `create_trust_links`: Cross-agent delegation

---

## 🧪 Testing

Comprehensive test suite ensuring HushhMCP compliance:

```bash
# Run MailerPanda tests
python -m pytest tests/unit/test_agents.py::TestMailerPandaAgent -v

# Test coverage includes:
# ✅ Agent initialization and configuration
# ✅ Consent token validation
# ✅ Trust link creation and delegation
# ✅ AI content generation capabilities
# ✅ Scope enforcement and security
# ✅ Workflow structure validation
# ✅ Error handling and recovery
# ✅ Vault storage functionality
```

---

## 🔗 Cross-Agent Integration

### Trust Link Creation

```python
# Create trust link for another agent
trust_link = agent._create_trust_link_for_delegation(
    target_agent="agent_calendar",
    resource_type="email_template",
    resource_id="campaign_123",
    user_id="user_123"
)
```

### Resource Sharing

- Email templates can be shared with other agents
- Campaign data accessible through trust links
- Secure delegation with expiration controls

---

## 📊 Analytics & Monitoring

### Campaign Tracking

- Email delivery status monitoring
- Campaign performance metrics
- User engagement analytics
- Error rate tracking

### Consent Auditing

- Consent validation logs
- Permission usage tracking
- Privacy compliance reporting
- Scope enforcement audits

---

## 🛡️ Security Features

### Privacy Controls

- **Consent-First Architecture**: Every operation requires explicit consent
- **Scope Enforcement**: Granular permission controls
- **Data Encryption**: All vault storage encrypted
- **Audit Trails**: Complete operation logging

### Security Best Practices

- Environment variable configuration
- No hardcoded credentials
- Secure API communication
- Input validation and sanitization

---

## 🔄 API Integration

### REST Endpoints

When deployed with the FastAPI server:

```bash
POST /agents/mailerpanda/execute
{
    "user_input": "Create marketing email",
    "user_id": "user_123",
    "consent_tokens": {...},
    "user_email": "sender@example.com",
    "receiver_email": ["recipient@example.com"]
}
```

---

## 📈 Performance

- **Initialization**: < 1 second
- **Consent Validation**: < 100ms per operation
- **AI Generation**: 2-5 seconds (depends on content complexity)
- **Email Sending**: 1-3 seconds per email
- **Trust Link Creation**: < 200ms

---

## 🤝 Contributing

When extending MailerPanda:

1. **Maintain HushhMCP Compliance**: All new features must integrate with consent system
2. **Add Comprehensive Tests**: Follow existing test patterns
3. **Update Documentation**: Keep README and manifest current
4. **Security Review**: Ensure no privacy leaks or security vulnerabilities

---

## 📞 Support

For questions about MailerPanda agent:

- **Framework**: HushhMCP Documentation
- **AI Integration**: Google Gemini API Documentation  
- **Email Service**: Mailjet API Documentation
- **Testing**: pytest Documentation

---

## 📄 License

Part of HushhMCP framework - Privacy-first AI agent ecosystem.

**🎯 Build AI that respects trust. Build with consent. — Team Hushh** 🐼
