"""
HushMCP Agents Package
=====================

This package contains all the agent implementations for the HushMCP framework.
"""

__all__ = []

# Import agents with error handling to prevent blocking entire package
try:
    from .research_agent import ResearchAgent, research_agent
    __all__.extend(["ResearchAgent", "research_agent"])
except ImportError as e:
    print(f"Warning: Could not import research_agent: {e}")

try:
    from .mailerpanda.index import MassMailerAgent
    __all__.extend(["MassMailerAgent"])
except ImportError as e:
    print(f"Warning: Could not import MailerPanda functions: {e}")