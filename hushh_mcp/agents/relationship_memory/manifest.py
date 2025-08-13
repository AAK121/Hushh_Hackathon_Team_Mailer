"""
Relationship Memory Agent Manifest
Defines the agent's metadata, scopes, and trust configurations
"""

from hushh_mcp.types import AgentManifest
from hushh_mcp.constants import (
    VAULT_READ_CONTACT,
    VAULT_WRITE_CONTACT,
    VAULT_READ_MEMORY,
    VAULT_WRITE_MEMORY,
    VAULT_READ_REMINDER,
    VAULT_WRITE_REMINDER
)

MANIFEST = AgentManifest(
    name="relationship_memory",
    description="AI-powered relationship memory and reminder system",
    version="1.0.0",
    required_scopes=[
        VAULT_READ_CONTACT,    # For reading contact information
        VAULT_WRITE_CONTACT,   # For updating contact details
        VAULT_READ_MEMORY,     # For accessing relationship memories
        VAULT_WRITE_MEMORY,    # For storing new memories
        VAULT_READ_REMINDER,   # For accessing reminders
        VAULT_WRITE_REMINDER   # For creating/updating reminders
    ],
    trust_link_scopes=[
        "calendar_integration",  # For scheduling reminders
        "messaging_integration"  # For sending notifications
    ],
    author="ChandreshThakur",
    license="MIT"
)
