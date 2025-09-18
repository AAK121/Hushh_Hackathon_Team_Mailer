# hushh_mcp/agents/addtocalendar/manifest.py

from hushh_mcp.constants import ConsentScope

# Defines the agent's identity and the permissions it needs to function.
manifest = {
    "id": "agent_addtocalendar",
    "name": "Self-Contained Calendar Agent",
    "description": "A self-contained agent that reads emails, identifies events, and adds them to a calendar under user consent.",
    "scopes": [
        ConsentScope.VAULT_READ_EMAIL,
        ConsentScope.VAULT_WRITE_CALENDAR
    ],
    "version": "1.1.0"
}