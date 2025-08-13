"""
Relationship Memory Agent Implementation
Handles core agent logic, memory management, and reminder generation
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from hushh_mcp.types import HushhConsentToken as ConsentToken, TrustLink, VaultKey
from hushh_mcp.vault.encrypt import encrypt_data, decrypt_data
from hushh_mcp.trust.link import create_trust_link, validate_trust_link

from .models import Contact, RelationshipMemory, Reminder
from .memory_manager import MemoryManager
from .scheduler import ReminderEngine
from .db import get_session
from .vector_store import VectorStore

logger = logging.getLogger(__name__)

class RelationshipMemoryAgent:
    """Main agent class for relationship memory management"""
    
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.reminder_engine = ReminderEngine()
        self.vector_store = VectorStore()
    
    async def add_memory(
        self,
        user_id: str,
        contact_id: int,
        memory_details: Dict,
        consent_tokens: Dict[str, ConsentToken]
    ) -> Dict:
        """Add a new memory for a contact"""
        
        # Validate required consent tokens
        self._validate_consent_for_operation(
            consent_tokens,
            ["VAULT_WRITE_MEMORY", "VAULT_READ_CONTACT"]
        )
        
        try:
            # Get DB session
            session = get_session()
            
            # Create memory embedding
            embedding_id = await self.vector_store.create_embedding(
                memory_details["detailed_notes"]
            )
            
            # Create memory record
            memory = RelationshipMemory(
                user_id=user_id,
                contact_id=contact_id,
                summary=memory_details["summary"],
                detailed_notes=memory_details["detailed_notes"],
                embedding_id=embedding_id,
                sentiment=memory_details.get("sentiment"),
                tags=memory_details.get("tags", [])
            )
            
            # Store in database
            session.add(memory)
            session.commit()
            
            # Generate reminders if needed
            await self.reminder_engine.process_memory(memory)
            
            return {
                "status": "success",
                "memory_id": memory.id,
                "reminders_created": True
            }
            
        except Exception as e:
            logger.error(f"Error adding memory: {str(e)}")
            raise
    
    async def get_contact_history(
        self,
        user_id: str,
        contact_id: int,
        consent_tokens: Dict[str, ConsentToken]
    ) -> Dict:
        """Get complete history for a contact"""
        
        # Validate consent
        self._validate_consent_for_operation(
            consent_tokens,
            ["VAULT_READ_MEMORY", "VAULT_READ_CONTACT"]
        )
        
        try:
            session = get_session()
            
            # Get all memories
            memories = session.query(RelationshipMemory).filter_by(
                user_id=user_id,
                contact_id=contact_id
            ).all()
            
            # Get active reminders
            reminders = session.query(Reminder).filter_by(
                user_id=user_id,
                contact_id=contact_id,
                status='pending'
            ).all()
            
            return {
                "memories": [self._format_memory(m) for m in memories],
                "reminders": [self._format_reminder(r) for r in reminders],
                "summary": await self._generate_relationship_summary(memories)
            }
            
        except Exception as e:
            logger.error(f"Error getting contact history: {str(e)}")
            raise
    
    async def create_reminder(
        self,
        user_id: str,
        contact_id: int,
        reminder_details: Dict,
        consent_tokens: Dict[str, ConsentToken]
    ) -> Dict:
        """Create a new reminder for a contact"""
        
        self._validate_consent_for_operation(
            consent_tokens,
            ["VAULT_WRITE_REMINDER"]
        )
        
        try:
            session = get_session()
            
            reminder = Reminder(
                user_id=user_id,
                contact_id=contact_id,
                type=reminder_details["type"],
                title=reminder_details["title"],
                description=reminder_details.get("description"),
                scheduled_at=reminder_details["scheduled_at"],
                recurrence=reminder_details.get("recurrence")
            )
            
            session.add(reminder)
            session.commit()
            
            return {
                "status": "success",
                "reminder_id": reminder.id
            }
            
        except Exception as e:
            logger.error(f"Error creating reminder: {str(e)}")
            raise
    
    def _validate_consent_for_operation(
        self,
        consent_tokens: Dict[str, ConsentToken],
        required_scopes: List[str]
    ) -> None:
        """Validate that all required consent scopes are present"""
        current_time = int(datetime.utcnow().timestamp() * 1000)  # Convert to epoch ms
        for scope in required_scopes:
            if scope not in consent_tokens:
                raise ValueError(f"Missing required consent scope: {scope}")
            token = consent_tokens[scope]
            if current_time > token.expires_at:
                raise ValueError(f"Expired consent token for scope: {scope}")
    
    def _format_memory(self, memory: RelationshipMemory) -> Dict:
        """Format a memory record for API response"""
        return {
            "id": memory.id,
            "summary": memory.summary,
            "detailed_notes": memory.detailed_notes,
            "sentiment": memory.sentiment,
            "tags": memory.tags,
            "created_at": memory.created_at.isoformat()
        }
    
    def _format_reminder(self, reminder: Reminder) -> Dict:
        """Format a reminder record for API response"""
        return {
            "id": reminder.id,
            "type": reminder.type,
            "title": reminder.title,
            "description": reminder.description,
            "scheduled_at": reminder.scheduled_at.isoformat(),
            "recurrence": reminder.recurrence,
            "status": reminder.status
        }
    
    async def _generate_relationship_summary(
        self,
        memories: List[RelationshipMemory]
    ) -> str:
        """Generate a summary of the relationship based on memories"""
        # TODO: Implement LLM-based summary generation
        return "Relationship summary pending implementation"
