# 🐱 GmailCat PDA - Smart Email to Calendar Agent

**Powered by HushMCP Framework - Your Privacy-First Personal Digital Assistant**

[![HushMCP](https://img.shields.io/badge/Powered%20by-HushMCP-purple)](https://github.com/AAK121/Hushh_Hackathon_Team_Mailer)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2+-green)](https://djangoproject.com)
[![OpenAI](https://img.shields.io/badge/AI-OpenAI%20GPT--4-orange)](https://openai.com)

---

## 🎯 What This Agent Does

GmailCat PDA is an intelligent email processing agent that transforms your inbox into actionable calendar events. Here's what it does:

### Core Functionality
- **📧 Smart Email Scanning**: Automatically scans your Gmail inbox for unread emails
- **🤖 AI-Powered Event Extraction**: Uses OpenAI GPT-4 to intelligently identify events, meetings, appointments, and deadlines from email content
- **📅 Automatic Calendar Creation**: Seamlessly creates Google Calendar events with proper dates, times, and descriptions
- **🔗 Direct Integration**: Provides direct links to created calendar events for easy access
- **📊 Detailed Reporting**: Shows processing results with statistics and success/failure rates

### Smart Features
- **Natural Language Processing**: Understands various date/time formats and event descriptions
- **Context Awareness**: Extracts relevant details like meeting locations, attendees, and agenda items
- **Batch Processing**: Handles multiple emails and events in a single operation
- **Error Handling**: Gracefully handles malformed dates, missing information, and API limitations
- **Real-time Feedback**: Provides live status updates during processing

---

## 🔒 Data Security & Privacy

GmailCat PDA is built with **privacy-first** principles using the HushMCP (Hushh Model Context Protocol) framework:

### HushMCP Security Features

#### 1. **Explicit Consent Tokens** 🎫
- **Scope-Based Permissions**: Separate tokens for email reading (`VAULT_READ_EMAIL`) and calendar writing (`VAULT_WRITE_CALENDAR`)
- **Time-Limited Access**: Tokens expire after 1 hour to minimize exposure window
- **Agent-Specific**: Each token is tied to a specific agent and user ID
- **Cryptographic Signatures**: HMAC-SHA256 signed tokens prevent tampering

#### 2. **Zero Data Persistence** 🚫
- **No Email Storage**: Emails are processed in memory and immediately discarded
- **No Content Logging**: Email content is never saved to disk or external services
- **Temporary Processing**: Only the minimum required data is kept during active processing
- **Clean Memory**: All sensitive data is cleared after processing completion

#### 3. **Secure Token Management** 🔐
- **Token Validation**: Each API call validates token signature, expiration, and scope
- **Revocation Support**: Tokens can be instantly revoked if needed
- **Signature Verification**: Prevents token forgery with cryptographic validation
- **Scope Enforcement**: Operations are strictly limited to granted permissions

#### 4. **Google OAuth Security** 🛡️
- **Standard OAuth2 Flow**: Uses Google's secure authentication protocols
- **Minimal Permissions**: Requests only essential scopes (Gmail read, Calendar write)
- **User Consent**: Explicit user authorization required for each permission
- **Token Refresh**: Automatic token refresh without requiring re-authentication

#### 5. **Local Processing** 🏠
- **On-Device Execution**: All processing happens locally on your machine
- **No Cloud Storage**: No data sent to external servers except authorized APIs
- **Direct API Calls**: Direct communication with Google and OpenAI APIs only
- **No Intermediary Servers**: No third-party data processing or storage

### Privacy Guarantees
- ✅ **Your emails are never stored or logged**
- ✅ **Processing happens locally on your device**
- ✅ **Only you have access to your consent tokens**
- ✅ **Data is encrypted in transit using HTTPS**
- ✅ **No user tracking or analytics collection**
- ✅ **Full control over data access permissions**

---

## 🌐 How to Run the Website

The GmailCat PDA comes with a beautiful, modern web interface for easy interaction.

### Prerequisites
- Python 3.8 or higher
- Google account with Gmail and Calendar access
- OpenAI API key
- Google OAuth credentials

### Quick Start (Recommended)

#### Option 1: Windows Batch File (Easiest)
```bash
# Navigate to the webapp folder
cd webapp

# Double-click the batch file
start_gmailcat.bat
```

#### Option 2: Python Startup Script
```bash
# Navigate to the webapp folder
cd webapp

# Run the startup script (handles everything automatically)
python start_server.py
```

#### Option 3: Manual Django Setup
```bash
# Navigate to the webapp folder
cd webapp

# Install dependencies
pip install -r requirements.txt

# Set up database
python manage.py migrate

# Start the development server
python manage.py runserver
```

### Access the Website
1. Open your web browser
2. Navigate to: **`http://127.0.0.1:8000`**
3. Click "Process Emails & Create Events" to start
4. Complete Google OAuth if prompted
5. View results and calendar links

### Website Features
- 🎨 **Beautiful Purple Gradient UI** - Modern, responsive design
- 📱 **Mobile Friendly** - Works on all devices
- ⚡ **Real-time Progress** - Live updates during processing
- 📊 **Visual Results** - Clear statistics and event links
- 🔔 **Toast Notifications** - User-friendly error and success messages
- 🎭 **Smooth Animations** - Engaging user experience

---

## 💻 How to Run in CLI

For developers and advanced users who prefer command-line interface.

### Simple CLI Execution

```bash
# Make sure you're in the addtocalendar directory
cd hushh_mcp/agents/addtocalendar

# Run the agent directly
python run_agent.py
```

### What Happens in CLI Mode

1. **Environment Check**: Validates OpenAI API key
2. **Token Generation**: Creates secure consent tokens for both email and calendar access
3. **Email Processing**: Scans Gmail inbox for unread emails
4. **AI Analysis**: Uses GPT-4 to extract events from email content
5. **Calendar Creation**: Creates Google Calendar events
6. **Results Display**: Shows detailed JSON results with statistics

---

## 🛠️ Setup & Configuration

### 1. Environment Setup
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 2. Google Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API and Calendar API
4. Create OAuth 2.0 credentials
5. Download as `credentials.json` and place in the `addtocalendar` folder

### 3. Required Permissions
- **Gmail API**: `https://www.googleapis.com/auth/gmail.readonly`
- **Calendar API**: `https://www.googleapis.com/auth/calendar.events`

---

## 📋 Dependencies

### Core Dependencies
- **HushMCP Framework**: Privacy-first consent management
- **OpenAI**: GPT-4 for intelligent event extraction
- **Google APIs**: Gmail and Calendar integration
- **Django**: Web framework for GUI
- **Beautiful Soup**: HTML content parsing

### Complete Requirements
```
# AI & Processing
openai>=1.0.0
beautifulsoup4>=4.12.0

# Google Integration
google-auth>=2.20.0
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.1.0
google-api-python-client>=2.90.0

# Web Framework
django>=4.2.0
django-cors-headers>=4.0.0

# HushMCP Dependencies
cryptography>=42.0.5
pyjwt[crypto]>=2.8.0
pydantic>=2.7.1
python-dotenv>=1.0.1
httpx>=0.27.0
requests>=2.32.3
```

---

## 🔧 Troubleshooting

### Common Issues

**🚨 "OPENAI_API_KEY is not properly set"**
- Solution: Add your OpenAI API key to the `.env` file
- Get key from: https://platform.openai.com/account/api-keys

**🚨 "Google credentials not found"**
- Solution: Download `credentials.json` from Google Cloud Console
- Place file in the `addtocalendar` directory

**🚨 "Calendar Access Denied: Scope mismatch"**
- Solution: This is fixed in the current version with dual-token system
- Restart the application if you encounter this

**🚨 "No unread emails to process"**
- Solution: Make sure you have unread emails in your Gmail inbox
- The agent only processes unread emails for efficiency

**🚨 Django server won't start**
- Check Python version (3.8+)
- Run: `pip install -r webapp/requirements.txt`
- Try: `python webapp/manage.py migrate`

---

## 🎯 Use Cases

### Personal Productivity
- **Meeting Scheduling**: Automatically add meeting invites to calendar
- **Appointment Tracking**: Never miss doctor, dentist, or service appointments
- **Event Management**: Capture conference, webinar, and social event details
- **Deadline Tracking**: Convert project deadlines into calendar reminders

### Business Applications
- **Client Management**: Automatically schedule client meetings and calls
- **Project Coordination**: Track project milestones and deliverables
- **Travel Planning**: Capture flight, hotel, and itinerary information
- **Compliance**: Ensure important deadlines and renewals are calendared

---

## 🚀 Advanced Features

### Customization Options
- **Time Zones**: Automatically handles time zone conversions
- **Event Categories**: Smart categorization of different event types
- **Duplicate Detection**: Prevents creation of duplicate calendar events
- **Batch Processing**: Efficient handling of multiple emails simultaneously

### AI Capabilities
- **Natural Language Understanding**: Processes human-written emails
- **Context Extraction**: Identifies relevant details from email threads
- **Date Intelligence**: Handles relative dates ("next Tuesday", "in 2 weeks")
- **Multi-format Support**: Works with various email clients and formats

---

## 📊 Performance & Limits

### Processing Capacity
- **Email Batch Size**: Up to 5 emails per run (configurable)
- **Token Validity**: 1 hour per session
- **API Rate Limits**: Respects Google and OpenAI rate limiting
- **Processing Time**: ~30-60 seconds for typical email batch

### Scalability
- **User Isolation**: Each user has separate token management
- **Concurrent Users**: Supports multiple users simultaneously
- **Resource Usage**: Minimal memory footprint and CPU usage
- **Storage**: Zero persistent data storage

---

## 🤝 Contributing

We welcome contributions to improve GmailCat PDA! Areas for enhancement:

- **Additional Email Providers**: Support for Outlook, Yahoo, etc.
- **Enhanced AI Models**: Integration with other LLM providers
- **Mobile App**: Native mobile applications
- **Calendar Providers**: Support for Outlook Calendar, Apple Calendar
- **Language Support**: Multi-language email processing

---

## 📄 License

This project is part of the Hushh_Hackathon_Team_Mailer repository. See the project root for license information.

---

## 🆘 Support

For support, issues, or feature requests:
- **GitHub Issues**: [Create an issue](https://github.com/AAK121/Hushh_Hackathon_Team_Mailer/issues)
- **Documentation**: Check the `docs/` folder in the project root
- **HushMCP Framework**: Refer to HushMCP documentation for advanced usage

---

**Built with ❤️ using the HushMCP Framework - Where Privacy Meets Productivity**

*Last Updated: August 2025*
