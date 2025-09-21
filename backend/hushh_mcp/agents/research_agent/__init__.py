"""
Research Agent Package
=====================

This package contains the Research Agent implementation for the HushMCP framework.
The Research Agent provides capabilities for academic paper search, analysis, and chat.
"""

from .index import ResearchAgent, research_agent
from .manifest import manifest as RESEARCH_AGENT_MANIFEST

__version__ = "1.0.0"
__all__ = ["ResearchAgent", "research_agent", "RESEARCH_AGENT_MANIFEST"]