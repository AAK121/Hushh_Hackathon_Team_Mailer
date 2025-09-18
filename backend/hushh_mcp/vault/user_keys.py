"""
User-specific Encryption Key Management for HushMCP Vault
=======================================================

This module handles generating, storing, and retrieving unique encryption keys
for each user, ensuring data isolation and security.
"""

import os
import json
import secrets
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from hushh_mcp.vault.encrypt import encrypt_data, decrypt_data
from hushh_mcp.types import EncryptedPayload

class UserKeyManager:
    """Manages user-specific encryption keys for vault data"""
    
    def __init__(self, vault_root: str = "vault"):
        self.vault_root = Path(vault_root)
        self.keys_dir = self.vault_root / "user_keys"
        self.keys_dir.mkdir(parents=True, exist_ok=True)
        
        # Master key for encrypting user keys (from environment)
        self.master_key = self._get_or_create_master_key()
    
    def _get_or_create_master_key(self) -> str:
        """Get or create the master encryption key"""
        master_key = os.getenv("VAULT_MASTER_KEY")
        if not master_key or len(master_key) != 64:
            # Generate a temporary key for serverless environments
            if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
                print("🔧 Generating temporary VAULT_MASTER_KEY for Vercel")
                master_key = secrets.token_hex(32)  # 64-character hex string
            else:
                raise ValueError("❌ VAULT_MASTER_KEY must be a 64-character hex string")
        return master_key
    
    def _derive_user_key_filename(self, user_id: str) -> str:
        """Create a deterministic filename for user keys"""
        # Hash the user_id to create a consistent filename
        user_hash = hashlib.sha256(user_id.encode()).hexdigest()[:16]
        return f"user_{user_hash}.key"
    
    def get_user_key(self, user_id: str) -> str:
        """Get or create a user-specific encryption key"""
        key_filename = self._derive_user_key_filename(user_id)
        key_path = self.keys_dir / key_filename
        
        try:
            if key_path.exists():
                # Load existing key
                with open(key_path, 'r') as f:
                    encrypted_key_data = json.load(f)
                
                # Decrypt the user key using master key
                encrypted_payload = EncryptedPayload(**encrypted_key_data)
                user_key = decrypt_data(encrypted_payload, self.master_key)
                return user_key
            else:
                # Generate new key for user
                user_key = secrets.token_hex(32)  # 64-character hex string
                
                # Encrypt the user key with master key
                encrypted_payload = encrypt_data(user_key, self.master_key)
                
                # Save encrypted key
                with open(key_path, 'w') as f:
                    json.dump({
                        'ciphertext': encrypted_payload.ciphertext,
                        'iv': encrypted_payload.iv,
                        'tag': encrypted_payload.tag,
                        'encoding': encrypted_payload.encoding,
                        'algorithm': encrypted_payload.algorithm
                    }, f)
                
                print(f"🔑 Generated new encryption key for user: {user_id}")
                return user_key
                
        except Exception as e:
            print(f"❌ Error managing user key for {user_id}: {e}")
            # No fallback - proper error handling required
            raise ValueError(f"Failed to generate user key for {user_id}: {e}")
    
    def rotate_user_key(self, user_id: str) -> str:
        """Generate a new key for a user (for security rotation)"""
        key_filename = self._derive_user_key_filename(user_id)
        key_path = self.keys_dir / key_filename
        
        # Remove old key
        if key_path.exists():
            key_path.unlink()
        
        # Generate new key
        return self.get_user_key(user_id)
    
    def delete_user_key(self, user_id: str) -> bool:
        """Delete a user's encryption key (for account deletion)"""
        key_filename = self._derive_user_key_filename(user_id)
        key_path = self.keys_dir / key_filename
        
        try:
            if key_path.exists():
                key_path.unlink()
                print(f"🗑️ Deleted encryption key for user: {user_id}")
                return True
            return False
        except Exception as e:
            print(f"❌ Error deleting user key for {user_id}: {e}")
            return False

# Global instance
user_key_manager = UserKeyManager()

def get_user_encryption_key(user_id: str) -> str:
    """Convenience function to get a user's encryption key"""
    return user_key_manager.get_user_key(user_id)

def rotate_user_encryption_key(user_id: str) -> str:
    """Convenience function to rotate a user's encryption key"""
    return user_key_manager.rotate_user_key(user_id)
