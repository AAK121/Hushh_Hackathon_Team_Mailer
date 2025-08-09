#!/usr/bin/env python3
"""
HushMCP Agent API Server
=======================

A comprehensive FastAPI-based REST API server for interacting with HushMCP agents.
Supports AddToCalendar and MailerPanda agents with proper input validation,
consent management, and human-in-the-loop workflows.
"""

import os
import sys
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import uvicorn

# Add the project root to Python path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# HushMCP framework imports
from hushh_mcp.consent.token import validate_token, issue_token
from hushh_mcp.constants import ConsentScope

# Initialize FastAPI app
app = FastAPI(
    title="HushMCP Agent API",
    description="Privacy-first AI agent orchestration platform supporting AddToCalendar and MailerPanda agents",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# PYDANTIC MODELS FOR REQUEST/RESPONSE VALIDATION
# ============================================================================

class ConsentTokenRequest(BaseModel):
    """Request model for creating consent tokens."""
    user_id: str = Field(..., description="User identifier")
    agent_id: str = Field(..., description="Target agent ID")
    scope: str = Field(..., description="Consent scope")
    
class ConsentTokenResponse(BaseModel):
    """Response model for consent token creation."""
    token: str = Field(..., description="Generated consent token")
    expires_at: int = Field(..., description="Token expiration timestamp")
    scope: str = Field(..., description="Token scope")

class AgentStatusResponse(BaseModel):
    """Response model for agent status."""
    agent_id: str
    name: str
    version: str
    status: str
    required_scopes: List[str]
    required_inputs: Dict[str, Any]

# ============================================================================
# ADDTOCALENDAR AGENT MODELS
# ============================================================================

class AddToCalendarRequest(BaseModel):
    """Request model for AddToCalendar agent."""
    user_id: str = Field(..., description="User identifier")
    email_token: str = Field(..., description="Consent token for email access")
    calendar_token: str = Field(..., description="Consent token for calendar access")
    google_access_token: str = Field(..., description="Google OAuth access token")
    action: str = Field(default="comprehensive_analysis", description="Action to perform")
    
    # Optional parameters for different actions
    manual_event: Optional[Dict[str, Any]] = Field(None, description="Manual event data for manual_event action")
    confidence_threshold: Optional[float] = Field(0.7, description="Minimum confidence for event extraction")
    max_emails: Optional[int] = Field(50, description="Maximum emails to process")
    
    @validator('action')
    def validate_action(cls, v):
        allowed_actions = ["comprehensive_analysis", "manual_event", "analyze_only"]
        if v not in allowed_actions:
            raise ValueError(f"Action must be one of: {allowed_actions}")
        return v

class AddToCalendarResponse(BaseModel):
    """Response model for AddToCalendar agent."""
    status: str = Field(..., description="Operation status")
    user_id: str = Field(..., description="User identifier")
    action_performed: str = Field(..., description="Action that was performed")
    
    # Email processing results
    emails_processed: Optional[int] = Field(None, description="Number of emails processed")
    events_extracted: Optional[int] = Field(None, description="Number of events extracted")
    events_created: Optional[int] = Field(None, description="Number of calendar events created")
    
    # Calendar links and results
    calendar_links: Optional[List[str]] = Field(None, description="Links to created calendar events")
    extracted_events: Optional[List[Dict[str, Any]]] = Field(None, description="Extracted event details")
    
    # Error and processing info
    errors: Optional[List[str]] = Field(None, description="Any errors encountered")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    trust_links: Optional[List[str]] = Field(None, description="Created trust links for delegation")

# ============================================================================
# MAILERPANDA AGENT MODELS
# ============================================================================

class MailerPandaRequest(BaseModel):
    """Request model for MailerPanda agent."""
    user_id: str = Field(..., description="User identifier")
    user_input: str = Field(..., description="Email campaign description")
    mode: str = Field(default="interactive", description="Execution mode")
    
    # Consent tokens for different operations
    consent_tokens: Dict[str, str] = Field(..., description="Consent tokens for various scopes")
    
    # Email configuration
    sender_email: Optional[str] = Field(None, description="Sender email address")
    recipient_emails: Optional[List[str]] = Field(None, description="List of recipient emails")
    
    # Campaign settings
    require_approval: Optional[bool] = Field(True, description="Whether to require human approval")
    use_ai_generation: Optional[bool] = Field(True, description="Whether to use AI for content generation")
    
    @validator('mode')
    def validate_mode(cls, v):
        allowed_modes = ["interactive", "headless", "demo"]
        if v not in allowed_modes:
            raise ValueError(f"Mode must be one of: {allowed_modes}")
        return v

class MailerPandaResponse(BaseModel):
    """Response model for MailerPanda agent."""
    status: str = Field(..., description="Operation status")
    user_id: str = Field(..., description="User identifier")
    mode: str = Field(..., description="Execution mode used")
    
    # Campaign results
    campaign_id: Optional[str] = Field(None, description="Generated campaign ID")
    email_template: Optional[Dict[str, str]] = Field(None, description="Generated email template")
    
    # Human-in-the-loop
    requires_approval: Optional[bool] = Field(None, description="Whether campaign requires approval")
    approval_status: Optional[str] = Field(None, description="Current approval status")
    feedback_required: Optional[bool] = Field(None, description="Whether feedback is needed")
    
    # Email sending results
    emails_sent: Optional[int] = Field(None, description="Number of emails sent")
    send_status: Optional[List[Dict[str, Any]]] = Field(None, description="Individual email send status")
    
    # Vault and trust links
    vault_storage_key: Optional[str] = Field(None, description="Vault storage key for campaign data")
    trust_links: Optional[List[str]] = Field(None, description="Created trust links")
    
    # Error and processing info
    errors: Optional[List[str]] = Field(None, description="Any errors encountered")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")

class MailerPandaApprovalRequest(BaseModel):
    """Request model for MailerPanda approval workflow."""
    user_id: str = Field(..., description="User identifier")
    campaign_id: str = Field(..., description="Campaign ID")
    action: str = Field(..., description="Approval action")
    feedback: Optional[str] = Field(None, description="User feedback for modifications")
    
    @validator('action')
    def validate_action(cls, v):
        allowed_actions = ["approve", "reject", "modify", "regenerate"]
        if v not in allowed_actions:
            raise ValueError(f"Action must be one of: {allowed_actions}")
        return v

# ============================================================================
# GLOBAL VARIABLES FOR SESSION MANAGEMENT
# ============================================================================

# Store active agent sessions for human-in-the-loop workflows
active_sessions = {}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_agent_requirements(agent_id: str) -> Dict[str, Any]:
    """Get input requirements for a specific agent."""
    if agent_id == "agent_addtocalendar":
        return {
            "required_tokens": ["email_token", "calendar_token"],
            "required_scopes": ["vault.read.email", "vault.write.calendar"],
            "additional_requirements": {
                "google_access_token": "Google OAuth access token for calendar API",
                "action": "Action to perform (comprehensive_analysis, manual_event, analyze_only)"
            },
            "optional_parameters": {
                "confidence_threshold": "Minimum confidence for event extraction (default: 0.7)",
                "max_emails": "Maximum emails to process (default: 50)",
                "manual_event": "Manual event data for manual_event action"
            }
        }
    elif agent_id == "agent_mailerpanda":
        return {
            "required_tokens": ["consent_tokens (dict)"],
            "required_scopes": [
                "vault.read.email", "vault.write.email", 
                "vault.read.file", "vault.write.file", "custom.temporary"
            ],
            "additional_requirements": {
                "user_input": "Email campaign description",
                "mode": "Execution mode (interactive, headless, demo)"
            },
            "optional_parameters": {
                "sender_email": "Sender email address",
                "recipient_emails": "List of recipient emails",
                "require_approval": "Whether to require human approval (default: True)",
                "use_ai_generation": "Whether to use AI for content generation (default: True)"
            }
        }
    else:
        return {"error": "Unknown agent"}

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with API information."""
    return {
        "service": "HushMCP Agent API",
        "version": "2.0.0",
        "supported_agents": ["agent_addtocalendar", "agent_mailerpanda"],
        "documentation": "/docs",
        "status": "operational",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/agents", response_model=Dict[str, Any])
async def list_agents():
    """List all available agents and their requirements."""
    agents = {}
    
    # AddToCalendar agent info
    agents["agent_addtocalendar"] = {
        "name": "AddToCalendar Agent",
        "version": "1.1.0",
        "description": "AI-powered calendar event extraction from emails",
        "status": "available",
        "requirements": get_agent_requirements("agent_addtocalendar"),
        "endpoints": {
            "execute": "/agents/addtocalendar/execute",
            "status": "/agents/addtocalendar/status"
        }
    }
    
    # MailerPanda agent info
    agents["agent_mailerpanda"] = {
        "name": "MailerPanda Agent", 
        "version": "3.0.0",
        "description": "AI-powered mass mailer with human-in-the-loop approval",
        "status": "available",
        "requirements": get_agent_requirements("agent_mailerpanda"),
        "endpoints": {
            "execute": "/agents/mailerpanda/execute",
            "approve": "/agents/mailerpanda/approve",
            "status": "/agents/mailerpanda/status"
        }
    }
    
    return {"agents": agents, "total_agents": len(agents)}

@app.get("/agents/{agent_id}/requirements", response_model=Dict[str, Any])
async def get_agent_requirements_endpoint(agent_id: str):
    """Get detailed input requirements for a specific agent."""
    requirements = get_agent_requirements(agent_id)
    if "error" in requirements:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    return {
        "agent_id": agent_id,
        "requirements": requirements,
        "example_request": f"See /docs for detailed request examples for {agent_id}"
    }

# ============================================================================
# CONSENT TOKEN ENDPOINTS
# ============================================================================

@app.post("/consent/token", response_model=ConsentTokenResponse)
async def create_consent_token(request: ConsentTokenRequest):
    """Create a consent token for agent operations."""
    try:
        # Convert scope string to ConsentScope enum
        scope_enum = getattr(ConsentScope, request.scope.replace(".", "_").upper(), None)
        if not scope_enum:
            raise HTTPException(status_code=400, detail=f"Invalid scope: {request.scope}")
        
        token = issue_token(
            user_id=request.user_id,
            agent_id=request.agent_id,
            scope=scope_enum
        )
        
        return ConsentTokenResponse(
            token=token.token,
            expires_at=token.expires_at,
            scope=request.scope
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create token: {str(e)}")

@app.post("/consent/validate")
async def validate_consent_token(token: str, scope: str, user_id: str):
    """Validate a consent token."""
    try:
        scope_enum = getattr(ConsentScope, scope.replace(".", "_").upper(), None)
        if not scope_enum:
            raise HTTPException(status_code=400, detail=f"Invalid scope: {scope}")
        
        is_valid, reason, parsed_token = validate_token(token, expected_scope=scope_enum)
        
        return {
            "valid": is_valid,
            "reason": reason,
            "user_id_match": parsed_token.user_id == user_id if parsed_token else False,
            "expires_at": parsed_token.expires_at if parsed_token else None
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation failed: {str(e)}")

# ============================================================================
# ADDTOCALENDAR AGENT ENDPOINTS
# ============================================================================

@app.post("/agents/addtocalendar/execute", response_model=AddToCalendarResponse)
async def execute_addtocalendar_agent(request: AddToCalendarRequest):
    """Execute AddToCalendar agent with email processing and calendar creation."""
    start_time = datetime.now(timezone.utc)
    
    try:
        # Import the agent
        from hushh_mcp.agents.addtocalendar.index import AddToCalendarAgent
        
        # Initialize agent
        agent = AddToCalendarAgent()
        
        # Execute agent
        result = agent.handle(
            user_id=request.user_id,
            email_token_str=request.email_token,
            calendar_token_str=request.calendar_token,
            google_access_token=request.google_access_token,
            action=request.action,
            manual_event=request.manual_event,
            confidence_threshold=request.confidence_threshold,
            max_emails=request.max_emails
        )
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        

        if (True):
            analysis_summary = result.get("analysis_summary", 0)
        
        # Format response
            response = AddToCalendarResponse(
                status="success",
                user_id=request.user_id,
                action_performed=request.action,
                emails_processed=analysis_summary.get("emails_processed", 0),
                events_extracted=analysis_summary.get("events_extracted", 0),
                events_created=analysis_summary.get("events_created", 0),
                calendar_links=analysis_summary.get("calendar_links", []),
                extracted_events=analysis_summary.get("extracted_events", []),
                errors=analysis_summary.get("errors", []),
                processing_time=processing_time,
                trust_links=result.get("trust_links", [])
            )
        
        print(response.status)
        
        return response
        
    except Exception as e:
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        return AddToCalendarResponse(
            status="error",
            user_id=request.user_id,
            action_performed=request.action,
            errors=[str(e)],
            processing_time=processing_time
        )

@app.get("/agents/addtocalendar/status", response_model=AgentStatusResponse)
async def get_addtocalendar_status():
    """Get AddToCalendar agent status and requirements."""
    return AgentStatusResponse(
        agent_id="agent_addtocalendar",
        name="AddToCalendar Agent",
        version="1.1.0",
        status="available",
        required_scopes=["vault.read.email", "vault.write.calendar"],
        required_inputs={
            "user_id": "User identifier",
            "email_token": "Consent token for email access",
            "calendar_token": "Consent token for calendar access", 
            "google_access_token": "Google OAuth access token",
            "action": "Action to perform (comprehensive_analysis, manual_event, analyze_only)"
        }
    )

# ============================================================================
# MAILERPANDA AGENT ENDPOINTS
# ============================================================================

@app.post("/agents/mailerpanda/execute", response_model=MailerPandaResponse)
async def execute_mailerpanda_agent(request: MailerPandaRequest):
    """Execute MailerPanda agent with AI content generation and email sending."""
    start_time = datetime.now(timezone.utc)
    session_id = f"{request.user_id}_{int(start_time.timestamp())}"
    
    try:
        # Import the agent
        from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
        
        # Initialize agent
        agent = MassMailerAgent()
        
        # Store session for potential human-in-the-loop workflows
        active_sessions[session_id] = {
            "agent": agent,
            "request": request,
            "start_time": start_time,
            "status": "executing"
        }
        
        # Execute agent
        result = agent.handle(
            user_id=request.user_id,
            consent_tokens=request.consent_tokens,
            user_input=request.user_input,
            mode=request.mode
        )
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        # Check if human approval is required
        requires_approval = result.get("requires_approval", False)
        
        if requires_approval and request.mode == "interactive":
            # Store session for approval workflow
            active_sessions[session_id]["status"] = "awaiting_approval"
            active_sessions[session_id]["result"] = result
            
            response = MailerPandaResponse(
                status="awaiting_approval",
                user_id=request.user_id,
                mode=request.mode,
                campaign_id=session_id,
                email_template=result.get("email_template"),
                requires_approval=True,
                approval_status="pending",
                feedback_required=True,
                processing_time=processing_time
            )
        else:
            # Complete execution
            active_sessions[session_id]["status"] = "completed"
            
            response = MailerPandaResponse(
                status="completed",
                user_id=request.user_id,
                mode=request.mode,
                campaign_id=session_id,
                email_template=result.get("email_template"),
                requires_approval=False,
                emails_sent=result.get("emails_sent", 0),
                send_status=result.get("send_status", []),
                vault_storage_key=result.get("vault_storage_key"),
                trust_links=result.get("trust_links", []),
                processing_time=processing_time
            )
        
        return response
        
    except Exception as e:
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        if session_id in active_sessions:
            active_sessions[session_id]["status"] = "error"
        
        return MailerPandaResponse(
            status="error",
            user_id=request.user_id,
            mode=request.mode,
            errors=[str(e)],
            processing_time=processing_time
        )

@app.post("/agents/mailerpanda/approve", response_model=MailerPandaResponse)
async def approve_mailerpanda_campaign(request: MailerPandaApprovalRequest):
    """Handle human-in-the-loop approval for MailerPanda campaigns."""
    start_time = datetime.now(timezone.utc)
    
    if request.campaign_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Campaign session not found")
    
    session = active_sessions[request.campaign_id]
    
    try:
        agent = session["agent"]
        original_request = session["request"]
        
        if request.action == "approve":
            # Continue with email sending
            result = session.get("result", {})
            # Simulate email sending completion
            result.update({
                "emails_sent": len(original_request.recipient_emails) if original_request.recipient_emails else 1,
                "send_status": [{"email": email, "status": "sent"} for email in (original_request.recipient_emails or ["demo@example.com"])],
                "approval_status": "approved"
            })
            
            session["status"] = "completed"
            
        elif request.action == "reject":
            session["status"] = "rejected"
            result = {"approval_status": "rejected"}
            
        elif request.action == "modify":
            # Handle modifications
            session["status"] = "modifying"
            result = {
                "approval_status": "modifying",
                "feedback": request.feedback,
                "requires_regeneration": True
            }
            
        elif request.action == "regenerate":
            # Trigger regeneration
            session["status"] = "regenerating"
            result = {"approval_status": "regenerating"}
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        return MailerPandaResponse(
            status=session["status"],
            user_id=request.user_id,
            mode=original_request.mode,
            campaign_id=request.campaign_id,
            approval_status=result.get("approval_status"),
            emails_sent=result.get("emails_sent"),
            send_status=result.get("send_status"),
            processing_time=processing_time
        )
        
    except Exception as e:
        return MailerPandaResponse(
            status="error",
            user_id=request.user_id,
            campaign_id=request.campaign_id,
            errors=[str(e)],
            processing_time=(datetime.now(timezone.utc) - start_time).total_seconds()
        )

@app.get("/agents/mailerpanda/status", response_model=AgentStatusResponse)
async def get_mailerpanda_status():
    """Get MailerPanda agent status and requirements."""
    return AgentStatusResponse(
        agent_id="agent_mailerpanda",
        name="MailerPanda Agent",
        version="3.0.0", 
        status="available",
        required_scopes=[
            "vault.read.email", "vault.write.email",
            "vault.read.file", "vault.write.file", "custom.temporary"
        ],
        required_inputs={
            "user_id": "User identifier",
            "consent_tokens": "Dictionary of consent tokens for various scopes",
            "user_input": "Email campaign description",
            "mode": "Execution mode (interactive, headless, demo)"
        }
    )

@app.get("/agents/mailerpanda/session/{campaign_id}")
async def get_mailerpanda_session(campaign_id: str):
    """Get the status of a specific MailerPanda campaign session."""
    if campaign_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Campaign session not found")
    
    session = active_sessions[campaign_id]
    return {
        "campaign_id": campaign_id,
        "status": session["status"],
        "start_time": session["start_time"].isoformat(),
        "requires_approval": session.get("result", {}).get("requires_approval", False)
    }

# ============================================================================
# MAIN APPLICATION
# ============================================================================

if __name__ == "__main__":
    print("Starting HushMCP Agent API Server...")
    print("API Documentation: http://127.0.0.1:8001/docs")
    print("Alternative Docs: http://127.0.0.1:8001/redoc")
    print("Supported Agents:")
    print("   - AddToCalendar Agent: /agents/addtocalendar/")
    print("   - MailerPanda Agent: /agents/mailerpanda/")
    
    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8001,
        reload=False,
        log_level="info"
    )
