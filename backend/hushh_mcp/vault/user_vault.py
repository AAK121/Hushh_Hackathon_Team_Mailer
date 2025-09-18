"""
User-Specific Vault Operations for HushMCP
==========================================

This module provides high-level vault operations that automatically
use user-specific encryption keys for data storage and retrieval.
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional
from hushh_mcp.vault.encrypt import encrypt_data, decrypt_data
from hushh_mcp.vault.user_keys import get_user_encryption_key
from hushh_mcp.types import EncryptedPayload

class UserVault:
    """User-specific vault for secure data storage"""
    
    def __init__(self, vault_root: str = "vault"):
        self.vault_root = Path(vault_root)
        self.vault_root.mkdir(parents=True, exist_ok=True)
    
    def _get_user_vault_dir(self, user_id: str) -> Path:
        """Get the vault directory for a specific user"""
        user_dir = self.vault_root / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    
    def store_data(self, user_id: str, key: str, data: Any) -> bool:
        """Store data securely in the user's vault"""
        try:
            # Get user's encryption key
            user_key = get_user_encryption_key(user_id)
            
            # Convert data to JSON string
            data_str = json.dumps(data, ensure_ascii=False, indent=2)
            
            # Encrypt the data
            encrypted_payload = encrypt_data(data_str, user_key)
            
            # Save to user's vault directory
            user_dir = self._get_user_vault_dir(user_id)
            file_path = user_dir / f"{key}.enc"
            
            with open(file_path, 'w') as f:
                json.dump({
                    'ciphertext': encrypted_payload.ciphertext,
                    'iv': encrypted_payload.iv,
                    'tag': encrypted_payload.tag,
                    'encoding': encrypted_payload.encoding,
                    'algorithm': encrypted_payload.algorithm,
                    'user_id': user_id,
                    'key': key
                }, f)
            
            print(f"🔒 Stored data for user {user_id}, key: {key}")
            return True
            
        except Exception as e:
            print(f"❌ Error storing data for user {user_id}, key {key}: {e}")
            return False
    
    def retrieve_data(self, user_id: str, key: str) -> Optional[Any]:
        """Retrieve and decrypt data from the user's vault"""
        try:
            # Get user's encryption key
            user_key = get_user_encryption_key(user_id)
            
            # Load encrypted data
            user_dir = self._get_user_vault_dir(user_id)
            file_path = user_dir / f"{key}.enc"
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r') as f:
                encrypted_data = json.load(f)
            
            # Verify this data belongs to the user
            if encrypted_data.get('user_id') != user_id:
                raise ValueError(f"Data ownership mismatch for user {user_id}")
            
            # Decrypt the data
            encrypted_payload = EncryptedPayload(
                ciphertext=encrypted_data['ciphertext'],
                iv=encrypted_data['iv'],
                tag=encrypted_data['tag'],
                encoding=encrypted_data['encoding'],
                algorithm=encrypted_data['algorithm']
            )
            
            decrypted_str = decrypt_data(encrypted_payload, user_key)
            data = json.loads(decrypted_str)
            
            print(f"🔓 Retrieved data for user {user_id}, key: {key}")
            return data
            
        except Exception as e:
            print(f"❌ Error retrieving data for user {user_id}, key {key}: {e}")
            return None
    
    def delete_data(self, user_id: str, key: str) -> bool:
        """Delete data from the user's vault"""
        try:
            user_dir = self._get_user_vault_dir(user_id)
            file_path = user_dir / f"{key}.enc"
            
            if file_path.exists():
                file_path.unlink()
                print(f"🗑️ Deleted data for user {user_id}, key: {key}")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Error deleting data for user {user_id}, key {key}: {e}")
            return False
    
    def list_user_keys(self, user_id: str) -> list[str]:
        """List all keys stored for a user"""
        try:
            user_dir = self._get_user_vault_dir(user_id)
            
            if not user_dir.exists():
                return []
            
            keys = []
            for file_path in user_dir.glob("*.enc"):
                key = file_path.stem  # filename without .enc extension
                keys.append(key)
            
            return keys
            
        except Exception as e:
            print(f"❌ Error listing keys for user {user_id}: {e}")
            return []
    
    def user_exists(self, user_id: str) -> bool:
        """Check if a user has any data in the vault"""
        user_dir = self._get_user_vault_dir(user_id)
        return user_dir.exists() and any(user_dir.glob("*.enc"))

# Global instance
user_vault = UserVault()

# Convenience functions
def store_user_data(user_id: str, key: str, data: Any) -> bool:
    """Store data for a user"""
    return user_vault.store_data(user_id, key, data)

def get_user_data(user_id: str, key: str) -> Optional[Any]:
    """Retrieve data for a user"""
    return user_vault.retrieve_data(user_id, key)

def delete_user_data(user_id: str, key: str) -> bool:
    """Delete data for a user"""
    return user_vault.delete_data(user_id, key)

def list_user_data_keys(user_id: str) -> list[str]:
    """List all data keys for a user"""
    return user_vault.list_user_keys(user_id)
