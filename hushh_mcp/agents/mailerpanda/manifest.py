from hushh_mcp.constants import ConsentScope

manifest = {
    "id": "agent_mailerpanda",
    "name": "AI-Powered MailerPanda Agent",
    "description": "An advanced email campaign agent with AI content generation, human-in-the-loop approval, LangGraph workflows, and privacy-first consent management.",
    "version": "2.0.0",
    "features": [
        "AI Content Generation (Gemini-2.0-flash)",
        "Human-in-the-Loop Approval Workflow", 
        "LangGraph State Management",
        "Mass Email with Excel Integration",
        "Dynamic Placeholder Detection",
        "Real-time Status Tracking",
        "Consent-Driven Operations",
        "Interactive Feedback Loop",
        "Error Recovery & Logging"
    ],
    "scopes": [
        ConsentScope.CUSTOM_TEMPORARY  # Covers AI generation, file access, and email sending
    ],
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
        "demo"             # Feature demonstration
    ]
}