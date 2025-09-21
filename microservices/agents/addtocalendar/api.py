#!/usr/bin/env python3
"""
AddToCalendar Agent Microservice
===============================

Dedicated microservice for calendar event extraction and Google Calendar integration.
"""

import os
import sys
import json
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv('.env')
    print("✅ AddToCalendar service environment loaded")
except ImportError:
    print("⚠️ python-dotenv not installed")

# Add backend path for imports
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Initialize FastAPI app
app = FastAPI(
    title="AddToCalendar Agent API",
    description="Microservice for calendar event extraction and Google Calendar integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CalendarRequest(BaseModel):
    """Request model for calendar operations."""
    user_id: str = Field(..., description="User identifier")
    email_content: Optional[str] = Field(None, description="Email content to analyze")
    event_data: Optional[Dict[str, Any]] = Field(None, description="Event data to add")
    token: Optional[str] = Field(None, description="Authorization token")

class CalendarResponse(BaseModel):
    """Response model for calendar operations."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    service: str = "addtocalendar"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "AddToCalendar Agent",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "addtocalendar",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/extract")
async def extract_events(request: CalendarRequest):
    """Extract calendar events from email content."""
    try:
        # Import the agent here to avoid loading if not needed
        from hushh_mcp.agents.addtocalendar.index import AddToCalendarAgent
        from hushh_mcp.consent.token import validate_token
        from hushh_mcp.constants import ConsentScope
        
        # Validate token
        if request.token:
            token_validation = validate_token(
                request.token, 
                request.user_id, 
                ConsentScope.VAULT_READ_CALENDAR
            )
            if not token_validation.get("valid"):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                )
        
        # Initialize agent
        agent = AddToCalendarAgent(request.user_id)
        
        # Extract events
        result = await agent.extract_events(request.email_content)
        
        return CalendarResponse(
            success=True,
            data=result
        )
        
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Agent module not available: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Event extraction failed: {str(e)}"
        )

@app.post("/add")
async def add_event(request: CalendarRequest):
    """Add event to Google Calendar."""
    try:
        # Import the agent
        from hushh_mcp.agents.addtocalendar.index import AddToCalendarAgent
        from hushh_mcp.consent.token import validate_token
        from hushh_mcp.constants import ConsentScope
        
        # Validate token
        if request.token:
            token_validation = validate_token(
                request.token, 
                request.user_id, 
                ConsentScope.VAULT_WRITE_CALENDAR
            )
            if not token_validation.get("valid"):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                )
        
        # Initialize agent
        agent = AddToCalendarAgent(request.user_id)
        
        # Add event
        result = await agent.add_event(request.event_data)
        
        return CalendarResponse(
            success=True,
            data=result
        )
        
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Agent module not available: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Event addition failed: {str(e)}"
        )

@app.post("/analyze")
async def analyze_email(request: CalendarRequest):
    """Analyze email for calendar events."""
    try:
        # Import the agent
        from hushh_mcp.agents.addtocalendar.index import AddToCalendarAgent
        
        # Initialize agent
        agent = AddToCalendarAgent(request.user_id)
        
        # Analyze email
        result = await agent.analyze_email(request.email_content)
        
        return CalendarResponse(
            success=True,
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Email analysis failed: {str(e)}"
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )