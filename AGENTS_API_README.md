# HushhMCP Agents API - Frontend Integration Guide

## Overview

The HushhMCP platform provides a unified REST API for interacting with four powerful AI agents. This guide contains everything you need to integrate these agents into your frontend application.

## 🚀 Quick Start

### Base URL
```
http://127.0.0.1:8001
```

### API Documentation
- **Swagger UI**: http://127.0.0.1:8001/docs
- **ReDoc**: http://127.0.0.1:8001/redoc

## 🤖 Available Agents

| Agent | Purpose | Version | Status |
|-------|---------|---------|--------|
| **AddToCalendar** | Email-to-calendar event extraction | 1.1.0 | ✅ Available |
| **MailerPanda** | AI-powered mass email campaigns | 3.0.0 | ✅ Available |
| **ChanduFinance** | Financial valuation & DCF analysis | 1.0.0 | ✅ Available |
| **Relationship Memory** | Contact & relationship management | 2.0.0 | ✅ Available |

---

## 📋 Common API Endpoints

### 1. Discover All Agents
```http
GET /agents
```

**Response:**
```json
{
  "agents": {
    "agent_addtocalendar": {...},
    "agent_mailerpanda": {...},
    "agent_chandufinance": {...},
    "agent_relationship_memory": {...}
  },
  "total_agents": 4
}
```

### 2. Health Check
```http
GET /health
```

### 3. Get Agent Requirements
```http
GET /agents/{agent_id}/requirements
```

---

## 🔐 Authentication & Consent

All agents require **HushhMCP consent tokens** for operation. Each agent needs specific scopes:

### Token Format
```
HCT:<base64_encoded_token_data>.<signature>
```

### Required Scopes by Agent

| Agent | Required Scopes |
|-------|----------------|
| **AddToCalendar** | `vault.read.email`, `vault.write.calendar` |
| **MailerPanda** | `vault.read.email`, `vault.write.email`, `vault.read.file`, `vault.write.file`, `custom.temporary` |
| **ChanduFinance** | `vault.read.finance`, `vault.write.file`, `agent.finance.analyze`, `custom.session.write` |
| **Relationship Memory** | `vault.read.contacts`, `vault.write.contacts`, `vault.read.memory`, `vault.write.memory`, `vault.read.reminder`, `vault.write.reminder` |

---

## 📧 AddToCalendar Agent

### Purpose
Extracts calendar events from emails using AI and adds them to Google Calendar.

### Execute Agent
```http
POST /agents/addtocalendar/execute
```

**Request Body:**
```json
{
  "user_id": "user123",
  "email_token": "HCT:email_token_here",
  "calendar_token": "HCT:calendar_token_here",
  "google_access_token": "google_oauth_token",
  "action": "comprehensive_analysis",
  "confidence_threshold": 0.7,
  "max_emails": 50
}
```

**Actions Available:**
- `comprehensive_analysis` - Full email analysis and calendar creation
- `manual_event` - Create specific manual event
- `analyze_only` - Email analysis without calendar creation

**Response:**
```json
{
  "status": "success",
  "user_id": "user123",
  "action": "comprehensive_analysis",
  "results": {
    "events_created": 3,
    "emails_processed": 25,
    "calendar_events": [...]
  },
  "processing_time": 2.45
}
```

### Get Status
```http
GET /agents/addtocalendar/status
```

### Frontend Integration Example
```javascript
const addToCalendar = async (userTokens) => {
  const response = await fetch('/agents/addtocalendar/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: currentUser.id,
      email_token: userTokens.email,
      calendar_token: userTokens.calendar,
      google_access_token: googleAuth.accessToken,
      action: 'comprehensive_analysis',
      max_emails: 50
    })
  });
  
  return await response.json();
};
```

---

## 📨 MailerPanda Agent

### Purpose
Creates and sends AI-generated email campaigns with human-in-the-loop approval.

### Execute Agent
```http
POST /agents/mailerpanda/execute
```

**Request Body:**
```json
{
  "user_id": "user123",
  "consent_tokens": {
    "vault.read.email": "HCT:token1",
    "vault.write.email": "HCT:token2",
    "vault.read.file": "HCT:token3",
    "vault.write.file": "HCT:token4",
    "custom.temporary": "HCT:token5"
  },
  "user_input": "Create marketing campaign for new product launch",
  "mode": "interactive",
  "sender_email": "marketing@company.com",
  "recipient_emails": ["customer1@example.com", "customer2@example.com"],
  "require_approval": true
}
```

