### 🛡️ Privacy Commitment
- **Data minimization** - We only collect what's necessary
- **User control** - You own and control your data
- **Transparency** - Open-source for full auditability
- **Security-first** - End-to-end encryption by default

---

## 🌟 Acknowledgments

### 👥 Core Team
- **Development Team** - Full-stack development and AI integration
- **Security Team** - Cryptographic protocol design and implementation
- **Design Team** - User experience and interface design
- **DevOps Team** - Infrastructure and deployment automation

### 🙏 Special Thanks
- **Hushh Labs** - Vision and platform foundation
- **IIT Bombay Analytics Club** - Hackathon organization and support
- **Open Source Community** - Libraries and frameworks that made this possible
- **Early Testers** - Feedback and bug reports during development

### 🔧 Built With
- **Backend**: FastAPI, Python 3.8+, Pydantic, LangGraph
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS
- **AI/ML**: Google Gemini 2.0, LangChain, NumPy
- **Security**: Cryptography library, HMAC-SHA256, AES-256-GCM
- **Infrastructure**: Docker, PostgreSQL, Redis, Nginx

---

## 🚀 Get Started Today

Ready to experience the future of privacy-first AI agents?

```bash
git clone https://github.com/AAK121/Hushh_Hackathon_Team_Mailer.git
cd Hushh_Hackathon_Team_Mailer
pip install -r requirements.txt
python api.py
```

**Join the revolution in trustworthy AI. Your data, your agents, your control.**

---

<div align="center">

### 🤫 **Let's build a better agentic internet together.**

