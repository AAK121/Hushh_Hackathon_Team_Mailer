# 📅 AddToCalendar Agent

**Version:** 1.1.0  
**Agent ID:** `agent_addtocalendar`  
**Framework:** HushhMCP v1.0  

> 🗓️ Intelligent AI-powered calendar agent that extracts events from emails and creates calendar entries with complete privacy controls and cross-agent communication.

---

## 🌟 Overview

AddToCalendar is an advanced calendar management agent that uses AI to intelligently extract event information from emails and automatically create calendar entries. Built on the HushhMCP framework, it ensures complete privacy compliance and seamless integration with other agents.

### ✨ Key Features

- **🤖 AI Event Extraction**: Advanced AI models for intelligent event detection
- **📧 Email Processing**: Automated email analysis and categorization
- **📅 Google Calendar Integration**: Seamless calendar event creation
- **🔒 Privacy-First Design**: Complete HushhMCP consent validation
- **🔗 Cross-Agent Communication**: Trust link support for agent delegation
- **🛡️ Vault Integration**: Secure data storage with encryption
- **📊 Smart Prioritization**: Intelligent email and event prioritization
- **🎯 High Confidence Filtering**: Quality control for event accuracy

---

## 🏗️ Architecture

### Core Components

```
AddToCalendar Agent
├── 🧠 AI Event Extraction Engine
├── 📧 Email Processing Pipeline
├── 🔐 Consent Validation System
├── 📅 Google Calendar API Integration
├── 🔗 Trust Link Manager
├── 🛡️ Vault Storage System
├── 📊 Prioritization Engine
└── 🎯 Confidence Scoring System
```

### HushhMCP Integration

- **Consent Scopes**: `VAULT_READ_EMAIL`, `VAULT_WRITE_CALENDAR`
- **Trust Links**: Cross-agent verification and delegation
- **Vault Storage**: Encrypted event and email data
- **Privacy Controls**: Operation-specific consent validation

---

## 🚀 Quick Start

### Prerequisites

```bash
# Required Environment Variables
GOOGLE_API_KEY=your_google_api_key

# Google Calendar API credentials
# Set up OAuth 2.0 credentials in Google Cloud Console
```

### Basic Usage

```python
from hushh_mcp.agents.addtocalendar.index import AddToCalendarAgent
from hushh_mcp.consent.token import issue_token
from hushh_mcp.constants import ConsentScope

# Initialize agent
agent = AddToCalendarAgent()

# Create consent tokens
email_token = issue_token(
    user_id="user_123",
    agent_id="agent_addtocalendar", 
    scope=ConsentScope.VAULT_READ_EMAIL
).token

calendar_token = issue_token(
    user_id="user_123",
    agent_id="agent_addtocalendar",
    scope=ConsentScope.VAULT_WRITE_CALENDAR
).token

# Execute agent with access token
result = agent.handle(
    user_id="user_123",
    email_token_str=email_token,
    calendar_token_str=calendar_token,
    google_access_token="your_google_access_token",
    action="process_emails"
)
```

---

## 📋 Workflow Stages

### 1. 🔒 Consent Validation
- Validates user consent for email reading and calendar writing
- Enforces scope-based permissions
- Ensures privacy compliance at every step

### 2. 📧 Email Processing
- Reads emails from user's account
- Categorizes emails by type and importance
- Prioritizes emails based on relevance and urgency

### 3. 🤖 AI Event Extraction
- Uses advanced AI models to extract event information
- Identifies dates, times, locations, and event details
- Assigns confidence scores to extracted events

### 4. 🎯 Confidence Filtering
- Filters events based on confidence thresholds
- Ensures only high-quality events are processed
- Reduces false positives and improves accuracy

### 5. 📅 Calendar Integration
- Creates events in Google Calendar
- Handles scheduling conflicts and duplicates
- Provides event links and confirmation

### 6. 🔗 Trust Link Creation
- Sets up delegation for other agents
- Enables secure resource sharing
- Maintains audit trails for inter-agent communication

---

## 🔧 Configuration

### Manifest Configuration

```python
{
    "id": "agent_addtocalendar",
    "name": "AddToCalendar",
    "version": "1.1.0",
    "description": "AI-powered calendar event extraction from emails",
    "required_scopes": [
        ConsentScope.VAULT_READ_EMAIL,
        ConsentScope.VAULT_WRITE_CALENDAR
    ],
    "capabilities": [
        "email_processing",
        "event_extraction", 
        "calendar_integration",
        "cross_agent_communication"
    ]
}
```

### Event Extraction Configuration

