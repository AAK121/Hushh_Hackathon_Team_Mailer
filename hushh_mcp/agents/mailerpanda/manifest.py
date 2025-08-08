from hushh_mcp.constants import ConsentScope

manifest = {
    "id": "agent_mailerpanda",
    "name": "AI-Powered MailerPanda Agent",
    "description": "An advanced email campaign agent with AI content generation, human-in-the-loop approval, LangGraph workflows, and privacy-first consent management using HushMCP framework.",
    "version": "3.0.0",
    "features": [
        "AI Content Generation (Gemini-2.0-flash)",
        "Human-in-the-Loop Approval Workflow", 
        "LangGraph State Management",
        "Mass Email with Excel Integration",
        "Dynamic Placeholder Detection",
        "Real-time Status Tracking",
        "HushMCP Consent-Driven Operations",
        "Secure Vault Data Storage",
        "Trust Link Agent Delegation",
        "Interactive Feedback Loop",
        "Error Recovery & Logging",
        "Cross-Agent Communication"
    ],
    "scopes": [
        ConsentScope.VAULT_READ_EMAIL,    # For reading contact data and email templates
        ConsentScope.VAULT_WRITE_EMAIL,   # For storing campaign results and drafts
        ConsentScope.VAULT_READ_FILE,     # For reading Excel contact files
        ConsentScope.VAULT_WRITE_FILE,    # For writing status files
        ConsentScope.CUSTOM_TEMPORARY     # For AI generation and email sending
    ],
    "required_scopes": {
        "content_generation": [ConsentScope.VAULT_READ_EMAIL, ConsentScope.CUSTOM_TEMPORARY],
        "email_sending": [ConsentScope.VAULT_READ_EMAIL, ConsentScope.VAULT_WRITE_EMAIL, ConsentScope.CUSTOM_TEMPORARY],
        "contact_management": [ConsentScope.VAULT_READ_FILE, ConsentScope.VAULT_WRITE_FILE],
        "campaign_storage": [ConsentScope.VAULT_WRITE_EMAIL, ConsentScope.VAULT_WRITE_FILE]
    },
    "trust_links": {
        "can_delegate_to": [
            "agent_addtocalendar",  # For calendar event creation from email campaigns
            "agent_identity",       # For user verification and authentication
            "agent_shopper"         # For product recommendation integration
        ],
        "can_receive_from": [
            "agent_addtocalendar",  # Receiving calendar event data for email campaigns
            "agent_identity"        # Receiving verified user identity data
        ]
    },
    "requirements": {
        "python_version": ">=3.8",
        "dependencies": [
            "langgraph>=0.1.0",
            "langchain-google-genai>=1.0.0", 
            "mailjet-rest>=1.3.0",
            "pandas>=1.5.0",
            "python-dotenv>=1.0.0",
            "typing-extensions>=4.0.0"
        ],
        "environment_variables": [
            "MAILJET_API_KEY",
            "MAILJET_API_SECRET", 
            "GOOGLE_API_KEY",
            "SENDER_EMAIL"
        ]
    },
    "usage_modes": [
        "interactive",      # Full interactive workflow
        "predefined",       # Quick testing with predefined campaign
        "demo",            # Feature demonstration
        "headless"         # API-driven without user interaction
    ],
    "hushh_mcp_version": "1.0.0"
}