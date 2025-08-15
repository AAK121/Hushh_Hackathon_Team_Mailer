# hushh_mcp/agents/relationship_memory/manifest.py

from hushh_mcp.constants import ConsentScope

manifest = {
    "id": "relationship_memory",
    "name": "Relationship Memory Agent",
    "description": "AI-powered agent for managing contacts, memories, and reminders with natural language understanding",
    "scopes": [
        ConsentScope.VAULT_READ_CONTACTS,
        ConsentScope.VAULT_WRITE_CONTACTS,
        ConsentScope.VAULT_READ_MEMORY,
        ConsentScope.VAULT_WRITE_MEMORY,
        ConsentScope.VAULT_READ_REMINDER,
        ConsentScope.VAULT_WRITE_REMINDER
    ],
    "version": "1.0.0"
}