**Modes Available:**
- `interactive` - Full interactive mode with approval steps
- `headless` - Automated execution without interaction
- `demo` - Demo mode for testing

**Response:**
```json
{
  "status": "success",
  "user_id": "user123",
  "campaign_id": "camp_12345",
  "approval_status": "pending",
  "emails_generated": 2,
  "requires_approval": true,
  "processing_time": 3.21
}
```

### Approve Campaign
```http
POST /agents/mailerpanda/approve
```

**Request Body:**
```json
{
  "user_id": "user123",
  "campaign_id": "camp_12345",
  "approval_decision": "approve",
  "consent_tokens": {...}
}
```

### Get Status
```http
GET /agents/mailerpanda/status
```

### Get Campaign Session
```http
GET /agents/mailerpanda/session/{campaign_id}
```

### Frontend Integration Example
```javascript
const createEmailCampaign = async (campaignDescription, userTokens) => {
  // Step 1: Create campaign
  const response = await fetch('/agents/mailerpanda/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: currentUser.id,
      consent_tokens: userTokens,
      user_input: campaignDescription,
      mode: 'interactive',
      require_approval: true
    })
  });
  
  const result = await response.json();
  
  // Step 2: Handle approval if needed
  if (result.requires_approval) {
    const approval = await showApprovalDialog(result.campaign_id);
    
    const approvalResponse = await fetch('/agents/mailerpanda/approve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: currentUser.id,
        campaign_id: result.campaign_id,
        approval_decision: approval ? 'approve' : 'reject',
        consent_tokens: userTokens
      })
    });
    
    return await approvalResponse.json();
  }
  
  return result;
};
```

---

## 💰 ChanduFinance Agent

### Purpose
Performs financial valuation analysis using DCF models and provides investment recommendations.

### Execute Agent
```http
POST /agents/chandufinance/execute
```

**Request Body:**
```json
{
  "user_id": "user123",
  "token": "HCT:finance_token_here",
  "ticker": "AAPL",
  "command": "run_valuation",
  "market_price": 175.50,
  "wacc": 0.09,
  "terminal_growth_rate": 0.025
}
```

**Commands Available:**
- `run_valuation` - Complete DCF valuation analysis
- `get_financials` - Retrieve financial data for a company
- `run_sensitivity` - Perform sensitivity analysis on valuation
- `market_analysis` - Compare market price with intrinsic value

**Response:**
```json
{
  "status": "success",
  "agent_id": "chandufinance",
  "user_id": "user123",
  "ticker": "AAPL",
  "results": {
    "executive_summary": {
      "fair_value_per_share": 185.32,
      "current_market_price": 175.50,
      "upside_potential": 5.59
    },
    "dcf_analysis": {
      "enterprise_value": 2500000000000,
      "equity_value": 2200000000000,
      "shares_outstanding": 15000000000,
      "fair_value_per_share": 185.32
    },
    "investment_recommendation": {
      "recommendation": "BUY",
      "confidence": "High",
      "price_target": 185.32,
      "reasoning": "Strong fundamentals with upside potential"
    }
  },
  "processing_time": 0.156
}
```

### Get Status
```http
GET /agents/chandufinance/status
```

### Frontend Integration Example
```javascript
const analyzeStock = async (ticker, marketPrice, userToken) => {
  const response = await fetch('/agents/chandufinance/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: currentUser.id,
      token: userToken,
      ticker: ticker.toUpperCase(),
      command: 'run_valuation',
      market_price: marketPrice,
      wacc: 0.09,
      terminal_growth_rate: 0.025
    })
  });
  
  const result = await response.json();
  
  if (result.status === 'success') {
    displayValuationResults({
      fairValue: result.results.dcf_analysis.fair_value_per_share,
      recommendation: result.results.investment_recommendation.recommendation,
      upside: result.results.executive_summary.upside_potential
    });
  }
  
  return result;
};

// Sensitivity Analysis
const runSensitivityAnalysis = async (ticker, userToken) => {
  return await fetch('/agents/chandufinance/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: currentUser.id,
      token: userToken,
      ticker: ticker,
      command: 'run_sensitivity',
      wacc: 0.09,
      terminal_growth_rate: 0.025,
      wacc_range: [0.08, 0.10],
      growth_range: [0.02, 0.03]
    })
  });
};
```

---

## 👥 Relationship Memory Agent

