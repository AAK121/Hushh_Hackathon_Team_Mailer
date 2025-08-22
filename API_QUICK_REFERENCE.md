# HushMCP API - Quick Reference for Frontend Developers

## 🚀 API Base Information

**Base URL**: `http://127.0.0.1:8001`  
**Protocol**: REST API with JSON  
**Authentication**: HushMCP Consent Tokens  
**CORS**: Enabled for all origins  

---

## 📊 Agent Summary Table

| Agent | ID | Version | Primary Function | Key Endpoints |
|-------|----|---------|-----------------|--------------| 
| **AddToCalendar** | `agent_addtocalendar` | 1.1.0 | Calendar event extraction | `/execute`, `/status` |
| **MailerPanda** | `agent_mailerpanda` | 3.0.0 | Email campaigns + approval | `/execute`, `/approve`, `/status`, `/session/{id}` |
| **ChanduFinance** | `agent_chandufinance` | 1.0.0 | Financial analysis & DCF | `/execute`, `/status` |
| **Relationship Memory** | `agent_relationship_memory` | 2.0.0 | Contact & memory management | `/execute`, `/proactive`, `/status`, `/chat/*` |

---

## 🔗 Essential Endpoints Quick Reference

### System Endpoints
```
GET  /                          # API info
GET  /health                    # Health check  
GET  /agents                    # List all agents
GET  /agents/{id}/requirements  # Agent requirements
```

### Authentication
```
POST /consent/token             # Issue consent token
POST /consent/validate          # Validate token
```

### Agent Execution Pattern
```
POST /agents/{agent_name}/execute
POST /agents/{agent_name}/status
```

---

## 💻 JavaScript Quick Start Templates

### 1. Basic API Client
```javascript
class HushMCPAPI {
  constructor() {
    this.baseURL = 'http://127.0.0.1:8001';
  }
  
  async get(endpoint) {
    const response = await fetch(`${this.baseURL}${endpoint}`);
    return response.json();
  }
  
  async post(endpoint, data) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  }
}

const api = new HushMCPAPI();
```

### 2. Agent Execution Template
```javascript
const executeAgent = async (agentName, payload) => {
  try {
    const result = await api.post(`/agents/${agentName}/execute`, payload);
    
    if (result.status === 'success') {
      console.log('Success:', result.message);
      return result.results;
    } else {
      console.error('Error:', result.message);
      return null;
    }
  } catch (error) {
    console.error('API Error:', error);
    return null;
  }
};
```

### 3. Token Management
```javascript
const tokenManager = {
  tokens: new Map(),
  
  async getToken(userId, agentId, scope) {
    const key = `${agentId}_${scope}`;
    
    if (this.tokens.has(key)) {
      return this.tokens.get(key);
    }
    
    const response = await api.post('/consent/token', {
      user_id: userId,
      agent_id: agentId,
      scope: scope,
      expires_in_ms: 3600000
    });
    
    this.tokens.set(key, response.token);
    return response.token;
  }
};
```

---

## 🎯 Common Request Patterns

### AddToCalendar Agent
```javascript
const analyzeCalendar = async (emailContent) => {
  return executeAgent('addtocalendar', {
    user_id: 'user123',
    tokens: {
      'calendar.read': await tokenManager.getToken('user123', 'agent_addtocalendar', 'calendar.read'),
      'calendar.write': await tokenManager.getToken('user123', 'agent_addtocalendar', 'calendar.write')
    },
    email_content: emailContent,
    action: 'comprehensive_analysis',
    google_api_key: 'your_google_api_key'
  });
};
```

### MailerPanda Agent
```javascript
const createCampaign = async (campaignData) => {
  return executeAgent('mailerpanda', {
    user_id: 'user123',
    tokens: {
      'email.read': await tokenManager.getToken('user123', 'agent_mailerpanda', 'email.read'),
      'email.write': await tokenManager.getToken('user123', 'agent_mailerpanda', 'email.write')
    },
    campaign_type: campaignData.type,
    target_audience: campaignData.audience,
    content_brief: campaignData.brief,
    mode: 'interactive',
    mailjet_api_key: 'your_mailjet_key',
    mailjet_api_secret: 'your_mailjet_secret'
  });
};
```

### Relationship Memory Chat
```javascript
const chatManager = {
  currentSession: null,
  
  async startChat(userId) {
    const response = await api.post('/agents/relationship_memory/chat/start', {
      user_id: userId,
      tokens: {
        'vault.read.contacts': await tokenManager.getToken(userId, 'agent_relationship_memory', 'vault.read.contacts'),
        'vault.write.contacts': await tokenManager.getToken(userId, 'agent_relationship_memory', 'vault.write.contacts'),
        'vault.read.memory': await tokenManager.getToken(userId, 'agent_relationship_memory', 'vault.read.memory'),
        'vault.write.memory': await tokenManager.getToken(userId, 'agent_relationship_memory', 'vault.write.memory')
      },
      vault_key: 'user_vault_key',
      session_name: 'main_chat',
      gemini_api_key: 'your_gemini_key'
    });
    
    this.currentSession = response.session_id;
    return response;
  },
  
  async sendMessage(message) {
    if (!this.currentSession) throw new Error('No active session');
    
    return api.post('/agents/relationship_memory/chat/message', {
      session_id: this.currentSession,
      message: message
    });
  }
};
```

