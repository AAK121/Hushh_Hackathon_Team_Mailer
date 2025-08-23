# 🚀 Frontend Integration Guide for HushMCP Agent API

## Table of Contents
1. [Overview](#overview)
2. [MailerPanda Agent Functionalities](#mailerpanda-agent-functionalities)
3. [All Available Agents](#all-available-agents)
4. [API Endpoints Reference](#api-endpoints-reference)
5. [Frontend Integration Examples](#frontend-integration-examples)
6. [Authentication & Security](#authentication--security)
7. [Error Handling](#error-handling)
8. [Code Examples](#code-examples)
9. [Best Practices](#best-practices)

## Overview

This guide provides comprehensive documentation for accessing all backend functionalities through the frontend. The backend runs on **port 8001** and provides 4 AI-powered agents with extensive capabilities.

**Base URL:** `http://localhost:8001`

## MailerPanda Agent Functionalities

The MailerPanda agent has **13 core functionalities** organized into multiple operational modes:

### 🔥 Core Features (13 Functionalities)

| # | Functionality | Description | API Access |
|---|---------------|-------------|------------|
| 1 | **AI Content Generation** | Gemini-2.0-flash powered email drafting | `POST /agents/mailerpanda/execute` |
| 2 | **Human-in-the-Loop Approval** | Interactive approval workflow | Built into interactive mode |
| 3 | **LangGraph State Management** | Advanced workflow orchestration | Internal processing |
| 4 | **Mass Email with Excel** | Bulk email campaigns from spreadsheet | File upload + execution |
| 5 | **Dynamic Placeholder Detection** | Smart template variable recognition | Automatic in content generation |
| 6 | **Description-Based Personalization** | ✨ NEW: AI customization per contact description | Automatic with description column |
| 7 | **Real-time Status Tracking** | Live email delivery monitoring | Campaign status endpoints |
| 8 | **HushMCP Consent Management** | Privacy-first operation validation | Token-based authentication |
| 9 | **Secure Vault Data Storage** | Encrypted campaign data storage | Vault storage APIs |
| 10 | **Trust Link Agent Delegation** | Cross-agent communication | Automatic delegation |
| 11 | **Interactive Feedback Loop** | Iterative content improvement | Feedback processing |
| 12 | **Error Recovery & Logging** | Comprehensive error handling | Status reporting |
| 13 | **Cross-Agent Communication** | Integration with other agents | Trust link system |

### 📧 Email Campaign Modes

```javascript
// 1. Interactive Mode (Full AI + Human Approval)
const interactiveMode = {
  mode: "interactive",
  features: [
    "AI content generation",
    "Human approval workflow", 
    "Real-time feedback",
    "Dynamic placeholder detection",
    "Description-based personalization", // ✨ NEW
    "Mass email support",
    "Vault storage",
    "Trust link creation"
  ]
};

// 2. Demo Mode (Safe Testing)
const demoMode = {
  mode: "demo",
  features: [
    "Simulated email sending",
    "Mock delivery statistics",
    "No actual emails sent",
    "Safe for testing"
  ]
};

// 3. Headless Mode (API-Only)
const headlessMode = {
  mode: "headless",
  features: [
    "Automated processing",
    "No user interaction",
    "Batch operations",
    "API-driven workflow"
  ]
};
```

### ✨ NEW: Description-Based Email Personalization

**Version 3.1.0 Feature** - AI-powered individual email customization based on contact descriptions.

#### 📊 Excel File Structure

```javascript
// Enhanced Excel file with description column
const excelStructure = {
  required_columns: ['name', 'email', 'company_name'],
  optional_columns: ['description'], // ✨ NEW FEATURE
  example_data: [
    {
      name: 'John Smith',
      email: 'john@techcorp.com',
      company_name: 'TechCorp',
      description: 'Long-time customer, prefers technical details and documentation'
    },
    {
      name: 'Sarah Johnson',
      email: 'sarah@startup.io', 
      company_name: 'StartupX',
      description: 'New to our services, needs gentle introduction and support info'
    },
    {
      name: 'Michael Chen',
      email: 'mike@enterprise.com',
      company_name: 'BigCorp',
      description: 'Executive level contact, keep it brief and business-focused'
    }
  ]
};
```

#### 🎯 How It Works

```javascript
class PersonalizationEngine {
  async processEmailCampaign(campaignData) {
    const results = [];
    
    // 1. Detect description column
    if (excelData.hasColumn('description')) {
      console.log('✨ Description-based personalization enabled');
      
      for (const contact of excelData.contacts) {
        if (contact.description && contact.description.trim()) {
          // 2. AI-powered customization
          const personalizedEmail = await this.customizeWithAI({
            baseTemplate: campaignData.template,
            baseSubject: campaignData.subject,
            contactInfo: contact,
            description: contact.description
          });
          
          results.push({
            email: contact.email,
            customized: true,
            content: personalizedEmail
          });
          
        } else {
          // 3. Fallback to standard template
          results.push({
            email: contact.email,
            customized: false,
            content: this.applyStandardTemplate(campaignData.template, contact)
          });
        }
      }
    }
    
    return results;
  }
}
```

#### 🚀 Frontend Implementation

```javascript
class PersonalizedCampaignManager {
  constructor() {
    this.baseUrl = 'http://localhost:8001';
  }

  // Create campaign with description-based personalization
  async createPersonalizedCampaign(campaignData) {
    const response = await fetch(`${this.baseUrl}/agents/mailerpanda/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: campaignData.userId,
        user_input: campaignData.description,
        mode: "interactive",
        consent_tokens: {
          ...campaignData.consentTokens,
          // ✨ Required for AI personalization
          "content_generation": "HCT:ai_personalization_token"
        },
        
        // Dynamic API keys for AI processing
        google_api_key: campaignData.googleApiKey,
        mailjet_api_key: campaignData.mailjetApiKey,
        mailjet_api_secret: campaignData.mailjetSecret,
        
        // Personalization settings
        enable_description_personalization: true,
        excel_file_path: "email_list_with_descriptions.xlsx"
      })
    });
    
    const result = await response.json();
    
    // Handle personalization results
    if (result.campaign_summary) {
      const { total_sent, personalized_count, standard_count } = result.campaign_summary;
      
      console.log(`📊 Campaign Results:`);
      console.log(`   Total Sent: ${total_sent}`);
      console.log(`   ✨ Personalized: ${personalized_count}`);
      console.log(`   📝 Standard: ${standard_count}`);
    }
    
    return result;
  }

  // Upload Excel file with descriptions
  async uploadPersonalizedContacts(file) {
    const formData = new FormData();
    formData.append('excel_file', file);
    formData.append('enable_personalization', 'true');
    
    const response = await fetch(`${this.baseUrl}/agents/mailerpanda/upload-contacts`, {
      method: 'POST',
      body: formData
    });
    
    const result = await response.json();
    
    if (result.description_column_detected) {
      console.log('✨ Description column detected - personalization enabled');
      console.log(`📊 ${result.contacts_with_descriptions} contacts have descriptions`);
    }
    
    return result;
  }

  // Preview personalization for a contact
  async previewPersonalization(baseTemplate, contactInfo, description) {
    const response = await fetch(`${this.baseUrl}/agents/mailerpanda/preview-personalization`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        base_template: baseTemplate,
        contact_info: contactInfo,
        description: description
      })
    });
    
    return await response.json();
  }
}

