# 📧 MailerPanda Agent

**Version:** 3.0.0  
**Agent ID:** `agent_mailerpanda`  
**Framework:** HushhMCP v1.0  

> 🐼 Advanced AI-powered mass mailer agent with complete privacy-first architecture, consent validation, and cross-agent communication capabilities.

---

## 🌟 Overview

MailerPanda is a sophisticated email campaign agent that leverages AI for content generation while maintaining strict privacy controls through the HushhMCP framework. It provides intelligent email composition, mass distribution, and cross-agent delegation capabilities.

### ✨ Key Features

- **🤖 AI Content Generation**: Gemini 2.0 Flash integration for intelligent email composition
- **🔒 Privacy-First Design**: Complete HushhMCP consent validation system
- **📊 LangGraph Workflows**: Modern state management with human-in-the-loop approval
- **🔗 Cross-Agent Communication**: Trust link delegation for seamless integration
- **📧 Mass Email Distribution**: Mailjet integration for reliable delivery
- **🛡️ Vault Integration**: Secure data storage with encryption
- **👥 Human Approval**: Interactive approval workflows for quality control

---

## 🏗️ Architecture

### Core Components

```
MailerPanda Agent
├── 🧠 AI Content Engine (Gemini 2.0)
├── 🔐 Consent Validation System
├── 📊 LangGraph Workflow Manager
├── 📧 Email Distribution Engine (Mailjet)
├── 🔗 Trust Link Manager
├── 🛡️ Vault Storage System
└── 👥 Human-in-the-Loop Interface
```

### HushhMCP Integration

- **Consent Scopes**: `VAULT_READ_EMAIL`, `VAULT_WRITE_EMAIL`, `VAULT_READ_FILE`, `VAULT_WRITE_FILE`, `CUSTOM_TEMPORARY`
- **Trust Links**: Full delegation workflow for cross-agent operations
- **Vault Storage**: Encrypted campaign data storage
- **Privacy Controls**: Operation-specific consent validation

---

## 🚀 Quick Start

### Prerequisites

```bash
# Required Environment Variables
GOOGLE_API_KEY=your_gemini_api_key
MAILJET_API_KEY=your_mailjet_api_key
MAILJET_API_SECRET=your_mailjet_secret
```

### Basic Usage

```python
from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
from hushh_mcp.consent.token import issue_token
from hushh_mcp.constants import ConsentScope

# Initialize agent
agent = MassMailerAgent()

# Create consent tokens
consent_tokens = {
    'content_generation': issue_token(
        user_id="user_123",
        agent_id="agent_mailerpanda", 
        scope=ConsentScope.CUSTOM_TEMPORARY
    ).token
}

# Create email campaign
state = {
    'user_input': 'Create a marketing email for our new product launch',
    'user_id': 'user_123',
    'consent_tokens': consent_tokens,
    'user_email': 'sender@example.com',
    'receiver_email': ['customer1@example.com', 'customer2@example.com']
}

# Execute workflow
result = agent.handle(state)
```

---

## 📋 Workflow Stages

### 1. 🔒 Consent Validation
- Validates user consent for each operation
- Enforces scope-based permissions
- Ensures privacy compliance

### 2. 🤖 AI Content Generation
- Uses Gemini 2.0 Flash for intelligent composition
- Context-aware email generation
- Maintains brand consistency

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
