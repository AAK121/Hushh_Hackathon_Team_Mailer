# hushh_mcp/agents/relationship_memory/manifest.py

from hushh_mcp.constants import ConsentScope

# Defines the agent's identity and the permissions it needs to function.
manifest = {
    "id": "agent_relationship_memory",
    "name": "Relationship Memory Agent",
    "description": "An AI-powered agent that manages contacts, memories, and reminders using LangGraph and Gemini AI with full vault encryption and MCP compliance.",
    "scopes": [
        ConsentScope.VAULT_READ_CONTACTS,
        ConsentScope.VAULT_WRITE_CONTACTS,
        ConsentScope.VAULT_READ_MEMORY,
        ConsentScope.VAULT_WRITE_MEMORY,
        ConsentScope.VAULT_READ_REMINDER,
        ConsentScope.VAULT_WRITE_REMINDER
    ],
    "version": "2.0.0",
    "author": "HushhMCP Team",
    "features": [
        "Natural language processing with Gemini AI",
        "Contact management with email and phone",
        "Memory tracking for relationships", 
        "Smart reminder system",
        "Encrypted vault storage",
        "LangGraph state management"
    ],
    "requirements": [
        "langchain-google-genai",
        "langgraph", 
        "pydantic",
        "python-dotenv"
    ]
}
