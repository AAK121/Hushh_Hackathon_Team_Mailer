# 🚀 HushMCP Agent API Documentation

**Version:** 2.0.0  
**Framework:** FastAPI + HushMCP  
**Supported Agents:** AddToCalendar, MailerPanda, ChanduFinance, Relationship Memory  

> 🛡️ Privacy-first AI agent orchestration platform with comprehensive consent management and human-in-the-loop workflows.

---

## 📋 Table of Contents

- [🌟 Overview](#-overview)
- [🏗️ Architecture](#️-architecture)
- [🚀 Quick Start](#-quick-start)
- [🔑 Authentication & Consent](#-authentication--consent)
- [📅 AddToCalendar Agent API](#-addtocalendar-agent-api)
- [📧 MailerPanda Agent API](#-mailerpanda-agent-api)
- [💰 ChanduFinance Agent API](#-chandufinance-agent-api)
- [📊 Response Formats](#-response-formats)
- [❌ Error Handling](#-error-handling)
- [🔧 Testing](#-testing)

---

## 💰 ChanduFinance Agent API

### Agent Overview

The ChanduFinance agent is an AI-powered personal financial advisor that provides personalized investment advice, portfolio analysis, and financial education based on your unique financial profile.

### Input Requirements

```bash
GET /agents/chandufinance/status
```

**Required Inputs:**
- `user_id`: User identifier
- `token`: HushhMCP consent token with appropriate scopes
- `command`: Command to execute

**Required Scopes:**
- `vault.read.file`: Read user financial data
- `vault.write.file`: Save financial profiles and goals
- `vault.read.finance`: Access financial analysis data
- `agent.finance.analyze`: Perform financial analysis

### Execute ChanduFinance Agent

```bash
POST /agents/chandufinance/execute
Content-Type: application/json

{
    "user_id": "user_123",
    "token": "HCT:finance_consent_token...",
    "command": "setup_profile",
    "full_name": "John Smith",
    "age": 28,
    "occupation": "Software Engineer",
    "monthly_income": 6000.0,
    "monthly_expenses": 4000.0,
    "current_savings": 15000.0,
    "risk_tolerance": "moderate",
    "investment_experience": "beginner",
    "investment_budget": 1500.0
}
```

### Available Commands

| Command | Description | Use Case |
|---------|-------------|----------|
| `setup_profile` | Create comprehensive financial profile | Initial onboarding |
| `view_profile` | View complete financial profile | Profile overview |
| `update_income` | Update monthly income | Job change/promotion |
| `add_goal` | Add financial goals | Goal-based planning |
| `personal_stock_analysis` | Personalized stock analysis | Investment decisions |
| `investment_education` | Educational content | Learning |
| `behavioral_coaching` | Behavioral finance guidance | Bias management |
| `explain_like_im_new` | Beginner explanations | Education |

### Stock Analysis Example

```bash
POST /agents/chandufinance/execute
Content-Type: application/json

{
    "user_id": "user_123",
    "token": "HCT:finance_consent_token...",
    "command": "personal_stock_analysis",
    "ticker": "AAPL"
}
```

### Goal Management Example

```bash
POST /agents/chandufinance/execute
Content-Type: application/json

{
    "user_id": "user_123",
    "token": "HCT:finance_consent_token...",
    "command": "add_goal",
    "goal_name": "Emergency Fund",
    "target_amount": 20000.0,
    "target_date": "2026-12-31",
    "priority": "high"
}
```

### Response Format

```json
{
    "status": "success",
    "agent_id": "chandufinance",
    "user_id": "user_123",
    "command": "personal_stock_analysis",
    "message": "Analysis completed successfully",
    "profile_summary": {
        "monthly_income": "$6,000.00",
        "savings_rate": "33.3%",
        "risk_tolerance": "moderate"
    },
    "ticker": "AAPL",
    "current_price": 175.50,
    "personalized_analysis": "Based on your moderate risk tolerance and $1,500 monthly investment budget, AAPL represents a solid choice for your portfolio. Consider allocating $450 (30% of monthly budget) as a conservative position...",
    "next_steps": [
        "Start with $150/month DCA for 3 months",
        "Learn about Apple's business model",
        "Consider VTI for broader diversification"
    ],
    "vault_stored": true,
    "processing_time": 2.3
}
```

### Educational Content Example

```bash
POST /agents/chandufinance/execute
Content-Type: application/json

{
    "user_id": "user_123",
    "token": "HCT:finance_consent_token...",
    "command": "explain_like_im_new",
    "topic": "compound_interest",
    "complexity": "beginner"
}
```

Response:
```json
{
    "status": "success",
    "agent_id": "chandufinance",
    "user_id": "user_123",
    "command": "explain_like_im_new",
    "explanation": "Think of compound interest like a snowball rolling down a hill. At first, it's small, but as it rolls, it picks up more snow and gets bigger faster and faster...",
    "coaching_advice": "Start investing early, even small amounts. A 25-year-old investing $200/month will have more at retirement than a 35-year-old investing $400/month.",
    "next_steps": [
        "Open an investment account",
        "Start with index funds",
        "Automate your investments"
    ],
    "processing_time": 1.8
}
```

---

## �� Response Formats MailerPanda Agent API](#-mailerpanda-agent-api)
- [� ChanduFinance Agent API](#-chandufinance-agent-api)
- [🧠 Relationship Memory Agent API](#-relationship-memory-agent-api)
- [�🔄 Human-in-the-Loop Workflows](#-human-in-the-loop-workflows)
- [📊 Response Formats](#-response-formats)
- [🧪 Testing & Examples](#-testing--examples)
- [⚠️ Error Handling](#️-error-handling)

---

## 🌟 Overview

The HushMCP Agent API provides a unified REST interface for interacting with privacy-first AI agents. It supports multiple agents with different capabilities while maintaining strict consent validation and secure operations.

### ✨ Key Features

- **🤖 Multi-Agent Support**: AddToCalendar, MailerPanda, ChanduFinance, and Relationship Memory agents
- **🔒 Privacy-First Design**: Complete consent token validation
- **👥 Human-in-the-Loop**: Interactive approval workflows
- **📊 Real-time Status**: Session management and progress tracking
- **🛡️ Secure Operations**: HushMCP framework integration
- **📚 Interactive Docs**: Built-in Swagger UI documentation
- **🔄 CORS Support**: Frontend integration ready
- **💰 Financial Intelligence**: AI-powered personal financial advisor
- **🧠 Memory Management**: Persistent relationship and context memory

---

## 🏗️ Architecture

```
Frontend Application
        ↓
   API Gateway (FastAPI)
        ↓
┌─────────────────────────┐
│   Consent Management    │
│   - Token validation   │
│   - Scope enforcement  │
└─────────────────────────┘
        ↓
┌─────────────────────────┐
│    Agent Router         │
│   - AddToCalendar       │
│   - MailerPanda         │
└─────────────────────────┘
        ↓
┌─────────────────────────┐
│   Session Manager       │
│   - Human-in-loop       │
│   - Status tracking     │
└─────────────────────────┘
```

### Supported Agents

| Agent | ID | Version | Purpose |
|-------|----|---------|---------| 
| **AddToCalendar** | `agent_addtocalendar` | 1.1.0 | Email→Calendar event extraction |
| **MailerPanda** | `agent_mailerpanda` | 3.0.0 | AI-powered email campaigns |

---

## 🚀 Quick Start

### 1. Start the API Server

```bash
# Start the API server
python api.py

# API will be available at:
# Main API: http://127.0.0.1:8001
# Interactive Docs: http://127.0.0.1:8001/docs
# Alternative Docs: http://127.0.0.1:8001/redoc
```

### 2. Check API Health

```bash
curl http://127.0.0.1:8001/health
```

### 3. List Available Agents

```bash
curl http://127.0.0.1:8001/agents
```

---

## 🔑 Authentication & Consent

### Consent Token Creation

Before using any agent, you need to create consent tokens:

```bash
POST /consent/token
Content-Type: application/json

{
    "user_id": "user_123",
    "agent_id": "agent_addtocalendar",
    "scope": "vault.read.email"
}
```

**Response:**
```json
{
    "token": "HCT:dGVzdF91c2VyXzEyM...",
    "expires_at": 1755345158982,
    "scope": "vault.read.email"
}
```

### Required Scopes by Agent

#### AddToCalendar Agent
- `vault.read.email` - Read emails for event extraction
- `vault.write.calendar` - Create calendar events

#### MailerPanda Agent
- `vault.read.email` - Read email templates
- `vault.write.email` - Store email campaigns
- `vault.read.file` - Read contact files
- `vault.write.file` - Write status files
- `custom.temporary` - AI generation and sending

---

## 📅 AddToCalendar Agent API

### Agent Overview

The AddToCalendar agent processes emails to extract event information and creates Google Calendar events automatically.

### Input Requirements

```bash
GET /agents/addtocalendar/requirements
```

**Required Inputs:**
- `user_id`: User identifier
- `email_token`: Consent token for email access
- `calendar_token`: Consent token for calendar access
- `google_access_token`: Google OAuth access token
- `action`: Action to perform

### Execute AddToCalendar Agent

```bash
POST /agents/addtocalendar/execute
Content-Type: application/json

{
    "user_id": "user_123",
    "email_token": "HCT:email_consent_token...",
    "calendar_token": "HCT:calendar_consent_token...",
    "google_access_token": "ya29.google_oauth_token...",
    "action": "comprehensive_analysis",
    "confidence_threshold": 0.7,
    "max_emails": 50
}
```

### Available Actions

| Action | Description | Use Case |
|--------|-------------|----------|
| `comprehensive_analysis` | Full email processing + calendar creation | Main workflow |
| `manual_event` | Create specific calendar event | Manual event entry |
| `analyze_only` | Extract events without creating | Preview mode |

### Response Format

```json
{
    "status": "success",
    "user_id": "user_123",
    "action_performed": "comprehensive_analysis",
    "emails_processed": 25,
    "events_extracted": 8,
    "events_created": 6,
    "calendar_links": [
        "https://calendar.google.com/event?eid=abc123",
        "https://calendar.google.com/event?eid=def456"
    ],
    "extracted_events": [
        {
            "summary": "Team Meeting",
            "start_time": "2025-01-20T14:00:00",
            "end_time": "2025-01-20T15:00:00",
            "confidence": 0.9
        }
    ],
    "processing_time": 12.5,
    "trust_links": ["trust_link_123"],
    "errors": []
}
```

### Google OAuth Setup

To use AddToCalendar agent, you need:

1. **Google Cloud Project** with Calendar API enabled
2. **OAuth 2.0 credentials** configured
3. **Access token** from frontend OAuth flow

Example OAuth flow:
```javascript
// Frontend JavaScript example
const auth = gapi.auth2.getAuthInstance();
const user = auth.currentUser.get();
const accessToken = user.getAuthResponse().access_token;

// Use this access_token in API calls
```

---

## 📧 MailerPanda Agent API

### Agent Overview

The MailerPanda agent creates AI-generated email campaigns with human-in-the-loop approval workflows and mass distribution capabilities.

### Input Requirements

```bash
GET /agents/mailerpanda/requirements
```

**Required Inputs:**
- `user_id`: User identifier
- `consent_tokens`: Dictionary of consent tokens
- `user_input`: Email campaign description
- `mode`: Execution mode

### Execute MailerPanda Agent

```bash
POST /agents/mailerpanda/execute
Content-Type: application/json

{
    "user_id": "user_123",
    "user_input": "Create a marketing email for our new product launch",
    "mode": "interactive",
    "consent_tokens": {
        "vault.read.email": "HCT:read_token...",
        "vault.write.email": "HCT:write_token...",
        "custom.temporary": "HCT:temp_token..."
    },
    "sender_email": "marketing@company.com",
    "recipient_emails": ["customer1@example.com", "customer2@example.com"],
    "require_approval": true,
    "use_ai_generation": true
}
```

### Execution Modes

| Mode | Description | Approval Required |
|------|-------------|------------------|
| `interactive` | Full human-in-the-loop workflow | Yes |
| `headless` | Automated execution | No |
| `demo` | Demo mode with mock operations | Optional |

### Response Format

#### Initial Response (Awaiting Approval)

```json
{
    "status": "awaiting_approval",
    "user_id": "user_123",
    "mode": "interactive",
    "campaign_id": "user_123_1754740358",
    "email_template": {
        "subject": "Introducing Our Revolutionary New Product!",
        "body": "Dear [Name],\n\nWe're excited to announce..."
    },
    "requires_approval": true,
    "approval_status": "pending",
    "feedback_required": true,
    "processing_time": 5.2
}
```

---

## 🔄 Human-in-the-Loop Workflows

### MailerPanda Approval Workflow

When a MailerPanda campaign requires approval, use the approval endpoint:

```bash
POST /agents/mailerpanda/approve
Content-Type: application/json

{
    "user_id": "user_123",
    "campaign_id": "user_123_1754740358",
    "action": "approve",
    "feedback": "Looks great!"
}
```

### Approval Actions

| Action | Description | Effect |
|--------|-------------|--------|
| `approve` | Approve and send campaign | Proceeds with email sending |
| `reject` | Reject campaign | Cancels the campaign |
| `modify` | Request modifications | Allows feedback for changes |
| `regenerate` | Regenerate content | Creates new AI content |

### Session Management

Check campaign status:
```bash
GET /agents/mailerpanda/session/{campaign_id}
```

Response:
```json
{
    "campaign_id": "user_123_1754740358",
    "status": "awaiting_approval",
    "start_time": "2025-01-19T23:45:58",
    "requires_approval": true
}
```

---

## � ChanduFinance Agent API

The **ChanduFinance Agent** is an AI-powered personal financial advisor that provides personalized investment advice, financial planning, and educational content based on your unique financial profile.

### Base URL
```
POST /agents/chandufinance/execute
GET  /agents/chandufinance/status
```

### Core Features
- **Profile Management**: Complete financial profile setup and management
- **Goal Planning**: Create and track financial goals with timelines
- **Investment Analysis**: AI-powered personalized stock analysis
- **Financial Education**: Beginner-friendly explanations and coaching
- **Risk Assessment**: Personalized risk tolerance evaluation

### Required Scopes
```
vault.read.file      - Read user profile data
vault.write.file     - Save profile and goal updates
vault.read.finance   - Access financial data
agent.finance.analyze - Perform financial analysis
```

### Available Commands

#### Profile Management
- `setup_profile` - Create comprehensive financial profile
- `view_profile` - Display current financial snapshot
- `update_income` - Update monthly income
- `set_budget` - Set detailed budget categories

#### Goal Management
- `add_goal` - Create financial goals with timelines
- `goal_progress_check` - Track progress toward goals

#### Investment Analysis
- `personal_stock_analysis` - AI-powered stock analysis
- `portfolio_review` - Comprehensive portfolio assessment

#### Education & Coaching
- `explain_like_im_new` - Beginner-friendly explanations
- `investment_education` - Structured learning modules
- `behavioral_coaching` - Overcome investment biases

### Example: Setup Financial Profile

**Request:**
```json
{
  "user_id": "user_123",
  "token": "HCT:valid_token_here",
  "command": "setup_profile",
  "monthly_income": 6000.0,
  "monthly_expenses": 4000.0,
  "age": 28,
  "current_savings": 15000.0,
  "risk_tolerance": "moderate",
  "investment_experience": "beginner"
}
```

**Response:**
```json
{
  "status": "success",
  "user_id": "user_123",
  "command": "setup_profile",
  "message": "Financial profile created successfully",
  "profile_summary": {
    "monthly_income": "$6,000.00",
    "monthly_expenses": "$4,000.00",
    "savings_rate": "33.3%",
    "investment_budget": "$1,500.00",
    "risk_tolerance": "moderate"
  },
  "welcome_message": "Congratulations on taking control of your finances! With a 33% savings rate, you're ahead of most people...",
  "next_steps": [
    "Set up investment goals",
    "Learn about compound interest",
    "Start your first investment analysis"
  ],
  "vault_stored": true,
  "processing_time": 0.8
}
```

### Example: Personalized Stock Analysis

**Request:**
```json
{
  "user_id": "user_123",
  "token": "HCT:valid_token_here",
  "command": "personal_stock_analysis",
  "ticker": "AAPL"
}
```

**Response:**
```json
{
  "status": "success",
  "user_id": "user_123",
  "command": "personal_stock_analysis",
  "ticker": "AAPL",
  "current_price": 175.50,
  "personalized_analysis": "Apple is an excellent choice for your moderate risk profile. As a beginner, you want quality companies with predictable growth...",
  "profile_health_score": {
    "risk_alignment": "excellent",
    "goal_alignment": "strong",
    "experience_match": "perfect"
  },
  "position_sizing": {
    "recommended_amount": 200.0,
    "percentage_of_budget": 13.3,
    "reasoning": "15% allocation allows for diversification while building core position"
  },
  "next_steps": [
    "Consider starting with $100-200 position",
    "Learn about Apple's business model",
    "Set up automatic monthly investments"
  ],
  "processing_time": 1.2
}
```

### Example: Investment Education

**Request:**
```json
{
  "user_id": "user_123",
  "token": "HCT:valid_token_here",
  "command": "explain_like_im_new",
  "topic": "compound_interest",
  "complexity": "beginner"
}
```

**Response:**
```json
{
  "status": "success",
  "user_id": "user_123",
  "command": "explain_like_im_new",
  "topic": "compound_interest",
  "explanation": "Think of compound interest like a snowball rolling down a hill. It starts small, but as it rolls, it picks up more snow and gets bigger and bigger...",
  "examples": [
    "If you invest $1,000 at 7% annually for 30 years, you'll have $7,612",
    "The key is time - starting early is more powerful than investing more later"
  ],
  "next_steps": [
    "Try the compound interest calculator",
    "Set up your first automatic investment",
    "Learn about dollar-cost averaging"
  ],
  "processing_time": 0.6
}
```

---

## 🧠 Relationship Memory Agent API

The **Relationship Memory Agent** maintains persistent context and memory for user interactions, relationships, and preferences across conversations.

### Base URL
```
POST /agents/relationship_memory/execute
GET  /agents/relationship_memory/status
```

### Core Features
- **Persistent Memory**: Remember user preferences and context
- **Relationship Tracking**: Maintain information about user relationships
- **Context Awareness**: Build on previous conversations
- **Reminder Management**: Set and track reminders

### Required Scopes
```
vault.read.contacts  - Read contact information
vault.write.contacts - Save relationship data
vault.read.memory    - Access stored memories
vault.write.memory   - Store new memories
vault.read.reminder  - Read reminders
vault.write.reminder - Create reminders
```

### Example: Natural Language Interaction

**Request:**
```json
{
  "user_id": "user_123",
  "token": "HCT:valid_token_here",
  "user_input": "Remember that John's birthday is next month and he likes coffee",
  "is_startup": false
}
```

**Response:**
```json
{
  "status": "success",
  "user_id": "user_123",
  "response": "I've noted that John's birthday is next month and that he likes coffee. I'll help you remember this for future gift ideas or planning.",
  "memory_stored": true,
  "relationships_updated": ["John"],
  "processing_time": 0.4
}
```

---

## �📊 Response Formats

### Standard Response Structure

All agent responses follow a consistent structure:

```json
{
    "status": "success|error|awaiting_approval|completed",
    "user_id": "user_identifier",
    "processing_time": 12.5,
    "errors": ["error1", "error2"],
    // Agent-specific fields
}
```

### Status Values

| Status | Description | Next Action |
|--------|-------------|-------------|
| `success` | Operation completed successfully | None |
| `completed` | Campaign completed | None |
| `awaiting_approval` | Requires human approval | Use approval endpoint |
| `error` | Operation failed | Check errors field |

### Error Response Format

```json
{
    "status": "error",
    "user_id": "user_123",
    "errors": [
        "Invalid consent token for scope vault.read.email",
        "Google access token expired"
    ],
    "processing_time": 1.2
}
```

---

## 🧪 Testing & Examples

### Complete AddToCalendar Workflow

```bash
# 1. Create consent tokens
curl -X POST http://127.0.0.1:8001/consent/token \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "agent_id": "agent_addtocalendar", 
    "scope": "vault.read.email"
  }'

# 2. Execute agent
curl -X POST http://127.0.0.1:8001/agents/addtocalendar/execute \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "email_token": "HCT:email_token...",
    "calendar_token": "HCT:calendar_token...",
    "google_access_token": "ya29.oauth_token...",
    "action": "comprehensive_analysis"
  }'
```

### Complete MailerPanda Workflow

```bash
# 1. Execute MailerPanda
curl -X POST http://127.0.0.1:8001/agents/mailerpanda/execute \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "user_input": "Create newsletter for product launch",
    "mode": "interactive",
    "consent_tokens": {
      "custom.temporary": "HCT:temp_token..."
    }
  }'

# 2. Approve campaign (if required)
curl -X POST http://127.0.0.1:8001/agents/mailerpanda/approve \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "campaign_id": "campaign_id_from_step1",
    "action": "approve"
  }'
```

---

## ⚠️ Error Handling

### Common Error Scenarios

#### 1. Invalid Consent Tokens
```json
{
    "status": "error",
    "errors": ["Invalid consent token for scope vault.read.email"]
}
```

#### 2. Expired Access Tokens
```json
{
    "status": "error", 
    "errors": ["Google access token expired or invalid"]
}
```

#### 3. Missing Required Parameters
```json
{
    "detail": "Field required: google_access_token"
}
```

#### 4. Agent Not Found
```json
{
    "detail": "Agent agent_unknown not found"
}
```

### Error Resolution Guide

| Error Type | Cause | Solution |
|------------|-------|----------|
| **Consent Token Invalid** | Token expired or wrong scope | Create new token with correct scope |
| **Google OAuth Failed** | Access token invalid | Refresh OAuth token in frontend |
| **Agent Not Available** | Agent not loaded | Check agent status endpoint |
| **Session Not Found** | Campaign ID invalid | Check active sessions |

---

## 🔧 Configuration

### Environment Variables

```bash
# Required for MailerPanda
GOOGLE_API_KEY=your_gemini_api_key
MAILJET_API_KEY=your_mailjet_api_key  
MAILJET_API_SECRET=your_mailjet_secret

# Required for AddToCalendar
GOOGLE_API_KEY=your_google_api_key
```

### API Server Settings

```python
# Default configuration in api.py
HOST = "127.0.0.1"
PORT = 8001
RELOAD = True  # Set to False in production
LOG_LEVEL = "info"
```

---

## 📈 Performance & Limits

### Processing Times

| Agent | Operation | Typical Time |
|-------|-----------|--------------|
| **AddToCalendar** | Email processing | 2-5 seconds |
| **AddToCalendar** | Event extraction | 1-3 seconds per email |
| **AddToCalendar** | Calendar creation | 500ms per event |
| **MailerPanda** | AI content generation | 3-8 seconds |
| **MailerPanda** | Email sending | 1-2 seconds per email |

### Rate Limits

- **Google Calendar API**: 1000 requests/100 seconds
- **Mailjet API**: Varies by plan
- **Consent Token Creation**: No limit
- **Agent Execution**: No artificial limits

---

## 🚀 Deployment

### Production Considerations

1. **Security**: Configure CORS appropriately
2. **SSL/TLS**: Use HTTPS in production
3. **Rate Limiting**: Implement request throttling
4. **Monitoring**: Add logging and metrics
5. **Error Tracking**: Integrate error reporting

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["python", "api.py"]
```

---

## 📞 Support

### Interactive Documentation

- **Swagger UI**: http://127.0.0.1:8001/docs
- **ReDoc**: http://127.0.0.1:8001/redoc

### API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/agents` | GET | List all agents |
| `/agents/{agent_id}/requirements` | GET | Agent requirements |
| `/consent/token` | POST | Create consent token |
| `/agents/addtocalendar/execute` | POST | Execute AddToCalendar |
| `/agents/mailerpanda/execute` | POST | Execute MailerPanda |
| `/agents/mailerpanda/approve` | POST | Approve MailerPanda campaign |

### Troubleshooting

For common issues, check:
1. Agent status endpoints
2. Consent token validity
3. Required environment variables
4. API documentation at `/docs`

---

## 📄 License

Part of HushhMCP framework - Privacy-first AI agent ecosystem.

**🎯 Build AI that respects trust. Build with consent. — Team Hushh** 🚀
