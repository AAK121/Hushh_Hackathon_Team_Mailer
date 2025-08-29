
# Comprehensive API Documentation

Our API provides a unified REST interface for interacting with privacy-first AI agents, built on **FastAPI + HushMCP** framework.

**Framework:** FastAPI + HushMCP  
**Supported Agents:** AddToCalendar, MailerPanda, ChanduFinance, Relationship Memory

## ✨ Key API Features

- **🤖 Multi-Agent Support**: AddToCalendar, MailerPanda, ChanduFinance, and Relationship Memory agents
- **🔒 Privacy-First Design**: Complete consent token validation
- **👥 Human-in-the-Loop**: Interactive approval workflows
- **📊 Real-time Status**: Session management and progress tracking
- **🛡️ Secure Operations**: HushMCP framework integration
- **📚 Interactive Docs**: Built-in Swagger UI documentation
- **🔄 CORS Support**: Frontend integration ready

## 🏗️ API Architecture

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
│   - ChanduFinance       │
│   - Relationship Memory │
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│   Session Manager       │
│   - Human-in-loop       │
│   - Status tracking     │
└─────────────────────────┘
```

## 🚀 API Quick Start

```bash
# Start the API server
python api.py

# API will be available at:
# Main API: http://127.0.0.1:8001
# Interactive Docs: http://127.0.0.1:8001/docs
# Alternative Docs: http://127.0.0.1:8001/redoc
```

## 🔑 Authentication & Consent

Before using any agent, create consent tokens:

```http
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

## 📅 AddToCalendar Agent API

The AddToCalendar agent processes emails to extract event information and creates Google Calendar events automatically.

```http
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

**Response:**
```json
{
  "status": "success",
  "user_id": "user_123",
  "action_performed": "comprehensive_analysis",
  "emails_processed": 25,
  "events_extracted": 8,
  "events_created": 6,
  "calendar_links": [
    "https://calendar.google.com/event?eid=abc123"
  ],
  "processing_time": 12.5
}
```

## 📧 MailerPanda Agent API

The MailerPanda agent creates AI-generated email campaigns with human-in-the-loop approval workflows.

```http
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
  "require_approval": true,
  "use_ai_generation": true
}
```

**Approval Workflow:**
```http
POST /agents/mailerpanda/approve
Content-Type: application/json

{
  "user_id": "user_123",
  "campaign_id": "user_123_1754740358",
  "action": "approve",
  "feedback": "Looks great!"
}
```

## 💰 ChanduFinance Agent API

AI-powered personal financial advisor providing personalized investment advice and financial planning.

```http
POST /agents/chandufinance/execute
Content-Type: application/json

{
  "user_id": "user_123",
  "token": "HCT:finance_consent_token...",
  "command": "setup_profile",
  "monthly_income": 6000.0,
  "monthly_expenses": 4000.0,
  "current_savings": 15000.0,
  "risk_tolerance": "moderate",
  "investment_experience": "beginner"
}
```

**Available Commands:**
- `setup_profile` - Create comprehensive financial profile
- `personal_stock_analysis` - AI-powered stock analysis
- `add_goal` - Create financial goals with timelines
- `explain_like_im_new` - Beginner-friendly explanations
- `investment_education` - Structured learning modules

**Response:**
```json
{
  "status": "success",
  "command": "personal_stock_analysis",
  "ticker": "AAPL",
  "current_price": 175.50,
  "personalized_analysis": "Based on your moderate risk tolerance...",
  "position_sizing": {
    "recommended_amount": 200.0,
    "percentage_of_budget": 13.3
  },
  "next_steps": [
    "Start with $100-200 position",
    "Learn about Apple's business model"
  ]
}
```

## 🧠 Relationship Memory Agent API

Maintains persistent context and memory for user interactions and relationships.

```http
POST /agents/relationship_memory/execute
Content-Type: application/json

{
  "user_id": "user_123",
  "token": "HCT:valid_token_here",
  "user_input": "Remember that John's birthday is next month and he likes coffee"
}
```

**Response:**
```json
{
  "status": "success",
  "response": "I've noted that John's birthday is next month and that he likes coffee...",
  "memory_stored": true,
  "relationships_updated": ["John"],
  "processing_time": 0.4
}
```

## 📊 Standard Response Format

All agents follow consistent response structure:

```json
{
  "status": "success|error|awaiting_approval|completed",
  "user_id": "user_identifier",
  "processing_time": 12.5,
  "errors": ["error1", "error2"]
  // Agent-specific fields
}
```

## ⚠️ Error Handling

**Common Error Scenarios:**

```json
// Invalid Consent Token
{
  "status": "error",
  "errors": ["Invalid consent token for scope vault.read.email"]
}