### Purpose
Manages contacts, relationship memories, and smart reminders using AI-powered natural language processing.

### Execute Agent
```http
POST /agents/relationship_memory/execute
```

**Request Body:**
```json
{
  "user_id": "user123",
  "tokens": {
    "vault.read.contacts": "HCT:token1",
    "vault.write.contacts": "HCT:token2",
    "vault.read.memory": "HCT:token3",
    "vault.write.memory": "HCT:token4",
    "vault.read.reminder": "HCT:token5",
    "vault.write.reminder": "HCT:token6"
  },
  "user_input": "Add contact John Doe with email john@example.com and phone +1234567890",
  "vault_key": "contacts_vault_key",
  "is_startup": false
}
```

**Response:**
```json
{
  "status": "success",
  "agent_id": "relationship_memory",
  "user_id": "user123",
  "message": "Contact John Doe added successfully",
  "results": {
    "action": "contact_added",
    "contact_id": "contact_123",
    "details": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1234567890"
    }
  },
  "processing_time": 0.89
}
```

### Proactive Checks
```http
POST /agents/relationship_memory/proactive
```

**Request Body:**
```json
{
  "user_id": "user123",
  "tokens": {
    "vault.read.contacts": "HCT:token1",
    "vault.read.memory": "HCT:token2",
    "vault.read.reminder": "HCT:token3"
  },
  "vault_key": "memory_vault_key"
}
```

### Get Status
```http
GET /agents/relationship_memory/status
```

### Frontend Integration Example
```javascript
const manageRelationship = async (userInput, userTokens) => {
  const response = await fetch('/agents/relationship_memory/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: currentUser.id,
      tokens: userTokens,
      user_input: userInput,
      is_startup: false
    })
  });
  
  return await response.json();
};

// Proactive reminder checks
const checkReminders = async (userTokens) => {
  const response = await fetch('/agents/relationship_memory/proactive', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: currentUser.id,
      tokens: userTokens
    })
  });
  
  const result = await response.json();
  
  if (result.status === 'success' && result.results.reminders) {
    showReminders(result.results.reminders);
  }
  
  return result;
};

// Natural language contact management
const processContactCommand = async (command, userTokens) => {
  const commands = [
    "Add contact Sarah Johnson with email sarah@company.com",
    "Set reminder to call John next Tuesday",
    "Remember that Mike likes coffee meetings",
    "Update Lisa's phone number to +1987654321",
    "Find all contacts from Google company"
  ];
  
  return await manageRelationship(command, userTokens);
};
```

---

## 🛠️ Error Handling

All agents return consistent error responses:

```json
{
  "status": "error",
  "agent_id": "agent_name",
  "user_id": "user123",
  "errors": ["Error message here"],
  "processing_time": 0.05
}
```

### Common Error Codes

| Status Code | Meaning |
|-------------|---------|
| `200` | Success |
| `400` | Bad Request - Invalid parameters |
| `401` | Unauthorized - Invalid or missing tokens |
| `404` | Not Found - Agent or resource not found |
| `422` | Validation Error - Request validation failed |
| `500` | Internal Server Error |

### Frontend Error Handling Example
```javascript
const handleAgentResponse = async (response) => {
  const data = await response.json();
  
  if (response.status === 200 && data.status === 'success') {
    return data;
  }
  
  // Handle different error types
  switch (response.status) {
    case 400:
      throw new Error(`Invalid request: ${data.errors?.join(', ')}`);
    case 401:
      throw new Error('Authentication failed. Please check your tokens.');
    case 404:
      throw new Error('Agent not found.');
    case 422:
      throw new Error(`Validation error: ${data.detail}`);
    default:
      throw new Error(`Agent error: ${data.errors?.join(', ') || 'Unknown error'}`);
  }
};
```

---

## 🚀 Complete Frontend Integration Example