---

## 🔧 Response Handling Patterns

### Success Response Handler
```javascript
const handleSuccess = (response) => {
  console.log(`✅ ${response.message}`);
  console.log(`⏱️ Processing time: ${response.processing_time}s`);
  
  if (response.results) {
    return response.results;
  }
  
  return response;
};
```

### Error Response Handler
```javascript
const handleError = (error, context = '') => {
  console.error(`❌ Error ${context}:`, error);
  
  if (error.response) {
    switch (error.response.status) {
      case 400:
        return 'Invalid request parameters';
      case 401:
        return 'Authentication required';
      case 404:
        return 'Resource not found';
      case 422:
        return 'Validation failed';
      case 500:
        return 'Server error';
      default:
        return 'Unknown error occurred';
    }
  }
  
  return error.message || 'Network error';
};
```

---

## 🎨 UI Integration Patterns

### React Hook for Agent
```javascript
import { useState, useCallback } from 'react';

const useHushMCPAgent = (agentName) => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  
  const execute = useCallback(async (payload) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await executeAgent(agentName, payload);
      setResult(response);
      return response;
    } catch (err) {
      setError(handleError(err));
      return null;
    } finally {
      setLoading(false);
    }
  }, [agentName]);
  
  return { execute, loading, result, error };
};

// Usage
const MyComponent = () => {
  const { execute, loading, result, error } = useHushMCPAgent('addtocalendar');
  
  const handleSubmit = async (formData) => {
    await execute({
      user_id: 'user123',
      email_content: formData.emailContent,
      // ... other params
    });
  };
  
  return (
    <div>
      {loading && <div>Processing...</div>}
      {error && <div className="error">{error}</div>}
      {result && <div className="success">{result.message}</div>}
    </div>
  );
};
```

### Vue Composable
```javascript
import { ref, computed } from 'vue';

export const useHushMCPAgent = (agentName) => {
  const loading = ref(false);
  const result = ref(null);
  const error = ref(null);
  
  const isSuccess = computed(() => result.value?.status === 'success');
  
  const execute = async (payload) => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await executeAgent(agentName, payload);
      result.value = response;
      return response;
    } catch (err) {
      error.value = handleError(err);
      return null;
    } finally {
      loading.value = false;
    }
  };
  
  const reset = () => {
    result.value = null;
    error.value = null;
  };
  
  return {
    execute,
    reset,
    loading: computed(() => loading.value),
    result: computed(() => result.value),
    error: computed(() => error.value),
    isSuccess
  };
};
```

---

## 🔍 Testing Snippets

### Health Check
```javascript
const testAPI = async () => {
  try {
    const health = await api.get('/health');
    console.log('✅ API is healthy:', health);
    
    const agents = await api.get('/agents');
    console.log(`✅ ${agents.total_agents} agents available`);
    
    return true;
  } catch (error) {
    console.error('❌ API test failed:', error);
    return false;
  }
};
```

### Agent Availability Check
```javascript
const checkAgent = async (agentId) => {
  try {
    const status = await api.get(`/agents/${agentId}/status`);
    console.log(`Agent ${agentId}:`, status.status);
    return status.status === 'available';
  } catch (error) {
    console.error(`Agent ${agentId} check failed:`, error);
    return false;
  }
};
```

---

## 📱 Mobile/React Native Integration

### Fetch Configuration for Mobile
```javascript
const mobileAPI = {
  baseURL: 'http://127.0.0.1:8001', // Use actual IP for device testing
  
  async request(endpoint, options = {}) {
    const config = {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      ...options
    };
    
    const response = await fetch(`${this.baseURL}${endpoint}`, config);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
  }
};
```

---

## 🎯 Best Practices Summary

### ✅ Do's
- Always check API health before making requests
- Implement proper error handling for all status codes
- Cache consent tokens until they expire
- Use the interactive docs for testing
- Validate required fields before sending requests
- Handle loading states in UI
- Implement retry logic for network failures

### ❌ Don'ts  
- Don't hardcode API keys in frontend code
- Don't ignore error responses
- Don't make requests without proper tokens
- Don't forget to handle async operations
- Don't assume all requests will succeed
- Don't ignore CORS policies in production

---

## 🚀 Ready-to-Use Code Snippets

### Complete Agent Tester
```javascript
const testAllAgents = async () => {
  const agents = ['addtocalendar', 'mailerpanda', 'chandufinance', 'relationship_memory'];
  
  for (const agent of agents) {
    const available = await checkAgent(`agent_${agent}`);
    console.log(`${agent}: ${available ? '✅' : '❌'}`);
  }
};
```

### Quick Demo Function
```javascript
const runQuickDemo = async () => {
  // Test AddToCalendar
  const calendarResult = await analyzeCalendar('Meeting with John tomorrow at 3 PM');
  console.log('Calendar Analysis:', calendarResult);
  
  // Test Relationship Memory Chat
  await chatManager.startChat('demo_user');
  const chatResult = await chatManager.sendMessage('add contact Alice with email alice@example.com');
  console.log('Chat Response:', chatResult);
};
```

**This API is production-ready and easy to integrate!** 🎉