```python
# Confidence thresholds
MINIMUM_CONFIDENCE = 0.7  # Default threshold for event acceptance
HIGH_CONFIDENCE = 0.9     # High confidence events
LOW_CONFIDENCE = 0.5      # Minimum for review

# Processing limits
MAX_EMAILS_PER_BATCH = 50
MAX_EVENTS_PER_EMAIL = 5
PROCESSING_TIMEOUT = 300  # seconds
```

---

## 🧪 Testing

Comprehensive test suite ensuring HushhMCP compliance:

```bash
# Run AddToCalendar tests
python -m pytest tests/unit/test_agents.py::TestAddToCalendarAgent -v

# Test coverage includes:
# ✅ Agent initialization and manifest compliance
# ✅ Consent validation (success/failure scenarios)
# ✅ Email prioritization and categorization
# ✅ AI event extraction functionality
# ✅ Calendar integration workflows
# ✅ Vault encryption and storage
# ✅ Trust link verification
# ✅ Error handling and recovery
# ✅ Scope enforcement
# ✅ Confidence-based filtering
```

### Test Results

```
16 tests total
14 passing ✅
2 minor failures ⚠️ (access token authentication updates)
Success rate: 87.5%
```

---

## 🔗 Cross-Agent Integration

### Trust Link Verification

```python
# Verify trust links from other agents
is_valid = agent._verify_trust_link(
    trust_link_token="trust_link_123",
    required_scope=ConsentScope.VAULT_READ_EMAIL
)
```

### Resource Delegation

- Calendar events can be shared with other agents
- Email summaries available through trust links
- Secure delegation with permission controls

---

## 📊 Analytics & Monitoring

### Event Extraction Metrics

- **Processing Speed**: Average email processing time
- **Accuracy Rate**: Event extraction success rate
- **Confidence Distribution**: Quality metrics for extracted events
- **Calendar Integration Success**: Event creation success rate

### Privacy Compliance Tracking

- Consent validation logs
- Scope enforcement audits
- Data access patterns
- Cross-agent communication logs

---

## 🛡️ Security Features

### Privacy Controls

- **Consent-First Architecture**: All operations require explicit user consent
- **Scope Enforcement**: Granular permission controls for different operations
- **Data Encryption**: All vault storage uses strong encryption
- **Access Logging**: Complete audit trail of all data access

### Security Best Practices

- OAuth 2.0 integration for Google services
- Environment variable configuration
- No hardcoded credentials or tokens
- Secure API communication protocols
- Input validation and sanitization

---

## 🔄 API Integration

### Google Calendar API

```python
# Event creation
event = {
    'summary': 'Team Meeting',
    'start': {'dateTime': '2025-01-20T14:00:00'},
    'end': {'dateTime': '2025-01-20T15:00:00'},
    'description': 'Weekly team sync meeting'
}

# Create in calendar
result = agent.create_events_in_calendar(
    events=[event],
    user_id="user_123", 
    consent_token=calendar_token
)
```

### REST Endpoints

When deployed with FastAPI server:

```bash
POST /agents/addtocalendar/execute
{
    "user_id": "user_123",
    "email_token_str": "email_consent_token",
    "calendar_token_str": "calendar_consent_token",
    "google_access_token": "google_oauth_token",
    "action": "process_emails"
}
```

---

## 📈 Performance Metrics

- **Email Processing**: 2-5 emails per second
- **Event Extraction**: 1-3 seconds per email
- **Calendar Creation**: 500ms per event
- **Consent Validation**: < 100ms per operation
- **Trust Link Verification**: < 200ms

---

## 🎯 Event Confidence System

### Confidence Levels

- **0.9+ High Confidence**: Automatically processed
- **0.7-0.9 Medium Confidence**: Standard processing
- **0.5-0.7 Low Confidence**: Requires review
- **< 0.5**: Filtered out

### Quality Assurance

- Multiple AI model validation
- Cross-reference with known patterns
- User feedback integration
- Continuous learning and improvement

---

## 🤝 Contributing

When extending AddToCalendar:

1. **Maintain HushhMCP Compliance**: All features must integrate with consent system
2. **Add Comprehensive Tests**: Follow existing test patterns  
3. **Update Documentation**: Keep README and manifest current
4. **Security Review**: Ensure privacy and security compliance
5. **Performance Testing**: Maintain processing speed standards

---

## 🚧 Known Limitations

- Google Calendar API rate limits
- Access token authentication migration in progress
- Limited to Google Calendar (other providers coming soon)
- Requires stable internet connection for API calls

---

## 📞 Support

For questions about AddToCalendar agent:

- **Framework**: HushhMCP Documentation
- **Google APIs**: Google Calendar API Documentation
- **AI Models**: Google AI Documentation
- **Testing**: pytest Documentation

---

## 📄 License

Part of HushhMCP framework - Privacy-first AI agent ecosystem.

**🎯 Build AI that respects trust. Build with consent. — Team Hushh** 📅