```javascript
class HushhMCPClient {
  constructor(baseURL = 'http://127.0.0.1:8001') {
    this.baseURL = baseURL;
  }

  async makeRequest(endpoint, method = 'GET', body = null) {
    const config = {
      method,
      headers: { 'Content-Type': 'application/json' }
    };
    
    if (body) {
      config.body = JSON.stringify(body);
    }
    
    const response = await fetch(`${this.baseURL}${endpoint}`, config);
    return await handleAgentResponse(response);
  }

  // Get all available agents
  async getAgents() {
    return await this.makeRequest('/agents');
  }

  // AddToCalendar Agent
  async addToCalendar(userId, tokens, googleToken, options = {}) {
    return await this.makeRequest('/agents/addtocalendar/execute', 'POST', {
      user_id: userId,
      email_token: tokens.email,
      calendar_token: tokens.calendar,
      google_access_token: googleToken,
      action: options.action || 'comprehensive_analysis',
      ...options
    });
  }

  // MailerPanda Agent
  async createEmailCampaign(userInput, userTokens, options = {}) {
    return await this.makeRequest('/agents/mailerpanda/execute', 'POST', {
      user_id: options.userId,
      consent_tokens: userTokens,
      user_input: userInput,
      mode: options.mode || 'interactive',
      ...options
    });
  }

  async approveCampaign(campaignId, decision, userTokens) {
    return await this.makeRequest('/agents/mailerpanda/approve', 'POST', {
      user_id: userTokens.userId,
      campaign_id: campaignId,
      approval_decision: decision,
      consent_tokens: userTokens
    });
  }

  // ChanduFinance Agent
  async analyzeStock(ticker, command, userToken, options = {}) {
    return await this.makeRequest('/agents/chandufinance/execute', 'POST', {
      user_id: options.userId,
      token: userToken,
      ticker: ticker.toUpperCase(),
      command: command,
      ...options
    });
  }

  // Relationship Memory Agent
  async manageRelationship(userInput, userTokens, options = {}) {
    return await this.makeRequest('/agents/relationship_memory/execute', 'POST', {
      user_id: options.userId,
      tokens: userTokens,
      user_input: userInput,
      vault_key: options.vaultKey,
      is_startup: options.isStartup || false
    });
  }

  async checkProactiveReminders(userTokens, options = {}) {
    return await this.makeRequest('/agents/relationship_memory/proactive', 'POST', {
      user_id: options.userId,
      tokens: userTokens,
      vault_key: options.vaultKey
    });
  }
}

// Usage example
const hushhAPI = new HushhMCPClient();

// Initialize and use agents
async function initializeApp() {
  try {
    // Get available agents
    const agents = await hushhAPI.getAgents();
    console.log(`Found ${agents.total_agents} agents:`, Object.keys(agents.agents));

    // Example: Analyze a stock
    const stockAnalysis = await hushhAPI.analyzeStock('AAPL', 'run_valuation', userFinanceToken, {
      userId: currentUser.id,
      market_price: 175.50,
      wacc: 0.09
    });

    // Example: Add calendar events
    const calendarResult = await hushhAPI.addToCalendar(
      currentUser.id,
      { email: emailToken, calendar: calendarToken },
      googleAccessToken,
      { action: 'comprehensive_analysis', max_emails: 25 }
    );

    // Example: Manage relationships
    const relationshipResult = await hushhAPI.manageRelationship(
      "Add contact Alice Smith with email alice@example.com",
      relationshipTokens,
      { userId: currentUser.id }
    );

  } catch (error) {
    console.error('HushhMCP API Error:', error.message);
  }
}
```

---

## 🔒 Security Best Practices

1. **Token Management**
   - Store consent tokens securely (encrypted storage)
   - Implement token refresh mechanisms
   - Validate token expiry before API calls

2. **HTTPS in Production**
   - Always use HTTPS in production environments
   - Implement proper CORS policies

3. **Rate Limiting**
   - Implement client-side rate limiting for API calls
   - Handle 429 Too Many Requests responses

4. **Error Logging**
   - Log API errors for debugging
   - Don't expose sensitive data in error messages

---

## 📞 Support & Documentation

- **API Documentation**: http://127.0.0.1:8001/docs
- **Health Check**: http://127.0.0.1:8001/health
- **Agent Discovery**: http://127.0.0.1:8001/agents

For additional support or custom integrations, refer to the individual agent documentation or contact the HushhMCP development team.

---

## 🎯 Quick Integration Checklist

- [ ] Set up HushhMCP API server (`python api.py`)
- [ ] Obtain necessary consent tokens for each agent
- [ ] Implement error handling for API responses
- [ ] Test each agent endpoint with sample data
- [ ] Set up proper authentication flow
- [ ] Implement retry mechanisms for failed requests
- [ ] Add loading states for long-running operations
- [ ] Configure CORS for your frontend domain
- [ ] Set up logging and monitoring
- [ ] Test in production environment

---

*This document covers all four HushhMCP agents and provides everything needed for successful frontend integration. Each agent offers unique capabilities while following consistent API patterns for ease of development.*
