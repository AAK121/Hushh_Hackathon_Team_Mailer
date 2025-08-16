# Relationship Memory Agent - Setup and Usage Guide

## ✅ Fixed Issues
- **Token Authentication**: Fixed token generation to use proper HushhConsentTokens
- **API Port Conflict**: Changed relationship memory API to run on port 8001 (main API uses 8000)
- **Demo Functionality**: Updated both interactive demos with proper token handling

## 🚀 How to Run the Agent

### Option 1: Interactive Chat Demo (Recommended for Testing)
```bash
cd "c:\Users\Dell\Downloads\Pda_mailer\Pda_mailer"
python hushh_mcp\agents\relationship_memory\interactive_chat_demo.py
```

### Option 2: Interactive Proactive Demo
```bash
cd "c:\Users\Dell\Downloads\Pda_mailer\Pda_mailer"
python hushh_mcp\agents\relationship_memory\interactive_proactive_demo.py
```

### Option 3: API Server (For Frontend Integration)
```bash
cd "c:\Users\Dell\Downloads\Pda_mailer\Pda_mailer"
python hushh_mcp\agents\relationship_memory\api.py
```
- API will run on http://localhost:8001
- Documentation: http://localhost:8001/docs
- Interactive API: http://localhost:8001/redoc

## 🧪 Testing the API (Run in separate terminal while API is running)
```bash
cd "c:\Users\Dell\Downloads\Pda_mailer\Pda_mailer"
python test_relationship_api.py
```

## 🎯 Available Features

### Core Functions
1. **Contact Management**
   - Add contacts with email, phone, notes
   - Update existing contact information
   - View all contacts
   - Get detailed contact information
   - Search contacts

2. **Memory Management**
   - Add memories about contacts
   - Associate memories with locations and dates
   - Tag memories for organization
   - View memories for specific contacts

3. **Date Management** (NEW!)
   - Add birthdays, anniversaries, and other important dates
   - Support for DD-MM format with optional year
   - View upcoming dates and events
   - Calculate days until events

4. **Reminder System**
   - Set reminders about contacts
   - Priority levels (low, medium, high)
   - Date-based reminders
   - View all reminders

5. **Proactive Features**
   - Startup checks for upcoming events
   - Reconnection suggestions based on contact priority
   - Intelligent conversation advice

### Example Commands (Natural Language)
```
# Contacts
"add contact John Smith with email john@example.com"
"add Sarah Wilson with phone 555-1234 and email sarah@work.com"
"show all my contacts"
"tell me about John Smith"

# Memories
"remember that Sarah loves photography"
"Sarah mentioned she works at Google in San Francisco"
"add memory: John graduated from MIT in 2020"

# Important Dates
"John's birthday is on March 15th"
"Sarah's work anniversary is June 22nd"
"add anniversary for Mike on December 5th"
"show upcoming birthdays"

# Reminders
"remind me to call Sarah about the project"
"remind me to send birthday wishes to John"
"show all my reminders"

# Advice & Proactive
"what should I get John for his birthday?"
"I need advice about reconnecting with Sarah"
"proactive check"
```

## 📋 API Endpoints

### Authentication
- `POST /auth/session?user_id={user_id}` - Create session with tokens

### Core Agent
- `POST /agent/process` - Process natural language commands
- `POST /agent/proactive` - Run proactive checks

### Specific Functions
- `POST /contacts/add` - Add new contact
- `GET /contacts/list` - List all contacts
- `GET /contacts/{contact_name}` - Get contact details
- `POST /memories/add` - Add memory
- `GET /memories/list` - List memories
- `POST /dates/add` - Add important date
- `GET /dates/upcoming` - Get upcoming dates
- `POST /reminders/add` - Add reminder
- `GET /reminders/list` - List reminders

### Utility
- `GET /` - Service information
- `GET /health` - Health check

## 🗂️ Clean File Structure

### Main Files (Keep)
- `index.py` - Main agent implementation with LangGraph workflow
- `api.py` - FastAPI REST API server
- `interactive_chat_demo.py` - Natural language chat interface
- `interactive_proactive_demo.py` - Feature demonstration
- `utils/vault_manager.py` - Data storage and encryption
- `README.md` - Documentation

### Test Files
- `test_relationship_api.py` - Comprehensive API testing

### Removed Files (Old/Unnecessary)
- `interactive_test.py` - Old demo with token issues

## 🔧 Configuration

### Required Environment Variables (.env)
```env
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_secret_key_32_chars_minimum
VAULT_ENCRYPTION_KEY=your_64_char_hex_key_for_aes256
```

### Required Python Packages
- fastapi
- uvicorn
- langchain-google-genai
- langgraph
- pydantic
- cryptography
- requests (for testing)

## 🚨 Important Notes

1. **Port Configuration**: 
   - Relationship Memory API: Port 8001
   - Main HushMCP API: Port 8000

2. **Token Security**: 
   - Uses proper HushhConsentToken format
   - Expires in 24 hours for demos
   - Required for all operations

3. **Data Storage**: 
   - AES-256-GCM encryption
   - JSON format with structured fields
   - Contact dates in DD-MM format

4. **LangGraph Workflow**: 
   - Gemini AI for intent parsing
   - Confidence-based action routing
   - Support for batch operations

## 🎯 Next Steps for Frontend Integration

1. **Start the API server** on port 8001
2. **Use the session endpoint** to get user tokens
3. **Send natural language commands** to `/agent/process`
4. **Use specific endpoints** for direct operations
5. **Implement proactive features** using `/agent/proactive`

The agent is now fully functional with proper token authentication and comprehensive API endpoints ready for frontend integration!
