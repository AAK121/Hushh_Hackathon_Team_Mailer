# HushMCP Agent API - Frontend Integration Guide

## 🚀 Overview

The **HushMCP Agent API** is a comprehensive FastAPI-based REST API server that provides access to four powerful AI agents for various automation tasks. This API is designed for easy frontend integration with complete CORS support, detailed documentation, and robust error handling.

**Base URL**: `http://127.0.0.1:8001`  
**API Documentation**: `http://127.0.0.1:8001/docs`  
**Alternative Docs**: `http://127.0.0.1:8001/redoc`

---

## 📋 Table of Contents

1. [Quick Start](#-quick-start)
2. [Authentication & Consent](#-authentication--consent)
3. [Available Agents](#-available-agents)
4. [Core API Endpoints](#-core-api-endpoints)
5. [Agent-Specific Endpoints](#-agent-specific-endpoints)
6. [Frontend Integration Examples](#-frontend-integration-examples)
7. [Error Handling](#-error-handling)
8. [Response Formats](#-response-formats)
9. [WebSocket Support](#-websocket-support)
10. [Testing & Debugging](#-testing--debugging)

---

## 🚀 Quick Start

### 1. Start the API Server

```bash
cd /path/to/Pda_mailer
python api.py
```

The server will start on `http://127.0.0.1:8001`

### 2. Check API Health

```javascript
// Check if API is running
fetch('http://127.0.0.1:8001/health')
  .then(response => response.json())
  .then(data => console.log('API Status:', data));
```

### 3. List Available Agents

```javascript
// Get all available agents
fetch('http://127.0.0.1:8001/agents')
  .then(response => response.json())
  .then(data => {
    console.log('Available Agents:', data.agents);
    console.log('Total Agents:', data.total_agents);
  });
```

---

## 🔐 Authentication & Consent

The API uses **HushMCP consent tokens** for privacy-compliant access. Each agent requires specific consent tokens for different operations.

### Get Consent Token

```javascript
const getConsentToken = async (userId, agentId, scope) => {
  const response = await fetch('http://127.0.0.1:8001/consent/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      agent_id: agentId,
      scope: scope,
      expires_in_ms: 3600000 // 1 hour
    })
  });
  
  const result = await response.json();
  return result.token;
};
```

### Validate Token

```javascript
const validateToken = async (token, scope) => {
  const response = await fetch('http://127.0.0.1:8001/consent/validate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      token: token,
      scope: scope
    })
  });
  
  return response.json();
};
```

---

## 🤖 Available Agents

### 1. **AddToCalendar Agent** 📅
- **Purpose**: Extract calendar events from emails and text
- **Version**: 1.1.0
- **Capabilities**: AI-powered event extraction, calendar integration

### 2. **MailerPanda Agent** 📧
- **Purpose**: Mass email campaigns with human approval
- **Version**: 3.0.0
- **Capabilities**: Email composition, human-in-the-loop workflow, campaign management

### 3. **ChanduFinance Agent** 💰
- **Purpose**: Financial analysis and investment recommendations
- **Version**: 1.0.0
- **Capabilities**: DCF analysis, stock valuation, investment advice

### 4. **Relationship Memory Agent** 🧠
- **Purpose**: Personal relationship management
- **Version**: 2.0.0
- **Capabilities**: Contact management, memory storage, reminders, interactive chat

---

## 🌐 Core API Endpoints

### System Endpoints

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| `GET` | `/` | API root information | Server info and capabilities |
| `GET` | `/health` | Health check | Server status |
| `GET` | `/agents` | List all agents | Agent details and endpoints |
| `GET` | `/agents/{agent_id}/requirements` | Agent requirements | Required inputs and scopes |

### Consent Management

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| `POST` | `/consent/token` | Issue consent token | `{user_id, agent_id, scope, expires_in_ms}` |
| `POST` | `/consent/validate` | Validate token | `{token, scope}` |

---

## 🔧 Agent-Specific Endpoints

### 📅 AddToCalendar Agent

#### Execute Calendar Analysis
```javascript
POST /agents/addtocalendar/execute

// Request Body
{
  "user_id": "user123",
  "tokens": {
    "calendar.read": "token1",
    "calendar.write": "token2"
  },
  "email_content": "Meeting with John tomorrow at 3 PM",
  "action": "comprehensive_analysis",
  "vault_key": "optional_vault_key",
  "google_api_key": "your_google_api_key"
}

// Response
{
  "status": "success",
  "user_id": "user123",
  "message": "Calendar analysis completed",
  "events": [...],
  "processing_time": 1.23
}
```

#### Get Agent Status
```javascript
GET /agents/addtocalendar/status

// Response
{
  "agent_id": "agent_addtocalendar",
  "name": "AddToCalendar Agent",
  "version": "1.1.0",
  "status": "available",
  "required_scopes": ["calendar.read", "calendar.write"],
  "required_inputs": {...}
}
```

### 📧 MailerPanda Agent

#### Execute Email Campaign
```javascript
POST /agents/mailerpanda/execute

// Request Body
{
  "user_id": "user123",
  "tokens": {
    "email.read": "token1",
    "email.write": "token2"
  },
  "campaign_type": "newsletter",
  "target_audience": "subscribers",
  "content_brief": "Monthly product updates",
  "mode": "interactive",
  "mailjet_api_key": "your_mailjet_key",
  "mailjet_api_secret": "your_mailjet_secret"
}
```

#### Human Approval Workflow
```javascript
POST /agents/mailerpanda/approve

// Request Body
{
  "campaign_id": "campaign_123",
  "action": "approve", // or "reject", "modify", "regenerate"
  "feedback": "Please make the subject line more engaging"
}
```

#### Get Campaign Session
```javascript
GET /agents/mailerpanda/session/{campaign_id}

// Response
{
  "session_id": "campaign_123",
  "status": "pending_approval",
  "campaign_data": {...},
  "created_at": "2025-08-23T...",
  "requires_approval": true
}
```

### 💰 ChanduFinance Agent

#### Financial Analysis
```javascript
POST /agents/chandufinance/execute

// Request Body
{
  "user_id": "user123",
  "tokens": {
    "finance.read": "token1",
    "finance.analyze": "token2"
  },
  "company_name": "Apple Inc.",
  "analysis_type": "dcf_valuation",
  "vault_key": "optional_vault_key",
  "alpha_vantage_api_key": "your_api_key"
}

// Response
{
  "status": "success",
  "user_id": "user123",
  "message": "Financial analysis completed",
  "valuation_result": {...},
  "recommendations": [...],
  "processing_time": 5.67
}
```

### 🧠 Relationship Memory Agent

#### Basic Execution
```javascript
POST /agents/relationship_memory/execute

// Request Body
{
  "user_id": "user123",
  "tokens": {
    "vault.read.contacts": "token1",
    "vault.write.contacts": "token2",
    "vault.read.memory": "token3",
    "vault.write.memory": "token4"
  },
  "user_input": "add contact John with email john@example.com",
  "vault_key": "user_vault_key",
  "gemini_api_key": "your_gemini_key"
}
```

#### Proactive Check
```javascript
POST /agents/relationship_memory/proactive

// Request Body
{
  "user_id": "user123",
  "tokens": {...},
  "vault_key": "user_vault_key"
}
```

#### Interactive Chat Session
```javascript
// Start Chat Session
POST /agents/relationship_memory/chat/start

{
  "user_id": "user123",
  "tokens": {...},
  "vault_key": "user_vault_key",
  "session_name": "main_chat",
  "gemini_api_key": "your_gemini_key"
}

// Send Message
POST /agents/relationship_memory/chat/message

{
  "session_id": "user123_main_chat_20250823_123456",
  "message": "remember that Sarah loves photography"
}

// Get Chat History
GET /agents/relationship_memory/chat/{session_id}/history

// End Session
DELETE /agents/relationship_memory/chat/{session_id}

// List Active Sessions
GET /agents/relationship_memory/chat/sessions
```

---

## 💻 Frontend Integration Examples

### React Component Example

```jsx
import React, { useState, useEffect } from 'react';

const AgentInterface = () => {
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [result, setResult] = useState(null);

  // Load available agents
  useEffect(() => {
    fetch('http://127.0.0.1:8001/agents')
      .then(res => res.json())
      .then(data => setAgents(Object.values(data.agents)));
  }, []);

  // Execute agent
  const executeAgent = async (agentId, payload) => {
    try {
      const response = await fetch(`http://127.0.0.1:8001/agents/${agentId}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      const result = await response.json();
      setResult(result);
    } catch (error) {
      console.error('Agent execution failed:', error);
    }
  };

  return (
    <div>
      <h2>HushMCP Agents</h2>
      {agents.map(agent => (
        <div key={agent.name} className="agent-card">
          <h3>{agent.name} v{agent.version}</h3>
          <p>{agent.description}</p>
          <button onClick={() => setSelectedAgent(agent)}>
            Use Agent
          </button>
        </div>
      ))}
      
      {result && (
        <div className="result">
          <h3>Result</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};
```

### Vue.js Integration

```vue
<template>
  <div class="agent-dashboard">
    <h2>HushMCP Agent Dashboard</h2>
    
    <!-- Agent Selection -->
    <select v-model="selectedAgentId" @change="loadAgentRequirements">
      <option value="">Select an Agent</option>
      <option v-for="agent in agents" :key="agent.id" :value="agent.id">
        {{ agent.name }} - {{ agent.description }}
      </option>
    </select>
    
    <!-- Dynamic Form -->
    <form v-if="agentRequirements" @submit.prevent="executeAgent">
      <div v-for="(field, key) in agentRequirements" :key="key">
        <label>{{ key }}:</label>
        <input 
          v-model="formData[key]" 
          :type="getInputType(field)"
          :placeholder="field"
        />
      </div>
      <button type="submit" :disabled="loading">
        {{ loading ? 'Processing...' : 'Execute Agent' }}
      </button>
    </form>
    
    <!-- Results -->
    <div v-if="result" class="result">
      <h3>Result</h3>
      <pre>{{ JSON.stringify(result, null, 2) }}</pre>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      agents: [],
      selectedAgentId: '',
      agentRequirements: null,
      formData: {},
      result: null,
      loading: false
    };
  },
  
  async mounted() {
    await this.loadAgents();
  },
  
  methods: {
    async loadAgents() {
      try {
        const response = await fetch('http://127.0.0.1:8001/agents');
        const data = await response.json();
        this.agents = Object.entries(data.agents).map(([id, agent]) => ({
          id,
          ...agent
        }));
      } catch (error) {
        console.error('Failed to load agents:', error);
      }
    },
    
    async loadAgentRequirements() {
      if (!this.selectedAgentId) return;
      
      try {
        const response = await fetch(`http://127.0.0.1:8001/agents/${this.selectedAgentId}/requirements`);
        const data = await response.json();
        this.agentRequirements = data.required_inputs;
        this.formData = {};
      } catch (error) {
        console.error('Failed to load requirements:', error);
      }
    },
    
    async executeAgent() {
      this.loading = true;
      try {
        const endpoint = this.agents.find(a => a.id === this.selectedAgentId)?.endpoints?.execute;
        const response = await fetch(`http://127.0.0.1:8001${endpoint}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.formData)
        });
        
        this.result = await response.json();
      } catch (error) {
        console.error('Agent execution failed:', error);
      } finally {
        this.loading = false;
      }
    },
    
    getInputType(field) {
      if (field.includes('email')) return 'email';
      if (field.includes('password') || field.includes('key')) return 'password';
      return 'text';
    }
  }
};
</script>
```

### JavaScript Utility Class

```javascript
class HushMCPClient {
  constructor(baseUrl = 'http://127.0.0.1:8001') {
    this.baseUrl = baseUrl;
    this.tokens = new Map();
  }

  // Generic API call method
  async apiCall(endpoint, method = 'GET', body = null) {
    const config = {
      method,
      headers: { 'Content-Type': 'application/json' }
    };
    
    if (body) config.body = JSON.stringify(body);
    
    const response = await fetch(`${this.baseUrl}${endpoint}`, config);
    
    if (!response.ok) {
      throw new Error(`API call failed: ${response.status} ${response.statusText}`);
    }
    
    return response.json();
  }

  // Get all agents
  async getAgents() {
    return this.apiCall('/agents');
  }

  // Get agent requirements
  async getAgentRequirements(agentId) {
    return this.apiCall(`/agents/${agentId}/requirements`);
  }

  // Issue consent token
  async getConsentToken(userId, agentId, scope, expiresInMs = 3600000) {
    const result = await this.apiCall('/consent/token', 'POST', {
      user_id: userId,
      agent_id: agentId,
      scope: scope,
      expires_in_ms: expiresInMs
    });
    
    this.tokens.set(`${agentId}_${scope}`, result.token);
    return result.token;
  }

  // Execute AddToCalendar agent
  async executeAddToCalendar(userId, emailContent, options = {}) {
    return this.apiCall('/agents/addtocalendar/execute', 'POST', {
      user_id: userId,
      email_content: emailContent,
      action: options.action || 'comprehensive_analysis',
      tokens: options.tokens || {},
      vault_key: options.vaultKey,
      google_api_key: options.googleApiKey,
      ...options
    });
  }

  // Execute MailerPanda agent
  async executeMailerPanda(userId, campaignType, targetAudience, contentBrief, options = {}) {
    return this.apiCall('/agents/mailerpanda/execute', 'POST', {
      user_id: userId,
      campaign_type: campaignType,
      target_audience: targetAudience,
      content_brief: contentBrief,
      mode: options.mode || 'interactive',
      tokens: options.tokens || {},
      mailjet_api_key: options.mailjetApiKey,
      mailjet_api_secret: options.mailjetApiSecret,
      ...options
    });
  }

  // Execute ChanduFinance agent
  async executeChanduFinance(userId, companyName, analysisType, options = {}) {
    return this.apiCall('/agents/chandufinance/execute', 'POST', {
      user_id: userId,
      company_name: companyName,
      analysis_type: analysisType,
      tokens: options.tokens || {},
      vault_key: options.vaultKey,
      alpha_vantage_api_key: options.alphaVantageApiKey,
      ...options
    });
  }

  // Relationship Memory Agent - Chat Interface
  async startRelationshipChat(userId, options = {}) {
    return this.apiCall('/agents/relationship_memory/chat/start', 'POST', {
      user_id: userId,
      tokens: options.tokens || {},
      vault_key: options.vaultKey,
      session_name: options.sessionName || 'default',
      gemini_api_key: options.geminiApiKey,
      ...options
    });
  }

  async sendRelationshipMessage(sessionId, message) {
    return this.apiCall('/agents/relationship_memory/chat/message', 'POST', {
      session_id: sessionId,
      message: message
    });
  }

  async getRelationshipHistory(sessionId) {
    return this.apiCall(`/agents/relationship_memory/chat/${sessionId}/history`);
  }

  async endRelationshipChat(sessionId) {
    return this.apiCall(`/agents/relationship_memory/chat/${sessionId}`, 'DELETE');
  }

  // Health check
  async healthCheck() {
    return this.apiCall('/health');
  }
}

// Usage example
const client = new HushMCPClient();

// Example: Start a relationship chat
async function startChat() {
  try {
    const session = await client.startRelationshipChat('user123', {
      sessionName: 'main_chat',
      vaultKey: 'user_vault_key',
      geminiApiKey: 'your_gemini_key'
    });
    
    console.log('Chat started:', session.session_id);
    
    // Send a message
    const response = await client.sendRelationshipMessage(
      session.session_id, 
      'add contact John with email john@example.com'
    );
    
    console.log('Agent response:', response.agent_response);
  } catch (error) {
    console.error('Chat failed:', error);
  }
}
```

---

## ⚠️ Error Handling

### Standard Error Response Format

```javascript
{
  "detail": "Error message",
  "status_code": 400,
  "error_type": "ValidationError",
  "additional_info": {...}
}
```

### Common HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| `200` | Success | Request completed successfully |
| `400` | Bad Request | Invalid request parameters |
| `401` | Unauthorized | Invalid or missing consent token |
| `404` | Not Found | Agent or resource not found |
| `422` | Validation Error | Request body validation failed |
| `500` | Server Error | Internal server error |

### Frontend Error Handling

```javascript
async function handleApiCall(apiFunction) {
  try {
    const result = await apiFunction();
    return { success: true, data: result };
  } catch (error) {
    let errorMessage = 'An unexpected error occurred';
    
    if (error.response) {
      // API returned an error response
      switch (error.response.status) {
        case 400:
          errorMessage = 'Invalid request. Please check your input.';
          break;
        case 401:
          errorMessage = 'Authorization failed. Please check your tokens.';
          break;
        case 404:
          errorMessage = 'Resource not found.';
          break;
        case 422:
          errorMessage = 'Validation error. Please check required fields.';
          break;
        case 500:
          errorMessage = 'Server error. Please try again later.';
          break;
      }
    }
    
    return { 
      success: false, 
      error: errorMessage,
      details: error.response?.data || error.message 
    };
  }
}
```

---

## 📊 Response Formats

### Successful Response Pattern

```javascript
{
  "status": "success",
  "agent_id": "agent_name",
  "user_id": "user123",
  "message": "Operation completed successfully",
  "results": {...}, // Agent-specific results
  "processing_time": 1.23,
  "timestamp": "2025-08-23T01:23:45.678Z"
}
```

### Error Response Pattern

```javascript
{
  "status": "error",
  "agent_id": "agent_name",
  "user_id": "user123",
  "message": "Error description",
  "errors": ["Detailed error messages"],
  "processing_time": 0.15
}
```

---

## 🔌 WebSocket Support

For real-time updates (future enhancement), the API can be extended with WebSocket support:

```javascript
// Example WebSocket connection (when implemented)
const ws = new WebSocket('ws://127.0.0.1:8001/ws/relationship_memory');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Real-time update:', data);
};

ws.send(JSON.stringify({
  type: 'chat_message',
  session_id: 'session123',
  message: 'Hello'
}));
```

---

## 🧪 Testing & Debugging

### Test API Availability

```javascript
const testAPI = async () => {
  try {
    const health = await fetch('http://127.0.0.1:8001/health');
    const data = await health.json();
    console.log('API Health:', data);
    
    const agents = await fetch('http://127.0.0.1:8001/agents');
    const agentData = await agents.json();
    console.log('Available Agents:', agentData.total_agents);
    
    return true;
  } catch (error) {
    console.error('API not available:', error);
    return false;
  }
};
```

### Debug Mode

Enable detailed logging by setting debug headers:

```javascript
const headers = {
  'Content-Type': 'application/json',
  'X-Debug': 'true',
  'X-Trace-Id': `trace_${Date.now()}`
};
```

### Interactive API Testing

Use the built-in Swagger UI for interactive testing:
- **Swagger UI**: `http://127.0.0.1:8001/docs`
- **ReDoc**: `http://127.0.0.1:8001/redoc`

---

## 🔧 Configuration

### Environment Variables

```bash
# Required API Keys
GEMINI_API_KEY=your_gemini_api_key
MAILJET_API_KEY=your_mailjet_api_key
MAILJET_API_SECRET=your_mailjet_secret
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key

# Server Configuration
API_HOST=127.0.0.1
API_PORT=8001
DEBUG_MODE=false

# CORS Configuration (for production)
ALLOWED_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
```

### CORS Configuration

The API includes CORS middleware for frontend integration:

```python
# In api.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📚 Additional Resources

### Sample Frontend Applications

1. **React Chat Interface**: `relationship_memory_chat.html` - Complete chat interface
2. **API Test Suite**: `test_interactive_chat_api.py` - Comprehensive testing
3. **Integration Examples**: Various code examples above

### API Documentation

- **Interactive Docs**: http://127.0.0.1:8001/docs
- **OpenAPI Spec**: http://127.0.0.1:8001/openapi.json
- **Alternative Docs**: http://127.0.0.1:8001/redoc

### Support & Troubleshooting

1. **Check API Health**: `GET /health`
2. **Validate Tokens**: `POST /consent/validate`
3. **Review Logs**: Server console output
4. **Test Endpoints**: Use Swagger UI for testing

---

## 🎯 Quick Integration Checklist

- [ ] ✅ API server running on port 8001
- [ ] ✅ CORS configured for your domain
- [ ] ✅ Environment variables set up
- [ ] ✅ Consent tokens implemented
- [ ] ✅ Error handling in place
- [ ] ✅ Agent requirements understood
- [ ] ✅ Response formats handled
- [ ] ✅ Interactive testing completed

**The HushMCP Agent API is ready for frontend integration!** 🚀

For questions or support, refer to the interactive documentation at `http://127.0.0.1:8001/docs` or examine the provided code examples.
