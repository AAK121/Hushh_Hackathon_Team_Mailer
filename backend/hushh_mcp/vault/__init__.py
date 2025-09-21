# hushh_mcp/vault/__init__.py

"""
Vault Module
============

This module provides encryption and secure storage capabilities for the HushMCP framework.
"""

from .encrypt import encrypt_data, decrypt_data
from .user_keys import generate_user_key, get_user_key
from .user_vault import UserVault

__all__ = [
    "encrypt_data",
    "decrypt_data", 
    "generate_user_key",
    "get_user_key",
    "UserVault"
]