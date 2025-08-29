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

### 🧠 **Relationship Memory Agent** - Smart Contact Management
- **Proactive Relationship Management** with AI suggestions
- **Conversation History** analysis and insights
- **Smart Contact Organization** with relationship mapping
- **Follow-up Reminders** based on interaction patterns

### 📅 **Calendar Agent** - Intelligent Scheduling
- **Smart Meeting Scheduling** with conflict detection
- **Cross-platform Integration** (Google Calendar, Outlook)
- **Event Optimization** based on preferences and patterns
- **Automated Follow-ups** and reminders

### 🔍 **Research Agent** - Information Intelligence
- **Multi-source Research** across academic and web sources
- **Real-time Analysis** with citation tracking
- **Knowledge Synthesis** from multiple documents
- **Automated Report Generation** with proper formatting

---

## 🏗️ System Architecture

```
Hushh AI Agent Ecosystem/
├── 🌐 frontend/                    # React + TypeScript Web Interface
│   ├── src/components/             # Agent-specific UI components
│   │   ├── MailerPandaAgent.tsx   # Email marketing interface
│   │   ├── FinanceAgent.tsx       # Finance dashboard
│   │   ├── RelationshipAgent.tsx  # Contact management
│   │   ├── AICalendarAgent.tsx    # Calendar interface
│   │   └── ResearchAgent.tsx      # Research tools
│   ├── src/services/              # API integration layer
│   └── src/contexts/              # State management
├── 🐍 api.py                      # FastAPI Backend Server
├── 🔐 hushh_mcp/                  # Core Protocol Framework
│   ├── agents/                    # AI Agent Implementations
│   │   ├── mailerpanda/          # Email marketing agent
│   │   ├── chandufinance/        # Financial analysis agent
│   │   ├── relationship_memory/   # Contact management agent
│   │   ├── addtocalendar/        # Calendar integration agent
│   │   └── research_agent/       # Information research agent
│   ├── consent/token.py          # Cryptographic consent management
│   ├── vault/encrypt.py          # AES-256-GCM data encryption
│   ├── trust/link.py             # Agent-to-agent trust delegation
│   └── operons/                  # Reusable AI functions
└── 🧪 tests/                     # Comprehensive test suite
```

---

## 🔐 Security & Privacy Architecture

### Cryptographic Consent Protocol
- **HMAC-SHA256 Signed Tokens** for all permissions
- **Time-bound Authorization** with automatic expiration
- **Scope-limited Access** - agents can only access permitted data
- **Revocation System** for immediate permission withdrawal

### Data Protection
- **AES-256-GCM Encryption** for all stored personal data
- **Zero-knowledge Architecture** - we can't see your data without consent
- **Local Storage Options** for maximum privacy
- **GDPR Compliant** design patterns

### Trust Framework
- **Agent-to-Agent Delegation** with cryptographic verification
- **Audit Trails** for all data access and modifications
- **Consent Verification** before every sensitive operation

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.8+** with pip
- **Node.js 18+** with npm/yarn
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

### 1. 📥 Clone & Setup Backend

```bash
git clone https://github.com/AAK121/Hushh_Hackathon_Team_Mailer.git
cd Hushh_Hackathon_Team_Mailer
pip install -r requirements.txt
```

### 2. 🔐 Configure Environment

Create your `.env` file:
```bash
cp .env.example .env
```

Add your API keys:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
SMTP_PASSWORD=your_email_app_password
DEFAULT_FROM_EMAIL=your-email@gmail.com
ENCRYPTION_KEY=your_32_byte_hex_key
```

### 3. 🚀 Start the Backend Server

```bash
python api.py
```
Backend runs on `http://localhost:8000`

### 4. 🌐 Setup Frontend

In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
Frontend runs on `http://localhost:5173`

### 5. 🎉 Access the Application

Open your browser to `http://localhost:5173` and start interacting with your AI agents!

---

## 💡 Core Features & Usage

### 🔐 Consent Management
Every agent action requires explicit user consent:
```javascript
// Frontend automatically handles consent tokens
const token = await generateConsentToken(userId, agentId, scope);
```

### 🧠 Agent Memory
Agents learn and remember your preferences:
- **Writing Style** - MailerPanda learns your email tone
- **Financial Goals** - Finance agent tracks your investment preferences
- **Relationship Context** - Memory agent maintains contact insights

### 📧 Email Campaigns
1. **Upload Contacts** - Excel file with name, email, description
2. **Write Prompt** - Natural language campaign description
3. **AI Generation** - Gemini creates personalized content
4. **Review & Approve** - Human-in-the-loop workflow
5. **Send & Track** - Secure delivery with status tracking

### 💰 Financial Analysis
- **Portfolio Tracking** with real-time data
- **Risk Assessment** based on your profile
- **Investment Recommendations** with market insights
- **Goal Planning** with progress tracking

---

## 🔧 Comprehensive API Documentation

Our API provides a unified REST interface for interacting with privacy-first AI agents, built on **FastAPI + HushMCP** framework.

**Framework:** FastAPI + HushMCP  
**Supported Agents:** AddToCalendar, MailerPanda, ChanduFinance, Relationship Memory

### ✨ Key API Features