[🌐 Website](https://hushh.ai) • [📧 Email](mailto:support@hushh.ai) • [💬 Discord](https://discord.gg/hushh) • [🐛 Issues](https://github.com/AAK121/Hushh_Hackathon_Team_Mailer/issues)

**Made with ❤️ for the future of AI privacy**

</div>er of modern AI with **cryptographically enforced consent**, creating a new paradigm for trustworthy personal AI assistants:

- 🧠 **Intelligent AI Agents** - Email marketing, finance, research, calendar management, and relationship memory
- 🔐 **Consent-Based Architecture** - Every action requires cryptographically signed user permission
- � **Real-time Chat Interfaces** - Natural language interaction with all agents
- 🗄️ **Encrypted Data Vault** - AES-256-GCM encryption for all personal data
- 🌐 **Modern Web Frontend** - React + TypeScript with real-time capabilities
- ⚡ **Production Ready** - FastAPI backend with comprehensive error handling

---

## 🤖 Featured AI Agents

### 📧 **MailerPanda Agent** - Smart Email Marketing
- **AI-Powered Content Generation** using Google Gemini 2.0
- **Intelligent Personalization** beyond simple name placeholders
- **Memory System** that learns your writing style over time
- **Human-in-the-Loop** approval workflow for all campaigns
- **Batch Email Processing** with Excel contact management

### 💰 **Finance Agent** - Personal Finance Assistant
- **Portfolio Analysis** with real-time market data
- **Investment Recommendations** based on risk profile
- **Financial Planning** with goal tracking
- **Market Research** integration with multiple data sources

{
    "user_id": "user_123",
    "campaign_id": "user_123_1754740358",
    "action": "approve",
    "feedback": "Looks great!"
}
```

### 💰 ChanduFinance Agent API

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

### 🧠 Relationship Memory Agent API

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

### 📊 Standard Response Format

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

### ⚠️ Error Handling

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

### 📈 Performance & Limits

| Agent | Operation | Typical Time |
|-------|-----------|--------------|
| **AddToCalendar** | Email processing | 2-5 seconds |
| **MailerPanda** | AI content generation | 3-8 seconds |
| **ChanduFinance** | Profile analysis | 1-3 seconds |
| **Relationship Memory** | Context storage | 0.4-1 seconds |

### 🔧 Environment Configuration

```bash
# Required Environment Variables
GOOGLE_API_KEY=your_gemini_api_key
MAILJET_API_KEY=your_mailjet_api_key  
MAILJET_API_SECRET=your_mailjet_secret
ENCRYPTION_KEY=your_32_byte_hex_key

```

### 📚 Interactive Documentation

- **Swagger UI**: http://127.0.0.1:8001/docs
- **ReDoc**: http://127.0.0.1:8001/redoc

### 🔗 Key API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/agents` | GET | List all agents |
| `/consent/token` | POST | Create consent token |
| `/agents/{agent}/execute` | POST | Execute agent |
| `/agents/mailerpanda/approve` | POST | Approve campaign |
| `/agents/{agent}/status` | GET | Agent status |

---

## 🧪 Testing

### Backend Tests
```bash
# Run all tests
pytest

# Run specific agent tests
pytest tests/test_mailerpanda.py
pytest tests/test_finance_agent.py

# Run with coverage
pytest --cov=hushh_mcp tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```






## 🔐 Security Best Practices

### For Developers
- **Never hardcode API keys** - Use environment variables
- **Validate all inputs** - Sanitize user data
- **Use consent tokens** - Never bypass permission checks
- **Encrypt sensitive data** - AES-256-GCM for storage
- **Log security events** - Audit trails for compliance

### For Users
- **Review permissions** - Understand what agents can access
- **Regular key rotation** - Update API keys periodically
- **Monitor activity** - Check agent actions in dashboard
- **Revoke unused tokens** - Clean up old permissions

---

## 📚 Documentation & Resources

### Internal Documentation
- `docs/agents.md` - Complete agent development guide
- `docs/consent.md` - Consent token lifecycle
- `docs/api.md` - Full API reference
- `docs/operons.md` - Reusable component library




## 💡 Roadmap & Future Vision

### 🎯 Immediate Goals
- [ ] **Real-time Collaboration** - Multi-user agent interactions
- [ ] **Mobile Applications** - iOS and Android native apps
- [ ] **Enterprise Integration** - SSO and team management features

### 🚀 Long-term Vision
- [ ] **Open Agent Marketplace** - Community-built agent ecosystem

---

### 🏅 What We Built
- **Complete Agent Ecosystem** - 5+ production-ready AI agents
- **Cryptographic Consent Protocol** - Industry-grade privacy protection
- **Modern Web Interface** - Intuitive user experience
- **Comprehensive Documentation** - Developer-friendly onboarding
- **Extensive Testing** - Production-ready codebase

---

## 🫱🏽‍🫲 Contributing

* Fork → Build → Pull Request
* Add a test for every feature
* Run `pytest` before submitting

---

## ⚖️ License

MIT — open to the world.

Let’s build a better agentic internet together.

```


# 🤫 Hushh AI Agent Ecosystem with MCP

A comprehensive **AI-powered personal data assistant platform** featuring intelligent agents with cryptographic consent management, real-time chat interfaces, and enterprise-grade security.

> 🔐 **Privacy-first AI agents** that work with your explicit consent, built on the HushhMCP (Micro Consent Protocol) foundation.

---

## 🚀 What Makes This Special?

This platform c## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### 🔧 Development Contributions
1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Add comprehensive tests** for new functionality
4. **Ensure all tests pass** (`pytest` for backend, `npm test` for frontend)
5. **Submit a pull request** with detailed description

### 🐛 Bug Reports
- Use GitHub Issues with the `bug` label
- Include reproduction steps and environment details
- Attach relevant logs and screenshots

### 💡 Feature Requests
- Use GitHub Issues with the `enhancement` label
- Describe the use case and expected behavior
- Consider privacy and security implications

### 📖 Documentation
- Help improve README, API docs, and tutorials
- Translate documentation to other languages
- Create video tutorials and examples

### 🧪 Testing
- Add test cases for edge conditions
- Improve test coverage
- Performance and security testing

---

## 🏢 Enterprise & Production Use

### 🚀 Deployment Options
- **Self-hosted** - Full control over your data and infrastructure
- **Cloud-managed** - Scalable deployment with managed services
- **Hybrid** - Sensitive data on-premises, compute in cloud
- **Edge computing** - Local processing for maximum privacy

### 🔒 Enterprise Security
- **SOC 2 Type II** compliance ready
- **GDPR, CCPA, HIPAA** compliance frameworks
- **Zero-trust architecture** with encrypted everything
- **Audit logging** for compliance and monitoring

### 📈 Scalability
- **Horizontal scaling** with load balancers
- **Microservices architecture** for independent scaling
- **Caching layers** for high-performance responses
- **Database clustering** for high availability

---

## 🛡️ Privacy Commitment
- **Data minimization** - We only collect what's necessary
- **User control** - You own and control your data
- **Transparency** - Open-source for full auditability
- **Security-first** - End-to-end encryption by default

---

## 🌟 Acknowledgments

### 👥 Core Team
- **Development Team** - Full-stack development and AI integration
- **Security Team** - Cryptographic protocol design and implementation
- **Design Team** - User experience and interface design
- **DevOps Team** - Infrastructure and deployment automation

### 🙏 Special Thanks
- **Hushh Labs** - Vision and platform foundation
- **IIT Bombay Analytics Club** - Hackathon organization and support
- **Open Source Community** - Libraries and frameworks that made this possible
- **Early Testers** - Feedback and bug reports during development

### 🔧 Built With
- **Backend**: FastAPI, Python 3.8+, Pydantic, LangGraph
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS
- **AI/ML**: Google Gemini 2.0, LangChain, NumPy
- **Security**: Cryptography library, HMAC-SHA256, AES-256-GCM
- **Infrastructure**: Docker, PostgreSQL, Redis, Nginx

---

## 🚀 Get Started Today

Ready to experience the future of privacy-first AI agents?

```bash
git clone https://github.com/AAK121/Hushh_Hackathon_Team_Mailer.git
cd Hushh_Hackathon_Team_Mailer
pip install -r requirements.txt
python api.py
```

**Join the revolution in trustworthy AI. Your data, your agents, your control.**

---

<div align="center">

### 🤫 **Let's build a better agentic internet together.**

[🌐 Website](https://hushh.ai) • [📧 Email](mailto:support@hushh.ai) • [💬 Discord](https://discord.gg/hushh) • [🐛 Issues](https://github.com/AAK121/Hushh_Hackathon_Team_Mailer/issues)

**Made with ❤️ for the future of AI privacy**

</div>
