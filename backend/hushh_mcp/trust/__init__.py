# hushh_mcp/trust/__init__.py

"""
Trust Module
============

This module provides trust link management for the HushMCP framework.
"""

from .link import create_trust_link, verify_trust_link

__all__ = ["create_trust_link", "verify_trust_link"]