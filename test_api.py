#!/usr/bin/env python3
"""
HushMCP Agent API Test Server
============================

A simplified version of the API for testing without full environment setup.
"""

import os
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Mock the missing modules for testing
class MockAgent:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id

class MockRegistry:
    def __init__(self):
        self.agents = {
            "addtocalendar": MockAgent("addtocalendar"),
            "mailerpanda": MockAgent("mailerpanda")
        }
    
    def list_agents(self):
        return [
            {
                "id": "addtocalendar",
                "name": "AddToCalendar Agent", 
                "description": "Extracts events from emails and adds them to calendar",
                "version": "1.0.0",
                "required_scopes": ["VAULT_READ_EMAIL", "VAULT_WRITE_CALENDAR"],
                "status": "active"
            },
            {
                "id": "mailerpanda",
                "name": "MailerPanda Agent",
                "description": "AI-powered mass email agent with human approval", 
                "version": "1.0.0",
                "required_scopes": ["VAULT_WRITE_EMAIL"],
                "status": "active"
            }
        ]

# Initialize FastAPI app
app = FastAPI(
    title="HushMCP Agent API (Test Mode)",
    description="Privacy-first AI agent orchestration platform - Test Server",
    version="1.0.0-test",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock registry
registry = MockRegistry()

# Pydantic models
class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    agents_available: int
    version: str
    mode: str = "test"

class AgentInfo(BaseModel):
    id: str
    name: str
    description: str
    version: str
    required_scopes: List[str]
    status: str

class ConsentTokenRequest(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    scopes: List[str] = Field(..., description="List of consent scopes")
    duration_hours: int = Field(default=24, description="Token validity duration in hours")

class ConsentTokenResponse(BaseModel):
    token: str = Field(..., description="Generated consent token")
    expires_at: datetime = Field(..., description="Token expiration timestamp")
    scopes: List[str] = Field(..., description="Granted scopes")

class AgentRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    agent_id: str = Field(..., description="Agent identifier")
    consent_tokens: Dict[str, str] = Field(..., description="Required consent tokens")
    parameters: Dict[str, Any] = Field(default={}, description="Agent-specific parameters")

class AgentResponse(BaseModel):
    status: str = Field(..., description="Request status")
    agent_id: str = Field(..., description="Agent that processed the request")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
    error: Optional[str] = Field(default=None, description="Error message if any")

# API endpoints
@app.get("/", response_model=HealthCheckResponse)
async def root():
    """Health check and API info endpoint."""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        agents_available=len(registry.agents),
        version="1.0.0-test",
        mode="test"
    )

@app.get("/agents", response_model=List[AgentInfo])
async def list_agents():
    """List all available agents and their capabilities."""
    agents = registry.list_agents()
    return [AgentInfo(**agent) for agent in agents]

@app.get("/agents/{agent_id}", response_model=AgentInfo)
async def get_agent_info(agent_id: str):
    """Get detailed information about a specific agent."""
    agents = registry.list_agents()
    agent = next((a for a in agents if a["id"] == agent_id), None)
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' not found"
        )
    
    return AgentInfo(**agent)

@app.post("/consent/token", response_model=ConsentTokenResponse)
async def generate_consent_token(request: ConsentTokenRequest):
    """Generate a mock consent token for testing."""
    # Generate a mock token
    mock_token = f"mock_token_{request.user_id}_{datetime.utcnow().timestamp()}"
    expires_at = datetime.utcnow().replace(hour=23, minute=59, second=59)
    
    return ConsentTokenResponse(
        token=mock_token,
        expires_at=expires_at,
        scopes=request.scopes
    )

@app.post("/agents/{agent_id}/execute", response_model=AgentResponse)
async def execute_agent(agent_id: str, request: AgentRequest):
    """Execute an agent (mock implementation for testing)."""
    
    if agent_id not in registry.agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' not found"
        )
    
    if request.agent_id != agent_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent ID in request body must match URL parameter"
        )
    
    # Mock responses based on agent type
    if agent_id == "addtocalendar":
        mock_data = {
            "status": "complete",
            "events_created": 2,
            "links": [
                "https://calendar.google.com/event?eid=mock_event_1",
                "https://calendar.google.com/event?eid=mock_event_2"
            ],
            "note": "This is a mock response - no actual calendar events were created"
        }
    elif agent_id == "mailerpanda":
        mock_data = {
            "status": "draft_created",
            "email_template": "Mock AI-generated email content",
            "subject": "Mock Subject Line",
            "recipients_count": len(request.parameters.get("receiver_emails", [])),
            "note": "This is a mock response - no actual emails were sent"
        }
    else:
        mock_data = {
            "status": "executed",
            "note": f"Mock execution of {agent_id} agent"
        }
    
    return AgentResponse(
        status="success",
        agent_id=agent_id,
        data=mock_data
    )

@app.post("/agents/addtocalendar/process-emails")
async def process_emails_to_calendar(
    user_id: str,
    email_token: str,
    calendar_token: str
):
    """Mock endpoint for AddToCalendar agent."""
    return AgentResponse(
        status="success",
        agent_id="addtocalendar",
        data={
            "status": "complete",
            "events_processed": 3,
            "events_created": 2,
            "note": "Mock response - no actual processing performed"
        }
    )

@app.post("/agents/mailerpanda/draft")
async def draft_email_content(
    user_input: str,
    user_email: str,
    consent_token: str,
    receiver_emails: Optional[List[str]] = None,
    mass_email: bool = False
):
    """Mock endpoint for MailerPanda email drafting."""
    return AgentResponse(
        status="success",
        agent_id="mailerpanda",
        data={
            "status": "draft_ready",
            "subject": f"RE: {user_input}",
            "email_template": f"Mock AI response to: {user_input}",
            "recipient_count": len(receiver_emails) if receiver_emails else 0,
            "mass_email": mass_email,
            "note": "Mock response - no actual AI generation performed"
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.on_event("startup")
async def startup_event():
    """Initialize the test API server."""
    print("🧪 Starting HushMCP Agent API Test Server")
    print(f"📋 Mock agents available: {len(registry.agents)}")
    print("⚠️  This is a test server - no real agent operations will be performed")

if __name__ == "__main__":
    print("🎮 HushMCP Agent API Test Server")
    print("=" * 50)
    print("🧪 Running in TEST MODE")
    print("⚠️  No real agent operations will be performed")
    print("🌐 Server URL: http://127.0.0.1:8001")
    print("📚 API Docs: http://127.0.0.1:8001/docs")
    print("=" * 50)
    
    uvicorn.run(
        "test_api:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )
