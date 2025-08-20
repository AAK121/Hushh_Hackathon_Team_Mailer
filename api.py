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

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv('.env')
    print("Environment variables loaded from .env file")
except ImportError:
    print("python-dotenv not installed, using system environment variables")

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
    elif agent_id == "agent_chandufinance":
        return {
            "required_tokens": ["finance_token"],
            "required_scopes": [
                "vault.read.finance", "vault.write.file", 
                "agent.finance.analyze", "custom.session.write"
            ],
            "additional_requirements": {
                "ticker": "Stock ticker symbol (e.g., AAPL, MSFT)",
                "command": "Command to execute (run_valuation, get_financials, run_sensitivity, market_analysis)"
            },
            "optional_parameters": {
                "market_price": "Current market price for comparison",
                "wacc": "Weighted average cost of capital (default: 0.10)",
                "terminal_growth_rate": "Terminal growth rate for DCF (default: 0.025)",
                "wacc_range": "WACC range for sensitivity analysis (tuple)",
                "growth_range": "Growth rate range for sensitivity analysis (tuple)"
            }
        }
    elif agent_id == "agent_relationship_memory":
        return {
            "required_tokens": ["memory_tokens (dict)"],
            "required_scopes": [
                "vault.read.contacts", "vault.write.contacts",
                "vault.read.memory", "vault.write.memory", 
                "vault.read.reminder", "vault.write.reminder"
            ],
            "additional_requirements": {
                "user_input": "Natural language input for relationship management",
                "user_id": "User identifier"
            },
            "optional_parameters": {
                "vault_key": "Specific vault key for data access",
                "is_startup": "Whether this is a startup/initialization call (default: False)"
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
        "supported_agents": ["agent_addtocalendar", "agent_mailerpanda", "agent_chandufinance", "agent_relationship_memory"],
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
    
    # ChanduFinance agent info
    agents["agent_chandufinance"] = {
        "name": "ChanduFinance Agent",
        "version": "1.0.0", 
        "description": "Financial valuation and DCF analysis with investment recommendations",
        "status": "available",
        "requirements": get_agent_requirements("agent_chandufinance"),
        "endpoints": {
            "execute": "/agents/chandufinance/execute",
            "status": "/agents/chandufinance/status"
        }
    }
    
    # Relationship Memory agent info
    agents["agent_relationship_memory"] = {
        "name": "Relationship Memory Agent",
        "version": "2.0.0",
        "description": "AI-powered relationship management with contact tracking, memories, and reminders",
        "status": "available", 
        "requirements": get_agent_requirements("agent_relationship_memory"),
        "endpoints": {
            "execute": "/agents/relationship_memory/execute",
            "proactive": "/agents/relationship_memory/proactive",
            "status": "/agents/relationship_memory/status"
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
        

        if result:
            analysis_summary = result.get("analysis_summary", {})
            
            # Ensure analysis_summary is a dict
            if not isinstance(analysis_summary, dict):
                analysis_summary = {}
        
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
# CHANDUFINANCE AGENT ENDPOINTS  
# ============================================================================

class ChanduFinanceRequest(BaseModel):
    """Request model for ChanduFinance agent execution."""
    user_id: str = Field(..., min_length=1, description="User identifier")
    token: str = Field(..., min_length=10, description="HushhMCP consent token")
    command: str = Field(..., description="Command to execute")
    
    # Profile setup parameters
    full_name: Optional[str] = Field(None, description="User's full name")
    age: Optional[int] = Field(None, ge=16, le=100, description="User's age")
    occupation: Optional[str] = Field(None, description="User's occupation")
    monthly_income: Optional[float] = Field(None, ge=0, description="Monthly income")
    monthly_expenses: Optional[float] = Field(None, ge=0, description="Monthly expenses")
    current_savings: Optional[float] = Field(None, ge=0, description="Current savings amount")
    current_debt: Optional[float] = Field(None, ge=0, description="Current debt amount")
    investment_budget: Optional[float] = Field(None, ge=0, description="Investment budget")
    risk_tolerance: Optional[str] = Field(None, description="Risk tolerance (conservative/moderate/aggressive)")
    investment_experience: Optional[str] = Field(None, description="Investment experience level")
    
    # Goal management parameters
    goal_name: Optional[str] = Field(None, description="Financial goal name")
    target_amount: Optional[float] = Field(None, ge=0, description="Goal target amount")
    target_date: Optional[str] = Field(None, description="Goal target date (YYYY-MM-DD)")
    priority: Optional[str] = Field(None, description="Goal priority (high/medium/low)")
    
    # Stock analysis parameters
    ticker: Optional[str] = Field(None, min_length=1, max_length=10, description="Stock ticker symbol")
    
    # Education parameters
    topic: Optional[str] = Field(None, description="Educational topic")
    complexity: Optional[str] = Field(None, description="Complexity level (beginner/intermediate/advanced)")

class ChanduFinanceResponse(BaseModel):
    """Response model for ChanduFinance agent execution."""
    status: str
    agent_id: str = "chandufinance"
    user_id: str
    command: str
    message: Optional[str] = None
    
    # Profile data
    profile_summary: Optional[Dict[str, Any]] = None
    welcome_message: Optional[str] = None
    profile_health_score: Optional[Dict[str, Any]] = None
    personal_info: Optional[Dict[str, Any]] = None
    financial_info: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    goals: Optional[List[Dict[str, Any]]] = None
    
    # Analysis results
    ticker: Optional[str] = None
    current_price: Optional[float] = None
    personalized_analysis: Optional[str] = None
    explanation: Optional[str] = None
    coaching_advice: Optional[str] = None
    goal_details: Optional[Dict[str, Any]] = None
    
    # Metadata
    next_steps: Optional[List[str]] = None
    vault_stored: Optional[bool] = None
    timestamp: Optional[str] = None
    errors: Optional[List[str]] = None
    processing_time: float

@app.post("/agents/chandufinance/execute", response_model=ChanduFinanceResponse)
async def execute_chandufinance_agent(request: ChanduFinanceRequest):
    """Execute ChanduFinance agent for comprehensive personal financial advice."""
    start_time = datetime.now(timezone.utc)
    
    try:
        # Import and execute the ChanduFinance agent
        from hushh_mcp.agents.chandufinance.index import run_agent
        
        # Prepare parameters based on command
        parameters = {
            'command': request.command
        }
        
        # Add parameters based on command type
        if request.command == 'setup_profile':
            # Profile setup parameters
            if request.full_name is not None:
                parameters['full_name'] = request.full_name
            if request.age is not None:
                parameters['age'] = request.age
            if request.occupation is not None:
                parameters['occupation'] = request.occupation
            if request.monthly_income is not None:
                parameters['monthly_income'] = request.monthly_income
            if request.monthly_expenses is not None:
                parameters['monthly_expenses'] = request.monthly_expenses
            if request.current_savings is not None:
                parameters['current_savings'] = request.current_savings
            if request.current_debt is not None:
                parameters['current_debt'] = request.current_debt
            if request.investment_budget is not None:
                parameters['investment_budget'] = request.investment_budget
            if request.risk_tolerance is not None:
                parameters['risk_tolerance'] = request.risk_tolerance
            if request.investment_experience is not None:
                parameters['investment_experience'] = request.investment_experience
                
        elif request.command == 'update_income':
            if request.monthly_income is not None:
                parameters['income'] = request.monthly_income
                
        elif request.command == 'add_goal':
            if request.goal_name is not None:
                parameters['goal_name'] = request.goal_name
            if request.target_amount is not None:
                parameters['target_amount'] = request.target_amount
            if request.target_date is not None:
                parameters['target_date'] = request.target_date
            if request.priority is not None:
                parameters['priority'] = request.priority
                
        elif request.command == 'personal_stock_analysis':
            if request.ticker is not None:
                parameters['ticker'] = request.ticker
                
        elif request.command in ['explain_like_im_new', 'investment_education', 'behavioral_coaching']:
            if request.topic is not None:
                parameters['topic'] = request.topic
            if request.complexity is not None:
                parameters['complexity'] = request.complexity
        
        # Execute the agent
        result = run_agent(
            user_id=request.user_id,
            token=request.token,
            parameters=parameters
        )
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        # Format response based on agent result
        if result.get("status") == "success":
            return ChanduFinanceResponse(
                status="success",
                user_id=request.user_id,
                command=request.command,
                message=result.get("message", "Operation completed successfully"),
                profile_summary=result.get("profile_summary"),
                welcome_message=result.get("welcome_message"),
                profile_health_score=result.get("profile_health_score"),
                personal_info=result.get("personal_info"),
                financial_info=result.get("financial_info"),
                preferences=result.get("preferences"),
                goals=result.get("goals"),
                ticker=result.get("ticker"),
                current_price=result.get("current_price"),
                personalized_analysis=result.get("personalized_analysis"),
                explanation=result.get("explanation"),
                coaching_advice=result.get("coaching_advice"),
                goal_details=result.get("goal_details"),
                next_steps=result.get("next_steps"),
                vault_stored=result.get("vault_stored"),
                timestamp=result.get("timestamp"),
                processing_time=processing_time
            )
        else:
            return ChanduFinanceResponse(
                status="error",
                user_id=request.user_id,
                command=request.command,
                errors=[result.get("error", "Unknown error occurred")],
                processing_time=processing_time
            )
            
    except Exception as e:
        return ChanduFinanceResponse(
            status="error",
            user_id=request.user_id,
            command=request.command,
            errors=[str(e)],
            processing_time=(datetime.now(timezone.utc) - start_time).total_seconds()
        )

@app.get("/agents/chandufinance/status", response_model=AgentStatusResponse)
async def get_chandufinance_status():
    """Get ChanduFinance agent status and requirements."""
    return AgentStatusResponse(
        agent_id="agent_chandufinance",
        name="ChanduFinance Personal Financial Advisor",
        version="2.0.0",
        status="available", 
        required_scopes=[
            "vault.read.file", "vault.write.file",
            "vault.read.finance", "agent.finance.analyze"
        ],
        required_inputs={
            "user_id": "User identifier",
            "token": "HushhMCP consent token",
            "command": "Command to execute",
        },
        supported_commands=[
            "setup_profile",
            "update_personal_info", 
            "update_income",
            "set_budget",
            "add_goal",
            "view_profile",
            "personal_stock_analysis",
            "portfolio_review",
            "goal_progress_check",
            "explain_like_im_new",
            "investment_education",
            "behavioral_coaching"
        ],
        description="AI-powered personal financial advisor with encrypted vault storage, goal tracking, stock analysis, and educational content"
    )

# ============================================================================
# RELATIONSHIP MEMORY AGENT ENDPOINTS
# ============================================================================

class RelationshipMemoryRequest(BaseModel):
    """Request model for Relationship Memory agent execution."""
    user_id: str = Field(..., min_length=1, description="User identifier")
    tokens: Dict[str, str] = Field(..., description="Dictionary of consent tokens for various scopes")
    user_input: str = Field(..., min_length=1, description="Natural language input for relationship management")
    vault_key: Optional[str] = Field(None, description="Specific vault key for data access")
    is_startup: Optional[bool] = Field(False, description="Whether this is a startup/initialization call")

class RelationshipMemoryResponse(BaseModel):
    """Response model for Relationship Memory agent execution."""
    status: str
    agent_id: str = "relationship_memory"
    user_id: str
    message: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    processing_time: float

@app.post("/agents/relationship_memory/execute", response_model=RelationshipMemoryResponse)
async def execute_relationship_memory_agent(request: RelationshipMemoryRequest):
    """Execute Relationship Memory agent for contact and memory management."""
    start_time = datetime.now(timezone.utc)
    
    try:
        # Import and execute the Relationship Memory agent
        from hushh_mcp.agents.relationship_memory.index import run
        
        # Execute the agent
        result = run(
            user_id=request.user_id,
            tokens=request.tokens,
            user_input=request.user_input,
            vault_key=request.vault_key,
            is_startup=request.is_startup
        )
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        # Format response based on agent result
        if result.get("status") == "success":
            return RelationshipMemoryResponse(
                status="success",
                user_id=request.user_id,
                message=result.get("message", "Relationship management completed successfully"),
                results=result,
                processing_time=processing_time
            )
        else:
            # Extract error message properly
            error_message = result.get("message") or result.get("error") or "Unknown error occurred"
            return RelationshipMemoryResponse(
                status="error",
                agent_id=result.get("agent_id", "relationship_memory"),
                user_id=request.user_id,
                message=error_message,
                results=None,
                errors=[error_message],
                processing_time=processing_time
            )
            
    except Exception as e:
        return RelationshipMemoryResponse(
            status="error",
            user_id=request.user_id,
            errors=[str(e)],
            processing_time=(datetime.now(timezone.utc) - start_time).total_seconds()
        )

@app.post("/agents/relationship_memory/proactive")
async def execute_relationship_memory_proactive(request: Dict[str, Any]):
    """Execute proactive checks for Relationship Memory agent."""
    start_time = datetime.now(timezone.utc)
    
    try:
        # Import and execute the proactive function
        from hushh_mcp.agents.relationship_memory.index import run_proactive_check
        
        # Execute proactive check
        result = run_proactive_check(
            user_id=request.get("user_id"),
            tokens=request.get("tokens", {}),
            vault_key=request.get("vault_key")
        )
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        return {
            "status": "success" if result.get("status") == "success" else "error",
            "agent_id": "relationship_memory",
            "user_id": request.get("user_id"),
            "results": result,
            "processing_time": processing_time
        }
        
    except Exception as e:
        return {
            "status": "error",
            "agent_id": "relationship_memory", 
            "user_id": request.get("user_id"),
            "errors": [str(e)],
            "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
        }

@app.get("/agents/relationship_memory/status", response_model=AgentStatusResponse)
async def get_relationship_memory_status():
    """Get Relationship Memory agent status and requirements."""
    return AgentStatusResponse(
        agent_id="agent_relationship_memory",
        name="Relationship Memory Agent",
        version="2.0.0",
        status="available",
        required_scopes=[
            "vault.read.contacts", "vault.write.contacts",
            "vault.read.memory", "vault.write.memory",
            "vault.read.reminder", "vault.write.reminder"
        ],
        required_inputs={
            "user_id": "User identifier",
            "tokens": "Dictionary of consent tokens for various scopes",
            "user_input": "Natural language input for relationship management"
        }
    )

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
    print("   - ChanduFinance Agent: /agents/chandufinance/")
    print("   - Relationship Memory Agent: /agents/relationship_memory/")
    
    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8002,
        reload=False,
        log_level="info"
    )
