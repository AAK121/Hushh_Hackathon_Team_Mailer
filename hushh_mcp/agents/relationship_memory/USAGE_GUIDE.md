# 🎯 Proactive Relationship Manager Agent - Usage Guide

## 🚀 How to Run the Interactive Demo

### Full HushhMCP Compliant Demo (Recommended)
```bash
python full_compliance_chat_demo.py
```

This runs the complete implementation with:
- ✅ Full HushhMCP token validation
- ✅ Proper vault integration
- ✅ Real Gemini LLM calls
- ✅ All enhanced features

### LLM-Only Demo (For Testing Intent Parsing)
```bash
python chat_demo_llm_only.py
```

This focuses on LLM capabilities without token validation.

## 💬 Natural Language Commands

### 📝 Adding Contacts

**Single Contact:**
```
add contact John Smith with email john@example.com
add high priority contact Sarah Johnson at sarah@techcorp.com
```

**Batch Contacts:**
```
add contacts: Alice Johnson and Bob Wilson with phone 555-1234
add these contacts: Mike Rodriguez with email mike@design.com and Lisa Wang at +1-555-0789
```

### 🧠 Adding Memories

```
remember that John loves photography and just bought a new camera
remember that Sarah mentioned she's planning a trip to Japan next month
John told me he's interested in machine learning and AI
```

### 📅 Important Dates

```
John's birthday is on March 15th
Sarah's work anniversary is June 22nd, 2020
add birthday for Mike on December 5th
```

### 💡 Getting Advice

```
what should I get John for his birthday?
I need advice about reconnecting with Sarah
help me plan a conversation with Mike
what are good topics to discuss with Lisa?
```

### 📋 Viewing Information

```
show me all my contacts
show upcoming birthdays and anniversaries
show my recent memories
tell me about John Smith
```

### 🚀 Proactive Features

```
proactive check
startup check
check for upcoming events
```

## 🔧 System Commands

- `help` - Show comprehensive help
- `status` - Show system status and compliance info
- `tokens` - Show token validation status
- `quit` or `exit` - Leave the demo

## ✨ Key Features Demonstrated

### 🧠 Advanced LLM Integration
- Natural language understanding with Gemini API
- Batch contact recognition from single input
- Intent parsing with high confidence scores
- Context-aware response generation

### 📦 Batch Processing
The agent can process multiple contacts in one command:
```
add contacts: Alice with email alice@startup.com, Bob at +1-555-0123, and Carol from TechCorp
```

### 🚀 Proactive Capabilities
- Automatic birthday/anniversary detection
- Reconnection suggestions based on priority levels
- Startup notifications for upcoming events

### 💡 Conversational Advice
- Memory-based recommendations
- Contextual suggestions for gifts and conversations
- Relationship management advice

### 📅 Interaction History Tracking
- Automatic last_talked_date updates
- Priority-based reconnection timing
- Days since contact calculations

### 🔐 Full HushhMCP Compliance
- Proper token validation and signing
- Secure vault integration
- Scope-based permission checking
- Complete audit trail

## 🎯 Example Session

```
[1] 🗣️ You: add contact Sarah Chen with email sarah@techstartup.com, she's a high priority contact

🤖 Agent Response (HushhMCP Compliant):
✅ Successfully added Sarah Chen to your contacts
🔐 Validated Scopes: vault.read.contacts, vault.write.contacts
⚙️ Action: add_contact

[2] 🗣️ You: remember that Sarah loves rock climbing and photography

🤖 Agent Response (HushhMCP Compliant):
✅ Successfully recorded memory about Sarah Chen (interaction timestamp updated)
⚙️ Action: add_memory

[3] 🗣️ You: what should I get Sarah for her birthday?

🤖 Agent Response (HushhMCP Compliant):
✅ Based on your memories, Sarah loves rock climbing and photography. Consider getting her climbing gear like a new harness or chalk bag, or photography equipment like a camera lens or tripod!
⚙️ Action: advice_generated
```

## 🔧 Troubleshooting

### Token Issues
If you see token validation errors, run:
```
tokens
```
This will show the status of all HushhMCP tokens.

### System Status
To check overall system health:
```
status
```

### Environment Requirements
Make sure you have:
- `GEMINI_API_KEY` - Your Gemini API key
- `SECRET_KEY` - HushhMCP secret key for token signing

## 🎉 Success Indicators

When everything is working correctly, you'll see:
- ✅ Token validation messages
- 🔐 Validated scopes in responses
- 🔍 LangGraph debug messages showing intent parsing
- ⚙️ Action taken indicators
- 📊 Data processing confirmations

The agent maintains full HushhMCP compliance while providing an intuitive natural language interface for relationship management!