# hushh_mcp/agents/research_agent/manifest.py

from hushh_mcp.constants import ConsentScope

manifest = {
    "id": "agent_research",
    "name": "Research Agent",
    "version": "1.0.0",
    "description": "AI-powered academic research assistant with arXiv integration and intelligent paper analysis",
    "author": "HushMCP Team",
    "license": "MIT",
    "required_scopes": {
        "arxiv_search": [ConsentScope.CUSTOM_TEMPORARY],
        "pdf_processing": [ConsentScope.VAULT_READ_FILE, ConsentScope.VAULT_WRITE_FILE],
        "note_management": [ConsentScope.VAULT_WRITE_FILE, ConsentScope.VAULT_READ_FILE],
        "paper_analysis": [ConsentScope.CUSTOM_TEMPORARY],
        "session_storage": [ConsentScope.VAULT_WRITE_FILE]
    },
    "capabilities": [
        "Natural language arXiv search query optimization",
        "Academic paper PDF processing and text extraction", 
        "AI-powered paper summarization",
        "Interactive snippet analysis with custom instructions",
        "Multi-editor note management with vault storage",
        "Session state management"
    ],
    "trust_links": {
        "supported": True,
        "delegation_scopes": [
            ConsentScope.VAULT_READ_FILE,
            ConsentScope.VAULT_WRITE_FILE,
            ConsentScope.CUSTOM_TEMPORARY
        ]
    },
    "api_endpoints": [
        "/paper/search/arxiv",
        "/paper/upload", 
        "/paper/{paper_id}/summary",
        "/paper/{paper_id}/process/snippet",
        "/session/notes"
    ]
}
