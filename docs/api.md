# HushMCP Agent API Documentation

## Overview

The HushMCP Agent API provides a FastAPI-based REST interface for interacting with privacy-first AI agents. The API is designed to be scalable, secure, and easy to integrate with web applications.

## Features

- **Agent Registry**: Automatic discovery and registration of agents
- **Consent-Driven**: All operations require explicit user consent tokens  
- **Async Processing**: Non-blocking request handling for better performance
- **Type Safety**: Full Pydantic validation for requests and responses
- **Auto Documentation**: Interactive API docs with Swagger UI
- **CORS Support**: Ready for web application integration
- **Error Handling**: Comprehensive error responses with details

## Quick Start

### 1. Install Dependencies

```bash
pip install -r api_requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file with:

```env
OPENAI_API_KEY=your_openai_key
MAILJET_API_KEY=your_mailjet_key
MAILJET_API_SECRET=your_mailjet_secret  
GEMINI_API_KEY=your_gemini_key
API_HOST=127.0.0.1
API_PORT=8001
```

### 3. Start the Server

```bash
# Using the launcher script (recommended)
python start_api.py

# Or directly with uvicorn
python api.py --reload

# Or with custom settings
uvicorn api:app --host 0.0.0.0 --port 8001 --reload
```

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