// Expired Access Token
{
  "status": "error", 
  "errors": ["Google access token expired or invalid"]
}

// Missing Parameters
{
  "detail": "Field required: google_access_token"
}
```

## 📈 Performance & Limits

| Agent | Operation | Typical Time |
|-------|-----------|--------------|
| **AddToCalendar** | Email processing | 2-5 seconds |
| **MailerPanda** | AI content generation | 3-8 seconds |
| **ChanduFinance** | Profile analysis | 1-3 seconds |
| **Relationship Memory** | Context storage | 0.4-1 seconds |

## 🔧 Environment Configuration

```bash
# Required Environment Variables
GOOGLE_API_KEY=your_gemini_api_key
MAILJET_API_KEY=your_mailjet_api_key  
MAILJET_API_SECRET=your_mailjet_secret
ENCRYPTION_KEY=your_32_byte_hex_key
```

## 📚 Interactive Documentation

- **Swagger UI**: http://127.0.0.1:8001/docs
- **ReDoc**: http://127.0.0.1:8001/redoc

## 🔗 Key API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/agents` | GET | List all agents |
| `/consent/token` | POST | Create consent token |
| `/agents/{agent}/execute` | POST | Execute agent |
| `/agents/mailerpanda/approve` | POST | Approve campaign |
| `/agents/{agent}/status` | GET | Agent status |

### 4. Access the API

- **API Server**: http://127.0.0.1:8001
- **Interactive Docs**: http://127.0.0.1:8001/docs
- **ReDoc Documentation**: http://127.0.0.1:8001/redoc

## API Endpoints

### Health and Discovery

#### `GET /`
Basic health check and API information.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-08T22:30:00Z",
  "agents_available": 2,
  "version": "1.0.0"
}
```

#### `GET /agents`
List all available agents and their capabilities.

**Response:**
```json
[
  {
    "id": "addtocalendar",
    "name": "AddToCalendar Agent",
    "description": "Extracts events from emails and adds them to calendar",
    "version": "1.0.0",
    "required_scopes": ["VAULT_READ_EMAIL", "VAULT_WRITE_CALENDAR"],
    "status": "active"
  },
  {
    "id": "mailerpanda", 
    "name": "MailerPanda Agent",
    "description": "AI-powered mass email agent with human approval",
    "version": "1.0.0",
    "required_scopes": ["VAULT_WRITE_EMAIL"],
    "status": "active"
  }
]
```

#### `GET /agents/{agent_id}`
Get detailed information about a specific agent.

### Consent Management

#### `POST /consent/token`
Generate a consent token for agent operations.

**Request:**
```json
{
  "user_id": "user123",
  "scopes": ["VAULT_READ_EMAIL", "VAULT_WRITE_CALENDAR"],
  "duration_hours": 24
}
```

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "expires_at": "2025-08-09T22:30:00Z",
  "scopes": ["VAULT_READ_EMAIL", "VAULT_WRITE_CALENDAR"]
}
```

### Agent Execution

#### `POST /agents/{agent_id}/execute`
Execute an agent with specific parameters.

**Request:**
```json
{
  "user_id": "user123",
  "agent_id": "addtocalendar",
  "consent_tokens": {
    "email_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "calendar_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "parameters": {}
}
```

**Response:**
```json
{
  "status": "success",
  "agent_id": "addtocalendar",
  "timestamp": "2025-08-08T22:30:00Z",
  "data": {
    "status": "complete",
    "events_created": 2,
    "links": ["https://calendar.google.com/event?eid=..."]
  }
}
```

### Specific Agent Endpoints

#### `POST /agents/addtocalendar/process-emails`
Process emails and create calendar events.

**Parameters:**
- `user_id`: User identifier
- `email_token`: Consent token for email access
- `calendar_token`: Consent token for calendar write access

#### `POST /agents/mailerpanda/draft`
Generate AI-powered email content.

**Parameters:**
- `user_input`: Description of the email to generate
- `user_email`: Sender email address
- `consent_token`: Consent token for email operations
- `receiver_emails`: List of recipient emails (optional)
- `mass_email`: Whether this is a mass email campaign

## Agent Integration Guide

### Adding New Agents

The API automatically discovers agents from the `hushh_mcp/agents/` directory. To add a new agent:

1. **Create Agent Directory:**
   ```
   hushh_mcp/agents/your_agent/
   ├── index.py       # Main agent class
   ├── manifest.py    # Agent metadata
   └── requirements.txt
   ```

2. **Implement Agent Class:**
   ```python
   class YourAgent:
       def __init__(self):
           self.agent_id = manifest["id"]
       
       def handle(self, **kwargs):
           # Your agent logic here
           return {"status": "success", "data": result}
   ```

3. **Create Manifest:**
   ```python
   manifest = {
       "id": "your_agent",
       "name": "Your Agent",
       "description": "What your agent does",
       "version": "1.0.0",
       "required_scopes": ["VAULT_READ_SOMETHING"]
   }
   ```

4. **Restart API Server** - The agent will be automatically loaded.

### Agent Interface Requirements

Agents must implement:

- `__init__()`: Initialize with agent_id from manifest
- `handle(**kwargs)`: Main execution method
- Return dict with status and data/error fields

### Consent Token Usage

Agents should validate consent tokens before accessing user data:

```python
from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope

def handle(self, consent_token, **kwargs):
    is_valid, reason, _ = validate_token(
        consent_token, 
        expected_scope=ConsentScope.VAULT_READ_EMAIL
    )
    if not is_valid:
        raise PermissionError(f"Access denied: {reason}")
    
    # Proceed with operation
```

## Security Considerations

### Authentication
- All agent operations require valid consent tokens
- Tokens are cryptographically signed and time-bound
- Invalid tokens result in 401 Unauthorized responses

### Authorization  
- Agents validate specific scopes before data access
- Granular permissions (read email, write calendar, etc.)
- User consent is required for each scope

### Data Privacy
- No data stored in API server
- All processing happens in agents with user consent
- Complete audit trail for compliance

## Error Handling

### Standard Error Response
```json
{
  "status": "error",
  "error": "Description of what went wrong",
  "timestamp": "2025-08-08T22:30:00Z"
}
```

### Common Error Codes
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Invalid or missing consent token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Agent or resource not found
- `500 Internal Server Error`: Unexpected server error

## Performance and Scaling

### Async Processing
- All endpoints use async/await for non-blocking operations
- Background tasks for long-running agent operations
- Concurrent request handling

### Monitoring
- Health check endpoints for load balancer integration
- Agent status monitoring
- Request/response logging

### Production Deployment
```bash
# Using Gunicorn with multiple workers
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001

# Using Docker
docker build -t hushmcp-api .
docker run -p 8001:8001 hushmcp-api
```

## Examples

### JavaScript/Fetch
```javascript
// Generate consent token
const tokenResponse = await fetch('/consent/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 'user123',
    scopes: ['VAULT_READ_EMAIL', 'VAULT_WRITE_CALENDAR'],
    duration_hours: 24
  })
});
const { token } = await tokenResponse.json();

// Execute agent
const result = await fetch('/agents/addtocalendar/execute', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 'user123',
    agent_id: 'addtocalendar', 
    consent_tokens: {
      email_token: token,
      calendar_token: token
    },
    parameters: {}
  })
});
```

### Python/Requests
```python
import requests

# Generate consent token
response = requests.post('http://127.0.0.1:8001/consent/token', json={
    'user_id': 'user123',
    'scopes': ['VAULT_READ_EMAIL', 'VAULT_WRITE_CALENDAR'],
    'duration_hours': 24
})
token = response.json()['token']

# Execute agent
response = requests.post('http://127.0.0.1:8001/agents/addtocalendar/execute', json={
    'user_id': 'user123',
    'agent_id': 'addtocalendar',
    'consent_tokens': {
        'email_token': token,
        'calendar_token': token
    },
    'parameters': {}
})
result = response.json()
```

### cURL
```bash
# Generate consent token
curl -X POST http://127.0.0.1:8001/consent/token \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user123","scopes":["VAULT_READ_EMAIL"],"duration_hours":24}'

# Execute agent
curl -X POST http://127.0.0.1:8001/agents/addtocalendar/execute \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user123","agent_id":"addtocalendar","consent_tokens":{"email_token":"TOKEN","calendar_token":"TOKEN"},"parameters":{}}'
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Agent Not Found**: Check agent directory structure and manifest
3. **Consent Token Invalid**: Verify token generation and expiration
4. **Permission Denied**: Check required scopes in agent manifest

### Debug Mode
```bash
python api.py --reload --log-level debug
```

### Logs
Check console output for:
- Agent loading status
- Request/response details  
- Error messages and stack traces

---

For more information, visit the interactive API documentation at `/docs` when the server is running.