// Usage Example
const campaignManager = new PersonalizedCampaignManager();

// Create personalized campaign
const campaign = await campaignManager.createPersonalizedCampaign({
  userId: "user_123",
  description: "Create a product announcement email highlighting our new AI features",
  consentTokens: {
    "vault.read.email": "HCT:read_token",
    "vault.write.email": "HCT:write_token",
    "content_generation": "HCT:ai_token"
  },
  googleApiKey: userGoogleApiKey,
  mailjetApiKey: userMailjetApiKey,
  mailjetSecret: userMailjetSecret
});
```

#### 📋 Personalization Benefits

```javascript
const personalizationBenefits = {
  engagement: {
    "Higher open rates": "Personalized subject lines increase opens by 26%",
    "Better click-through": "Relevant content improves CTR by 14%",
    "Reduced unsubscribes": "Targeted messaging reduces opt-outs by 18%"
  },
  
  efficiency: {
    "Automated customization": "No manual email writing required",
    "Bulk personalization": "Process hundreds of contacts simultaneously", 
    "Consistent quality": "AI ensures professional tone across all emails"
  },
  
  flexibility: {
    "Works with existing data": "Enhances current Excel workflow",
    "Optional feature": "Graceful fallback to standard templates",
    "Maintains placeholders": "Compatible with existing template system"
  },
  
  compliance: {
    "Consent validation": "Full HushMCP privacy compliance",
    "Secure processing": "Encrypted AI operations",
    "Audit trail": "Complete tracking of personalization activities"
  }
};
```

## All Available Agents

### 🤖 Complete Agent Roster (4 Agents)

| Agent | ID | Primary Function | Key Features |
|-------|-----|------------------|--------------|
| **MailerPanda** | `agent_mailerpanda` | Email Campaign Management | AI drafting, Mass email, Excel integration, Approval workflow |
| **AddToCalendar** | `agent_addtocalendar` | Calendar Event Management | Event creation, Scheduling, Calendar integration |
| **ChanduFinance** | `agent_chandufinance` | Financial Data Processing | Financial analysis, Data processing |
| **RelationshipMemory** | `agent_relationshipmemory` | Relationship Management | Memory storage, Relationship tracking, Interactive chat |

## API Endpoints Reference

### 🎯 Core API Structure

```javascript
const API_BASE = "http://localhost:8001";

