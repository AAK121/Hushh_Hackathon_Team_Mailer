# 🐼 MailerPanda Agent - Enhanced AI Email Campaign System

A privacy-first, AI-powered mass email agent with human-in-the-loop approval, built on the HushMCP consent framework.

## 🚀 Features

### 🤖 AI-Powered Content Generation
- **Gemini Integration**: Uses Google's Gemini-2.0-flash for intelligent email drafting
- **Context-Aware**: Understands email intent and generates appropriate content
- **Placeholder Support**: Automatically detects and uses Excel column placeholders

### 👨‍💼 Human-in-the-Loop Workflow
- **Interactive Approval**: Human review required before sending any emails
- **Iterative Feedback**: Refine emails through multiple rounds of AI generation
- **Real-time Preview**: See exactly what will be sent before approval

### 🔄 LangGraph State Management
- **Structured Workflow**: Graph-based state management for complex email campaigns
- **Conditional Routing**: Intelligent decision-making based on user feedback
- **State Persistence**: Maintains context throughout the entire workflow

### 📊 Advanced Email Features
- **Mass Email Support**: Process large contact lists from Excel files
- **Personalization**: Dynamic placeholder replacement for each recipient
- **Status Tracking**: Real-time status updates and comprehensive logging
- **Error Handling**: Graceful failure handling with detailed error reports

### 🔐 Privacy & Consent (HushMCP)
- **Consent Validation**: Every operation requires explicit user permission
- **Granular Scopes**: Fine-grained control over data access permissions
- **Token-Based Security**: Cryptographically signed consent tokens
- **Audit Trail**: Complete logging of all consent validations

## 🛠️ Technical Architecture

```python
# LangGraph Workflow
START → AI Content Generation → Human Feedback → [Approved?] → Send Emails → END
                    ↑                              ↓
                    └─── Refinement Loop ──────────┘
```

### Components
- **State Management**: `AgentState` TypedDict with comprehensive email campaign state
- **AI Engine**: Google Gemini for natural language email generation
- **Email Service**: Mailjet API for reliable email delivery
- **Data Processing**: Pandas for Excel file handling and placeholder management
- **Consent Framework**: HushMCP for privacy-first operations

## 📁 Project Structure

```
mailerpanda/
├── index.py              # Main agent implementation
├── manifest.py           # Agent metadata and permissions
├── run_agent.py          # Interactive runner with CLI options
├── demo_interactive.py   # Feature demonstration script
├── .env                  # Environment configuration
├── email_list.xlsx       # Sample contact database
├── email_status.xlsx     # Delivery status tracking
└── README.md             # This file
```

## 🚀 Quick Start

### 1. Environment Setup

Create a `.env` file with your API keys:

```env
# Mailjet API Keys
MAILJET_API_KEY="your_mailjet_api_key"
MAILJET_API_SECRET="your_mailjet_secret"

# Sender Configuration
SENDER_EMAIL="your_email@domain.com"

# Google AI
GOOGLE_API_KEY="your_google_api_key"
```

### 2. Install Dependencies

```bash
pip install langgraph langchain-google-genai mailjet-rest pandas python-dotenv
```

### 3. Prepare Contact List

Create `email_list.xlsx` with columns:
- `name`: Recipient name
- `email`: Email address
- `company_name`: Company/organization (optional)

### 4. Run Interactive Mode

```bash
python run_agent.py
```

### 5. Run Predefined Campaign

```bash
python run_agent.py --predefined
```

## 💡 Usage Examples

### Interactive Campaign Creation
```python
# User Input: "Send welcome emails to new team members"
# AI generates professional email template
# Human reviews and approves/refines
# Mass email sent with personalization
```

### Mass Email with Placeholders
```python
# Email template: "Dear {name}, welcome to {company_name}!"
# Automatically fills placeholders from Excel data
# Each recipient gets personalized email
```

### Human-in-the-Loop Approval
```
📧 Draft Email Preview:
📌 Subject: Welcome to Our Team!
📝 Content: Dear {name}, we're excited to welcome you...

✅ Approve this email? (yes/y/approve OR provide feedback): 
> make it more formal

# AI refines based on feedback and shows new version
```

## 🔧 Advanced Configuration

### Custom LangGraph Nodes
```python
def custom_content_node(state: AgentState) -> dict:
    # Custom email generation logic
    return {"email_template": custom_content}

# Add to workflow
graph_builder.add_node("custom_node", custom_content_node)
```

### Consent Scope Customization
```python
# Define custom permission scopes
manifest = {
    "scopes": [
        ConsentScope.CUSTOM_TEMPORARY,
        ConsentScope.VAULT_READ_EMAIL,
        # Add more as needed
    ]
}
```

## 📊 Monitoring & Analytics

### Email Status Tracking
- Real-time delivery status
- Bounce/failure handling
- Comprehensive logging
- Excel export of results

### Consent Audit Trail
- All permission checks logged
- Token validation history
- User approval tracking

## 🛡️ Security Features

### HushMCP Consent Framework
- **Token Validation**: Every operation requires valid consent
- **Scope Isolation**: Operations limited to granted permissions
- **Time-bound Access**: Tokens automatically expire
- **Revocation Support**: Immediate permission withdrawal

### Data Protection
- **No Persistent Storage**: Contact data processed in memory
- **Encryption**: All consent tokens cryptographically signed
- **Access Control**: Granular permission management

## 🧪 Demo & Testing

### Feature Showcase
```bash
python demo_interactive.py --features
```

### Interactive Demo
```bash
python demo_interactive.py
```

### Predefined Test Campaign
```bash
python run_agent.py --predefined
```

## 🔄 Workflow Details

1. **Initialization**: Load environment, validate API keys, initialize AI models
2. **User Input**: Collect email campaign requirements
3. **Consent Validation**: Verify permissions for AI generation
4. **Content Generation**: AI drafts email based on user input
5. **Human Review**: Present draft for approval/feedback
6. **Refinement Loop**: Iterate based on feedback until approved
7. **Final Consent**: Validate permissions for email sending
8. **Email Delivery**: Send personalized emails to all contacts
9. **Status Tracking**: Log delivery results and save to Excel

## 📈 Scalability

- **Batch Processing**: Handles large contact lists efficiently
- **Error Recovery**: Continues processing despite individual failures
- **Rate Limiting**: Respects email service API limits
- **Memory Optimization**: Processes contacts in chunks for large datasets

## 🤝 Integration

### HushMCP Framework
Seamlessly integrates with other HushMCP agents for multi-agent workflows.

### External APIs
- **Mailjet**: Primary email delivery service
- **Google Gemini**: AI content generation
- **Excel/CSV**: Contact data sources

## 📝 License

Part of the HushMCP framework - Privacy-first AI agent platform.

## 🆘 Troubleshooting

### Common Issues
1. **Missing API Keys**: Check `.env` file configuration
2. **Excel Format**: Ensure proper column names (`name`, `email`)
3. **Network Issues**: Verify internet connectivity for API calls
4. **Consent Errors**: Check token validity and scope permissions

### Debug Mode
Add verbose logging by setting environment variable:
```bash
export DEBUG=true
python run_agent.py
```