- **🤖 Multi-Agent Support**: AddToCalendar, MailerPanda, ChanduFinance, and Relationship Memory agents
- **🔒 Privacy-First Design**: Complete consent token validation
- **👥 Human-in-the-Loop**: Interactive approval workflows
- **📊 Real-time Status**: Session management and progress tracking
- **🛡️ Secure Operations**: HushMCP framework integration
- **📚 Interactive Docs**: Built-in Swagger UI documentation
- **🔄 CORS Support**: Frontend integration ready

### 🏗️ API Architecture

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

### 🚀 API Quick Start

```bash
# Start the API server
python api.py

# API will be available at:
# Main API: http://127.0.0.1:8001
# Interactive Docs: http://127.0.0.1:8001/docs
# Alternative Docs: http://127.0.0.1:8001/redoc
```

### 🔑 Authentication & Consent

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

### 📅 AddToCalendar Agent API

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

### 📧 MailerPanda Agent API

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

---

## 🏗️ Architecture Deep Dive

### HushhMCP Protocol
- **Stateless Tokens** - No server-side session storage
- **Cryptographic Signatures** - HMAC-SHA256 verification
- **Scope Isolation** - Fine-grained permission control
- **Time Bounds** - Automatic token expiration

### Agent Framework
- **LangGraph Workflows** - Complex multi-step processes
- **Memory Persistence** - Encrypted user preference storage
- **Cross-Agent Communication** - Secure trust delegation
- **Error Recovery** - Robust failure handling

### Frontend Architecture
- **React 19** with TypeScript
- **Real-time Updates** with WebSocket connections
- **State Management** with React Context
- **Component Isolation** - Agent-specific UI modules

---

## 🤖 Building Custom Agents

### 1. Generate Agent Scaffold
```bash
python hushh_mcp/cli/generate_agent.py my-custom-agent
```

### 2. Implement Agent Logic
```python
# hushh_mcp/agents/my_custom_agent/index.py
from hushh_mcp.consent.token import validate_token
from hushh_mcp.vault.encrypt import get_encrypted_data

async def execute_agent(user_id: str, tokens: dict, user_input: str):
    # Validate consent
    if not validate_token(tokens.get('vault.read.data'), user_id, 'vault.read.data'):
        raise PermissionError("Invalid consent token")
    
    # Access encrypted data
    user_data = await get_encrypted_data(user_id, 'my_data_key')
    
    # Your custom logic here
    result = process_user_request(user_input, user_data)
    
    return {"status": "success", "result": result}
```

### 3. Add Frontend Component
```tsx
// frontend/src/components/MyCustomAgent.tsx
import React from 'react';
import { useHushMCP } from '../hooks/useHushMCP';

const MyCustomAgent: React.FC = () => {
  const { executeAgent, generateToken } = useHushMCP();
  
  const handleExecute = async (input: string) => {
    const tokens = await generateToken('my-custom-agent', 'vault.read.data');
    const result = await executeAgent('my-custom-agent', input, tokens);
    return result;
  };
  
  return (
    <div>
      {/* Your UI here */}
    </div>
  );
};
```

---

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

### External Resources
- [HushhMCP Specification](https://github.com/hushh-labs/hushhmcp-spec)
- [Privacy-First AI Principles](https://hushh.ai/privacy)
- [Agent Development Tutorials](https://docs.hushh.ai/agents)

---

## 🛠️ Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check Python version
python --version  # Should be 3.8+

# Install dependencies
pip install -r requirements.txt

# Check environment variables
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('Keys loaded:', bool(os.getenv('GOOGLE_API_KEY')))"
```

#### Frontend Build Errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+
```

#### Agent Permission Errors
- Verify consent tokens are properly generated
- Check token expiration times
- Ensure scope matches required permissions

### Getting Help
- 📧 Email: support@hushh.ai
- 💬 Discord: [Join our community](https://discord.gg/hushh)
- 🐛 Issues: [GitHub Issues](https://github.com/AAK121/Hushh_Hackathon_Team_Mailer/issues)

---

## 💡 Roadmap & Future Vision

### 🎯 Immediate Goals
- [ ] **Advanced Personalization Engine** - Multi-modal user preference learning
- [ ] **Real-time Collaboration** - Multi-user agent interactions
- [ ] **Mobile Applications** - iOS and Android native apps
- [ ] **Enterprise Integration** - SSO and team management features

### 🚀 Long-term Vision
- [ ] **Federated Agent Network** - Cross-platform agent communication
- [ ] **Blockchain Integration** - Immutable consent and trust records
- [ ] **Open Agent Marketplace** - Community-built agent ecosystem
- [ ] **Advanced AI Models** - Custom fine-tuned models for each agent

---

## � Built For: Hushh PDA Hackathon

This project was developed as part of the **Hushh Personal Data Assistant Hackathon**, demonstrating the future of privacy-first AI agents.

### 🎓 Hackathon Details
- **Organizers**: Hushh Labs in collaboration with DAV Team and Analytics Club, IIT Bombay
- **Prize Pool**: INR 1,70,000+
- **Theme**: Building infrastructure for programmable trust and consent
- **Focus**: Real-world AI agents that respect user privacy and autonomy

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

## ⚖️ License & Legal

### 📜 MIT License
```
MIT License

Copyright (c) 2025 Hushh AI Agent Ecosystem Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
