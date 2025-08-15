"""
Vault Manager for Relationship Memory Agent
Handles persistent storage of contacts, memories, and reminders using Hushh MCP vault system
"""

import json
import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path

from hushh_mcp.vault.encrypt import encrypt_data, decrypt_data
from hushh_mcp.types import VaultKey, VaultRecord, EncryptedPayload, UserID, AgentID, ConsentScope


class VaultManager:
    """Manages encrypted storage for relationship memory data"""
    
    def __init__(self, user_id: str, vault_key: str, db_path: Optional[str] = None):
        self.user_id = UserID(user_id)
        self.agent_id = AgentID("relationship_memory")
        self.vault_key = vault_key
        
        # Initialize database
        if db_path is None:
            db_dir = Path(__file__).parent / "data"
            db_dir.mkdir(exist_ok=True)
            self.db_path = db_dir / f"relationship_memory_{user_id}.db"
        else:
            self.db_path = Path(db_path)
        
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for vault records"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vault_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_type TEXT NOT NULL,
                    record_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    ciphertext TEXT NOT NULL,
                    iv TEXT NOT NULL,
                    tag TEXT NOT NULL,
                    encoding TEXT NOT NULL,
                    algorithm TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER,
                    expires_at INTEGER,
                    deleted BOOLEAN DEFAULT FALSE,
                    metadata TEXT,
                    UNIQUE(record_type, record_id, user_id)
                )
            """)
            conn.commit()
    
    def _create_vault_key(self, scope: ConsentScope) -> VaultKey:
        """Create a vault key for the given scope"""
        return VaultKey(user_id=self.user_id, scope=scope)
    
    def _store_record(self, record_type: str, record_id: str, data: Dict, scope: ConsentScope) -> VaultRecord:
        """Store encrypted data in the vault"""
        encrypted = encrypt_data(json.dumps(data), self.vault_key)
        timestamp = int(datetime.now().timestamp() * 1000)
        
        vault_key = self._create_vault_key(scope)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO vault_records 
                (record_type, record_id, user_id, agent_id, scope, ciphertext, iv, tag, 
                 encoding, algorithm, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record_type, record_id, str(self.user_id), str(self.agent_id), scope.value,
                encrypted.ciphertext, encrypted.iv, encrypted.tag, encrypted.encoding, 
                encrypted.algorithm, timestamp, timestamp
            ))
            conn.commit()
        
        return VaultRecord(
            key=vault_key,
            data=encrypted,
            agent_id=self.agent_id,
            created_at=timestamp,
            updated_at=timestamp
        )
    
    def _retrieve_record(self, record_type: str, record_id: str, scope: ConsentScope) -> Optional[Dict]:
        """Retrieve and decrypt data from the vault"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT ciphertext, iv, tag, encoding, algorithm
                FROM vault_records
                WHERE record_type = ? AND record_id = ? AND user_id = ? AND scope = ? AND deleted = FALSE
            """, (record_type, record_id, str(self.user_id), scope.value))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            encrypted = EncryptedPayload(
                ciphertext=row[0],
                iv=row[1],
                tag=row[2],
                encoding=row[3],
                algorithm=row[4]
            )
            
            decrypted = decrypt_data(encrypted, self.vault_key)
            return json.loads(decrypted)
    
    def _retrieve_all_records(self, record_type: str, scope: ConsentScope) -> List[Dict]:
        """Retrieve all records of a given type"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT record_id, ciphertext, iv, tag, encoding, algorithm, created_at
                FROM vault_records
                WHERE record_type = ? AND user_id = ? AND scope = ? AND deleted = FALSE
                ORDER BY created_at DESC
            """, (record_type, str(self.user_id), scope.value))
            
            records = []
            for row in cursor.fetchall():
                encrypted = EncryptedPayload(
                    ciphertext=row[1],
                    iv=row[2],
                    tag=row[3],
                    encoding=row[4],
                    algorithm=row[5]
                )
                
                try:
                    decrypted = decrypt_data(encrypted, self.vault_key)
                    data = json.loads(decrypted)
                    data['_vault_id'] = row[0]
                    data['_created_at'] = row[6]
                    records.append(data)
                except Exception as e:
                    print(f"Warning: Failed to decrypt record {row[0]}: {e}")
                    continue
            
            return records
    
    def _delete_record(self, record_type: str, record_id: str, scope: ConsentScope) -> bool:
        """Mark a record as deleted (soft delete)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE vault_records 
                SET deleted = TRUE, updated_at = ?
                WHERE record_type = ? AND record_id = ? AND user_id = ? AND scope = ?
            """, (
                int(datetime.now().timestamp() * 1000),
                record_type, record_id, str(self.user_id), scope.value
            ))
            conn.commit()
            return cursor.rowcount > 0
    
    # Contact Management
    def store_contact(self, contact_data: Dict) -> VaultRecord:
        """Store a contact in the vault"""
        contact_id = contact_data.get('id', contact_data['name'].lower().replace(' ', '_'))
        return self._store_record('contact', contact_id, contact_data, ConsentScope.VAULT_WRITE_CONTACTS)
    
    def get_contact(self, contact_id: str) -> Optional[Dict]:
        """Retrieve a specific contact"""
        return self._retrieve_record('contact', contact_id, ConsentScope.VAULT_READ_CONTACTS)
    
    def get_all_contacts(self) -> List[Dict]:
        """Retrieve all contacts"""
        return self._retrieve_all_records('contact', ConsentScope.VAULT_READ_CONTACTS)
    
    def delete_contact(self, contact_id: str) -> bool:
        """Delete a contact"""
        return self._delete_record('contact', contact_id, ConsentScope.VAULT_WRITE_CONTACTS)
    
    # Memory Management
    def store_memory(self, memory_data: Dict) -> VaultRecord:
        """Store a memory in the vault"""
        memory_id = memory_data.get('id', f"memory_{int(datetime.now().timestamp())}")
        return self._store_record('memory', memory_id, memory_data, ConsentScope.VAULT_WRITE_MEMORY)
    
    def get_memories_for_contact(self, contact_name: str) -> List[Dict]:
        """Retrieve all memories for a specific contact"""
        all_memories = self._retrieve_all_records('memory', ConsentScope.VAULT_READ_MEMORY)
        return [m for m in all_memories if m.get('contact_name', '').lower() == contact_name.lower()]
    
    def get_all_memories(self) -> List[Dict]:
        """Retrieve all memories"""
        return self._retrieve_all_records('memory', ConsentScope.VAULT_READ_MEMORY)
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory"""
        return self._delete_record('memory', memory_id, ConsentScope.VAULT_WRITE_MEMORY)
    
    # Reminder Management
    def store_reminder(self, reminder_data: Dict) -> VaultRecord:
        """Store a reminder in the vault"""
        reminder_id = reminder_data.get('id', f"reminder_{int(datetime.now().timestamp())}")
        return self._store_record('reminder', reminder_id, reminder_data, ConsentScope.VAULT_WRITE_REMINDER)
    
    def get_reminders_for_contact(self, contact_name: str) -> List[Dict]:
        """Retrieve all reminders for a specific contact"""
        all_reminders = self._retrieve_all_records('reminder', ConsentScope.VAULT_READ_REMINDER)
        return [r for r in all_reminders if r.get('contact_name', '').lower() == contact_name.lower()]
    
    def get_all_reminders(self) -> List[Dict]:
        """Retrieve all reminders"""
        return self._retrieve_all_records('reminder', ConsentScope.VAULT_READ_REMINDER)
    
    def delete_reminder(self, reminder_id: str) -> bool:
        """Delete a reminder"""
        return self._delete_record('reminder', reminder_id, ConsentScope.VAULT_WRITE_REMINDER)
    
    # Search and Query Methods
    def search_contacts(self, query: str) -> List[Dict]:
        """Search contacts by name or details"""
        all_contacts = self.get_all_contacts()
        query_lower = query.lower()
        
        results = []
        for contact in all_contacts:
            # Search in name
            if query_lower in contact.get('name', '').lower():
                results.append(contact)
                continue
            
            # Search in details
            details = contact.get('details', {})
            for value in details.values():
                if isinstance(value, str) and query_lower in value.lower():
                    results.append(contact)
                    break
        
        return results
    
    def search_memories(self, query: str) -> List[Dict]:
        """Search memories by content"""
        all_memories = self.get_all_memories()
        query_lower = query.lower()
        
        return [
            memory for memory in all_memories
            if query_lower in memory.get('summary', '').lower() or
               query_lower in memory.get('contact_name', '').lower()
        ]
