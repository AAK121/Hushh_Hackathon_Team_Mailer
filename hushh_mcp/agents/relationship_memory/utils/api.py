"""
FastAPI routes for the Relationship Memory Agent
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime

from hushh_mcp.types import HushhConsentToken as ConsentToken
from .index import RelationshipMemoryAgent

router = APIRouter(prefix="/relationship", tags=["relationship"])

# Initialize agent
agent = RelationshipMemoryAgent()

# Request/Response Models
class MemoryCreate(BaseModel):
    contact_id: int
    summary: str
    detailed_notes: str
    sentiment: Optional[str] = None
    tags: Optional[List[str]] = None

class ReminderCreate(BaseModel):
    contact_id: int
    type: str
    title: str
    description: Optional[str] = None
    scheduled_at: datetime
    recurrence: Optional[str] = None

@router.post("/add-memory")
async def add_memory(
    memory: MemoryCreate,
    user_id: str,
    consent_tokens: Dict[str, ConsentToken]
):
    """Add a new memory for a contact"""
    try:
        result = await agent.add_memory(
            user_id=user_id,
            contact_id=memory.contact_id,
            memory_details=memory.dict(),
            consent_tokens=consent_tokens
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/contact-history/{contact_id}")
async def get_contact_history(
    contact_id: int,
    user_id: str,
    consent_tokens: Dict[str, ConsentToken]
):
    """Get complete history for a contact"""
    try:
        result = await agent.get_contact_history(
            user_id=user_id,
            contact_id=contact_id,
            consent_tokens=consent_tokens
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-reminder")
async def create_reminder(
    reminder: ReminderCreate,
    user_id: str,
    consent_tokens: Dict[str, ConsentToken]
):
    """Create a new reminder for a contact"""
    try:
        result = await agent.create_reminder(
            user_id=user_id,
            contact_id=reminder.contact_id,
            reminder_details=reminder.dict(),
            consent_tokens=consent_tokens
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