// Main agent execution endpoints
const ENDPOINTS = {
  // MailerPanda Agent
  mailerpanda: `${API_BASE}/agents/mailerpanda/execute`,
  
  // AddToCalendar Agent  
  addtocalendar: `${API_BASE}/agents/addtocalendar/execute`,
  
  // ChanduFinance Agent
  chandufinance: `${API_BASE}/agents/chandufinance/execute`,
  
  // RelationshipMemory Agent
  relationshipMemory: `${API_BASE}/agents/relationshipmemory/execute`,
  relationshipChat: `${API_BASE}/agents/relationshipmemory/chat`,
  
  // Research Agent (from frontend)
  researchSearch: `${API_BASE}/research/search`,
  researchChat: `${API_BASE}/research/chat`,
  researchPaperContent: `${API_BASE}/research/paper/{paper_id}/content`,
  
  // Utility endpoints
  health: `${API_BASE}/health`,
  docs: `${API_BASE}/docs`,
  consent: `${API_BASE}/consent/validate`
};
```

### 📋 Request/Response Models

#### MailerPanda Request
```typescript
interface MailerPandaRequest {
  // Required
  user_id: string;
  user_input: string;      // Natural language campaign description
  mode: "interactive" | "demo" | "headless";
  consent_tokens: Record<string, string>;
  
  // Optional - Dynamic API Keys (Secure!)
  google_api_key?: string;
  mailjet_api_key?: string;
  mailjet_api_secret?: string;
  
  // Campaign Configuration
  sender_email?: string;
  recipient_emails?: string[];
  require_approval?: boolean;
  use_ai_generation?: boolean;
  excel_file_path?: string;    // For mass emails
  
  // Advanced Options
  template_variables?: Record<string, string>;
  email_template?: string;     // Pre-written template
  subject_line?: string;       // Pre-written subject
}
```

#### Universal Agent Response
```typescript
interface AgentResponse {
  status: "success" | "error" | "pending" | "requires_approval";
  agent_id: string;
  user_id: string;
  execution_time: number;
  
  // Results
  result?: any;
  data?: any;
  
  // MailerPanda Specific
  campaign_id?: string;
  emails_sent?: number;
  send_status?: Array<{
    email: string;
    status: "sent" | "failed" | "pending";
    timestamp: string;
  }>;
  
  // Human-in-the-loop
  requires_approval?: boolean;
  approval_url?: string;
  feedback_prompt?: string;
  
  // Security & Privacy
  consent_validated?: boolean;
  vault_storage_key?: string;
  trust_links?: string[];
  
  // Error handling
  error?: string;
  error_code?: string;
  suggestions?: string[];
}
```

## Frontend Integration Examples

### 🎨 Complete MailerPanda Integration

```javascript
class MailerPandaManager {
  constructor() {
    this.baseUrl = 'http://localhost:8001';
    this.currentCampaign = null;
  }

