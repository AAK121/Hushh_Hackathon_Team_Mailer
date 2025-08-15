# 🤖 Relationship Memory Agent

An AI-powered agent that manages contacts, memories, and reminders using LangGraph and Gemini AI with full vault encryption and MCP compliance.

## 🎯 Features

- **🧠 AI-Powered Natural Language Processing** - Uses Google Gemini AI for intelligent input parsing
- **👥 Contact Management** - Store and manage contacts with emails, phones, and additional details
- **💭 Memory Tracking** - Remember interactions and important details about relationships
- **⏰ Smart Reminders** - Set and manage reminders for important follow-ups
- **🔐 Encrypted Vault Storage** - All data is encrypted using Hush MCP vault system
- **🕸️ LangGraph State Management** - Advanced workflow with proper error handling
- **✅ Full MCP Compliance** - Proper consent token validation and scope management

## 📁 File Structure

```
relationship_memory/
├── index.py              # Main entry point with token validation
├── manifest.py           # Agent metadata and required scopes
├── run_agent.py          # Standalone script with token issuance
├── langgraph_agent.py    # LangGraph implementation with Gemini AI
├── .env                  # Environment configuration
├── README.md             # This file
├── __init__.py           # Package initialization
├── utils/                # Utility modules
├── legacy/               # Legacy implementations
└── tests/                # Test files and demos
```

## 🚀 Quick Start

### 1. Environment Setup

The agent now uses the main project `.env` file located at the project root.
Make sure your main `.env` file contains:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here_at_least_32_characters_long
VAULT_ENCRYPTION_KEY=64_character_hex_string_for_vault_encryption
```

### 2. Install Dependencies

```bash
pip install langchain-google-genai langgraph pydantic python-dotenv
```

### 3. Run the Agent

#### Interactive Mode:
```bash
python run_agent.py
```

#### Demo Mode:
```bash
python run_agent.py demo
```

#### Direct Usage:
```python
from hushh_mcp.agents.relationship_memory.index import run_agent
result = run_agent(demo_mode=True)
```

## 🔧 Usage Examples

### Adding Contacts
```
> add john smith with email john@example.com
> add sarah with phone 9876543210 working at google
```

### Managing Memories
```
> remember that I met sarah at the conference
> remember that john likes coffee and works late
```

### Setting Reminders
```
> remind me to call mike on 2024-03-15
> remind me to follow up with sarah next week
```

### Viewing Data
```
> show my contacts
> show all memories
> search for contacts at google
```

## 🏗️ Architecture

### LangGraph Workflow
1. **Input Parsing Node** - Uses Gemini AI to extract structured data
2. **Validation Node** - Validates extracted information
3. **Action Execution Node** - Performs the requested operation
4. **Response Generation Node** - Formats the response

### MCP Compliance
- **Token Validation** - All operations require valid consent tokens
- **Scope Checking** - Operations are limited to granted permissions
- **Vault Encryption** - All data is encrypted before storage
- **User Isolation** - Data is scoped to individual users

## 🔐 Required Permissions

The agent requires the following consent scopes:
- `VAULT_READ_CONTACTS` - Reading contact information
- `VAULT_WRITE_CONTACTS` - Creating/updating contacts
- `VAULT_READ_MEMORY` - Accessing stored memories
- `VAULT_WRITE_MEMORY` - Creating new memories
- `VAULT_READ_REMINDER` - Reading reminders
- `VAULT_WRITE_REMINDER` - Creating/updating reminders

## 🧪 Testing

Run the test suite:
```bash
cd tests/
python test_gemini.py
```

## 📝 API Reference

### Main Handler Class
```python
class RelationshipMemoryAgentHandler:
    def handle(self, user_id: str, tokens: Dict[str, str], 
               user_input: str, vault_key: str = None) -> Dict[str, Any]
```

### Standalone Function
```python
def run_agent(user_id: str = None, vault_key: str = None, 
              demo_mode: bool = True) -> Dict[str, Any]
```

## 🤝 Contributing

1. Follow the MCP agent standards defined in `/docs/agents.md`
2. Ensure all operations respect consent token scopes
3. Add tests for new functionality
4. Update this README for significant changes

## 📜 License

MIT License - See project root for details.
