# hushh_mcp/operons/__init__.py

"""
Operons Module
==============

This module provides operational analysis capabilities for the HushMCP framework.
"""

from .email_analysis import analyze_email
from .financial_modeling import create_financial_model
from .verify_email import verify_email_address

__all__ = ["analyze_email", "create_financial_model", "verify_email_address"]