  // 1. Create Interactive Email Campaign
  async createInteractiveCampaign(campaignData) {
    const response = await fetch(`${this.baseUrl}/agents/mailerpanda/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: campaignData.userId,
        user_input: campaignData.description,
        mode: "interactive",
        consent_tokens: campaignData.consentTokens,
        google_api_key: campaignData.googleApiKey,    // User's API key
        mailjet_api_key: campaignData.mailjetApiKey,  // User's API key
        mailjet_api_secret: campaignData.mailjetSecret,
        require_approval: true,
        use_ai_generation: true
      })
    });
    
    const result = await response.json();
    this.currentCampaign = result;
    
    // Handle human-in-the-loop approval
    if (result.requires_approval) {
      await this.handleApprovalWorkflow(result);
    }
    
    return result;
  }

  // 2. Mass Email Campaign with Excel
  async createMassEmailCampaign(excelFile, campaignConfig) {
    // First upload Excel file (if needed)
    const formData = new FormData();
    formData.append('file', excelFile);
    formData.append('campaign_config', JSON.stringify(campaignConfig));
    
    const response = await fetch(`${this.baseUrl}/agents/mailerpanda/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ...campaignConfig,
        mode: "interactive",
        mass_email: true,
        excel_file_path: excelFile.name
      })
    });
    
    return await response.json();
  }

  // 3. Demo Mode (Safe Testing)
  async runDemoMode(testConfig) {
    const response = await fetch(`${this.baseUrl}/agents/mailerpanda/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ...testConfig,
        mode: "demo"
      })
    });
    
    return await response.json();
  }

  // 4. Headless Mode (Automated)
  async runHeadlessMode(automationConfig) {
    const response = await fetch(`${this.baseUrl}/agents/mailerpanda/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ...automationConfig,
        mode: "headless"
      })
    });
    
    return await response.json();
  }

  // 5. Campaign Status Tracking
  async getCampaignStatus(campaignId) {
    const response = await fetch(`${this.baseUrl}/campaigns/${campaignId}/status`);
    return await response.json();
  }

  // 6. Human Approval Workflow Handler
  async handleApprovalWorkflow(campaignResult) {
    if (!campaignResult.requires_approval) return campaignResult;
    
    // Display approval UI
    const approved = await this.showApprovalDialog(campaignResult);
    
    if (approved) {
      // Send approval
      const response = await fetch(`${this.baseUrl}/campaigns/${campaignResult.campaign_id}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approved: true })
      });
      return await response.json();
    }
    
    return { status: "cancelled" };
  }

  // 7. Real-time Status Updates
  async subscribeToUpdates(campaignId, callback) {
    const eventSource = new EventSource(`${this.baseUrl}/campaigns/${campaignId}/updates`);
    
    eventSource.onmessage = (event) => {
      const update = JSON.parse(event.data);
      callback(update);
    };
    
    return eventSource;
  }
}

// Usage Example
const mailerManager = new MailerPandaManager();

// Create a complete email campaign
const campaign = await mailerManager.createInteractiveCampaign({
  userId: "user_123",
  description: "Create a welcome email for new subscribers with a 20% discount offer",
  consentTokens: {
    "vault.read.email": "HCT:user_read_token",
    "vault.write.email": "HCT:user_write_token"
  },
  googleApiKey: userGoogleApiKey,
  mailjetApiKey: userMailjetApiKey,
  mailjetSecret: userMailjetSecret
});
```

### 🔄 Multi-Agent Workflow Example

```javascript
class MultiAgentWorkflow {
  constructor() {
    this.baseUrl = 'http://localhost:8001';
  }

  // Complete workflow: Email + Calendar + Research
  async executeCompleteWorkflow(workflowData) {
    const results = {};
    
    // 1. Create email campaign with MailerPanda
    results.emailCampaign = await fetch(`${this.baseUrl}/agents/mailerpanda/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: workflowData.userId,
        user_input: workflowData.emailDescription,
        mode: "interactive",
        consent_tokens: workflowData.consentTokens
      })
    }).then(r => r.json());
    
    // 2. Create calendar event with AddToCalendar
    if (workflowData.includeCalendarEvent) {
      results.calendarEvent = await fetch(`${this.baseUrl}/agents/addtocalendar/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: workflowData.userId,
          user_input: workflowData.eventDescription,
          consent_tokens: workflowData.consentTokens
        })
      }).then(r => r.json());
    }
    
    // 3. Interactive chat with RelationshipMemory
    if (workflowData.includeRelationshipTracking) {
      results.relationshipChat = await fetch(`${this.baseUrl}/agents/relationshipmemory/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: workflowData.userId,
          message: workflowData.relationshipQuery,
          session_id: workflowData.sessionId
        })
      }).then(r => r.json());
    }
    
    // 4. Research papers (if needed)
    if (workflowData.researchQuery) {
      results.research = await fetch(`${this.baseUrl}/research/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: workflowData.researchQuery,
          user_id: workflowData.userId
        })
      }).then(r => r.json());
    }
    
    return results;
  }
}
```

### 🎯 Research Agent Integration

```javascript
class ResearchManager {
  constructor() {
    this.baseUrl = 'http://localhost:8001';
    this.selectedPaper = null;
  }

  // 1. Search for papers
  async searchPapers(query, userId = 'demo_user') {
    const response = await fetch(`${this.baseUrl}/research/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, user_id: userId })
    });
    
    const data = await response.json();
    return data.papers || [];
  }

  // 2. Get paper content
  async getPaperContent(paperId) {
    const encodedId = encodeURIComponent(paperId);
    const response = await fetch(`${this.baseUrl}/research/paper/${encodedId}/content`);
    return await response.json();
  }

  // 3. Chat with AI about paper
  async chatAboutPaper(message, paperId, userId = 'demo_user', conversationHistory = []) {
    const response = await fetch(`${this.baseUrl}/research/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        paper_id: paperId,
        user_id: userId,
        conversation_history: conversationHistory,
        paper_content: await this.getPaperContent(paperId)
      })
    });
    
    return await response.json();
  }

  // 4. Complete research workflow
  async performResearchWorkflow(query) {
    // Search for papers
    const papers = await this.searchPapers(query);
    
    if (papers.length === 0) {
      throw new Error('No papers found for query');
    }
    
    // Select first paper
    this.selectedPaper = papers[0];
    
    // Get full content
    const content = await this.getPaperContent(this.selectedPaper.id);
    
    // Generate analysis
    const analysis = await this.chatAboutPaper(
      "Please provide a comprehensive analysis of this paper",
      this.selectedPaper.id
    );
    
    return {
      papers,
      selectedPaper: this.selectedPaper,
      content,
      analysis
    };
  }
}
```

## Authentication & Security

### 🔒 Consent Token Management

```javascript
class ConsentManager {
  constructor() {
    this.tokens = new Map();
  }

  // Generate consent tokens for different scopes
  generateTokens(userId, scopes) {
    const tokens = {};
    
    scopes.forEach(scope => {
      tokens[scope] = `HCT:${userId}_${scope}_${Date.now()}`;
    });
    
    return tokens;
  }

  // Validate consent for operation
  async validateConsent(tokens, operation) {
    const response = await fetch('http://localhost:8001/consent/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        consent_tokens: tokens,
        operation: operation
      })
    });
    
    return await response.json();
  }

  // Required scopes for MailerPanda operations
  getMailerPandaScopes() {
    return {
      content_generation: ['vault.read.email', 'custom.temporary'],
      email_sending: ['vault.read.email', 'vault.write.email', 'custom.temporary'],
      contact_management: ['vault.read.file', 'vault.write.file'],
      campaign_storage: ['vault.write.email', 'vault.write.file']
    };
  }
}
```

## Error Handling

### ⚠️ Comprehensive Error Handling

```javascript
class ErrorHandler {
  static async handleApiCall(apiCall) {
    try {
      const response = await apiCall();
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Check for application-level errors
      if (data.status === 'error') {
        throw new Error(data.error || 'Unknown application error');
      }
      
      return data;
      
    } catch (error) {
      // Handle different error types
      if (error.name === 'TypeError') {
        console.error('Network error:', error.message);
        return { status: 'error', error: 'Network connection failed' };
      }
      
      if (error.message.includes('403') || error.message.includes('401')) {
        console.error('Authentication error:', error.message);
        return { status: 'error', error: 'Invalid or missing consent tokens' };
      }
      
      if (error.message.includes('429')) {
        console.error('Rate limit error:', error.message);
        return { status: 'error', error: 'Too many requests, please try again later' };
      }
      
      console.error('Unexpected error:', error);
      return { status: 'error', error: error.message };
    }
  }

  // Specific error handlers for each agent
  static handleMailerPandaErrors(error) {
    const errorMappings = {
      'Missing valid consent token': 'Please provide valid email consent tokens',
      'Email validation failed': 'One or more email addresses are invalid',
      'Campaign execution failed': 'Email campaign could not be completed',
      'Permission denied': 'Insufficient permissions for this operation'
    };
    
    return errorMappings[error] || error;
  }
}

// Usage
const result = await ErrorHandler.handleApiCall(async () => {
  return fetch('http://localhost:8001/agents/mailerpanda/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestData)
  });
});
```

## Best Practices

### 🏆 Frontend Integration Best Practices

1. **Always Use HTTPS in Production**
```javascript
const API_BASE = process.env.NODE_ENV === 'production' 
  ? 'https://your-api-domain.com' 
  : 'http://localhost:8001';
```

2. **Implement Proper Loading States**
```javascript
class LoadingManager {
  constructor() {
    this.loadingStates = new Map();
  }

  setLoading(operation, isLoading) {
    this.loadingStates.set(operation, isLoading);
    this.updateUI(operation, isLoading);
  }

  updateUI(operation, isLoading) {
    const button = document.getElementById(`${operation}-button`);
    const spinner = document.getElementById(`${operation}-spinner`);
    
    if (button) button.disabled = isLoading;
    if (spinner) spinner.style.display = isLoading ? 'block' : 'none';
  }
}
```

3. **Cache API Responses Appropriately**
```javascript
class ApiCache {
  constructor(ttl = 5 * 60 * 1000) { // 5 minutes
    this.cache = new Map();
    this.ttl = ttl;
  }

  set(key, value) {
    this.cache.set(key, {
      value,
      timestamp: Date.now()
    });
  }

  get(key) {
    const cached = this.cache.get(key);
    if (!cached) return null;
    
    if (Date.now() - cached.timestamp > this.ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return cached.value;
  }
}
```

4. **Implement Retry Logic**
```javascript
async function retryApiCall(apiCall, maxRetries = 3, delay = 1000) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await apiCall();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, delay * (i + 1)));
    }
  }
}
```

5. **Secure API Key Handling**
```javascript
class SecureApiKeyManager {
  constructor() {
    this.encryptedKeys = new Map();
  }

  storeApiKey(service, key) {
    // In production, use proper encryption
    const encrypted = btoa(key); // Basic encoding for demo
    sessionStorage.setItem(`api_key_${service}`, encrypted);
  }

  getApiKey(service) {
    const encrypted = sessionStorage.getItem(`api_key_${service}`);
    return encrypted ? atob(encrypted) : null;
  }

  clearApiKeys() {
    Object.keys(sessionStorage).forEach(key => {
      if (key.startsWith('api_key_')) {
        sessionStorage.removeItem(key);
      }
    });
  }
}
```

## 🎉 Complete Usage Example

```javascript
// Complete application integrating all functionalities
class HushMCPApp {
  constructor() {
    this.mailerManager = new MailerPandaManager();
    this.researchManager = new ResearchManager();
    this.consentManager = new ConsentManager();
    this.errorHandler = new ErrorHandler();
  }

  async initialize() {
    // Check backend health
    const health = await fetch('http://localhost:8001/health');
    if (!health.ok) {
      throw new Error('Backend server is not running');
    }
    
    console.log('✅ HushMCP Backend connected successfully');
  }

  async runCompleteWorkflow(userInput) {
    try {
      // 1. Generate consent tokens
      const tokens = this.consentManager.generateTokens('user_123', [
        'vault.read.email', 'vault.write.email', 'custom.temporary'
      ]);

      // 2. Create email campaign
      const campaign = await this.mailerManager.createInteractiveCampaign({
        userId: 'user_123',
        description: userInput.emailDescription,
        consentTokens: tokens,
        googleApiKey: userInput.googleApiKey,
        mailjetApiKey: userInput.mailjetApiKey,
        mailjetSecret: userInput.mailjetSecret
      });

      // 3. Research related papers (if needed)
      let research = null;
      if (userInput.researchQuery) {
        research = await this.researchManager.performResearchWorkflow(
          userInput.researchQuery
        );
      }

      // 4. Return comprehensive results
      return {
        status: 'success',
        campaign,
        research,
        timestamp: new Date().toISOString()
      };

    } catch (error) {
      return this.errorHandler.handleApiCall(() => {
        throw error;
      });
    }
  }
}

// Initialize and use the app
const app = new HushMCPApp();
await app.initialize();

const result = await app.runCompleteWorkflow({
  emailDescription: "Create a product launch email with technical details",
  researchQuery: "machine learning product launch strategies",
  googleApiKey: "your-google-api-key",
  mailjetApiKey: "your-mailjet-api-key", 
  mailjetSecret: "your-mailjet-secret"
});

console.log('Workflow completed:', result);
```

---

## 📞 Support & Documentation

- **Backend API Documentation:** `http://localhost:8001/docs`
- **Health Check:** `http://localhost:8001/health`
- **All Agents Available:** MailerPanda, AddToCalendar, ChanduFinance, RelationshipMemory
- **MailerPanda Features:** 12 comprehensive functionalities for complete email campaign management

This guide covers all aspects of integrating with the HushMCP backend API, providing complete access to all agent functionalities through clean, secure frontend code.
