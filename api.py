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

# Optional numpy import for handling numeric types
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("numpy not available, using standard Python types")

# Utility function to convert numpy types to JSON serializable types
def convert_numpy_types(obj):
    """Convert numpy types to JSON serializable Python types."""
    if not NUMPY_AVAILABLE:
        return obj
    
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    return obj

from fastapi import FastAPI, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
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
    description="Privacy-first AI agent orchestration platform supporting AddToCalendar and MailerPanda agents with intelligent email personalization",
    version="2.1.0",
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

class AgentResponse(BaseModel):
    """Standard response model for agent operations."""
    status: str
    agent_id: str
    user_id: str
    session_id: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    processing_time: Optional[float] = None

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
    
    # Dynamic API key support
    google_api_key: Optional[str] = Field(None, description="Dynamic Google API key for AI operations")
    api_keys: Optional[Dict[str, str]] = Field(None, description="Additional API keys for various services")
    
    @field_validator('action')
    @classmethod
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
    
    # ✨ NEW: Personalization settings
    enable_description_personalization: Optional[bool] = Field(True, description="Enable AI-powered description-based email personalization")
    excel_file_path: Optional[str] = Field(None, description="Path to Excel file with contact descriptions")
    personalization_mode: Optional[str] = Field("smart", description="Personalization mode: 'smart', 'conservative', or 'aggressive'")
    
    # Dynamic API key support
    google_api_key: Optional[str] = Field(None, description="Dynamic Google API key for AI generation")
    mailjet_api_key: Optional[str] = Field(None, description="Dynamic Mailjet API key for email sending")
    mailjet_api_secret: Optional[str] = Field(None, description="Dynamic Mailjet API secret for email sending")
    api_keys: Optional[Dict[str, str]] = Field(None, description="Additional API keys for various services")
    
    @field_validator('mode')
    @classmethod
    def validate_mode(cls, v):
        allowed_modes = ["interactive", "headless"]
        if v not in allowed_modes:
            raise ValueError(f"Mode must be one of: {allowed_modes}")
        return v
        
    @field_validator('personalization_mode')
    @classmethod
    def validate_personalization_mode(cls, v):
        if v is not None:
            allowed_modes = ["smart", "conservative", "aggressive"]
            if v not in allowed_modes:
                raise ValueError(f"Personalization mode must be one of: {allowed_modes}")
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
    
    # ✨ NEW: Personalization statistics
    personalization_enabled: Optional[bool] = Field(None, description="Whether personalization was enabled")
    personalized_count: Optional[int] = Field(None, description="Number of emails that were personalized")
    standard_count: Optional[int] = Field(None, description="Number of emails using standard template")
    description_column_detected: Optional[bool] = Field(None, description="Whether description column was found in data")
    contacts_with_descriptions: Optional[int] = Field(None, description="Number of contacts with descriptions")
    
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
    
    @field_validator('action')
    @classmethod
    def validate_action(cls, v):
        allowed_actions = ["approve", "reject", "modify", "regenerate"]
        if v not in allowed_actions:
            raise ValueError(f"Action must be one of: {allowed_actions}")
        return v

class MassEmailResponse(BaseModel):
    """Response model for mass email operations."""
    status: str = Field(..., description="Operation status")
    user_id: str = Field(..., description="User identifier")
    campaign_id: Optional[str] = Field(None, description="Campaign ID if created")
    emails_sent: Optional[int] = Field(None, description="Number of emails sent")
    emails_failed: Optional[int] = Field(None, description="Number of emails that failed")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    message: Optional[str] = Field(None, description="Status message")
    errors: Optional[List[str]] = Field(None, description="List of errors if any")
    
    # Mass email specific fields
    template: Optional[Dict[str, str]] = Field(None, description="Email template used")
    recipients_processed: Optional[int] = Field(None, description="Total recipients processed")
    personalization_stats: Optional[Dict[str, Any]] = Field(None, description="Personalization statistics")

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
                "mode": "Execution mode (interactive, headless)"
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
    elif agent_id == "agent_research":
        return {
            "required_tokens": ["consent_tokens (dict)"],
            "required_scopes": [
                "custom.temporary", "vault.read.file", "vault.write.file"
            ],
            "additional_requirements": {
                "query": "Natural language research query for arXiv search",
                "user_id": "User identifier"
            },
            "optional_parameters": {
                "paper_file": "PDF file for upload and processing",
                "text_snippet": "Text snippet for AI processing",
                "instruction": "Processing instruction for snippets",
                "editor_id": "Editor identifier for note management",
                "content": "Note content for saving"
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
        "version": "3.1.0",
        "description": "AI-powered mass mailer with human-in-the-loop approval and intelligent description-based email personalization",
        "status": "available",
        "features": [
            "AI Content Generation (Gemini-2.0-flash)",
            "Human-in-the-Loop Approval Workflow", 
            "LangGraph State Management",
            "Mass Email with Excel Integration",
            "Dynamic Placeholder Detection",
            "Description-Based Email Personalization",  # ✨ NEW
            "Real-time Status Tracking",
            "HushMCP Consent-Driven Operations",
            "Secure Vault Data Storage",
            "Trust Link Agent Delegation",
            "Interactive Feedback Loop",
            "Error Recovery & Logging",
            "Cross-Agent Communication"
        ],
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
        "version": "2.1.0", 
        "description": "Advanced AI-powered financial advisor with portfolio management, analytics, market data, and planning capabilities",
        "status": "available",
        "requirements": get_agent_requirements("agent_chandufinance"),
        "endpoints": {
            "execute": "/agents/chandufinance/execute",
            "status": "/agents/chandufinance/status",
            # Portfolio Management
            "portfolio_create": "/agents/chandufinance/portfolio/create",
            "portfolio_analyze": "/agents/chandufinance/portfolio/analyze", 
            "portfolio_rebalance": "/agents/chandufinance/portfolio/rebalance",
            # Financial Analytics
            "analytics_cashflow": "/agents/chandufinance/analytics/cashflow",
            "analytics_spending": "/agents/chandufinance/analytics/spending",
            "analytics_tax": "/agents/chandufinance/analytics/tax-optimization",
            # Market Data
            "market_stocks": "/agents/chandufinance/market/stock-price",
            "market_portfolio": "/agents/chandufinance/market/portfolio-value",
            # Advanced Planning
            "planning_retirement": "/agents/chandufinance/planning/retirement",
            "planning_emergency": "/agents/chandufinance/planning/emergency-fund"
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
            "status": "/agents/relationship_memory/status",
            "chat_start": "/agents/relationship_memory/chat/start",
            "chat_message": "/agents/relationship_memory/chat/message",
            "chat_history": "/agents/relationship_memory/chat/{session_id}/history",
            "chat_end": "/agents/relationship_memory/chat/{session_id}",
            "chat_sessions": "/agents/relationship_memory/chat/sessions"
        }
    }
    
    # Research agent info
    agents["agent_research"] = {
        "name": "Research Agent",
        "version": "1.0.0",
        "description": "AI-powered academic research assistant with arXiv integration and intelligent paper analysis",
        "status": "available",
        "requirements": get_agent_requirements("agent_research"),
        "endpoints": {
            "search_arxiv": "/agents/research/search/arxiv",
            "upload": "/agents/research/upload",
            "summary": "/agents/research/paper/{paper_id}/summary",
            "process_snippet": "/agents/research/paper/{paper_id}/process/snippet",
            "save_notes": "/agents/research/session/notes",
            "status": "/agents/research/status"
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
        
        # Issue token
        token_obj = issue_token(
            user_id=request.user_id,
            agent_id=request.agent_id, 
            scope=scope_enum
        )
        
        return ConsentTokenResponse(
            token=token_obj.token,
            expires_at=token_obj.expires_at,
            scope=str(token_obj.scope)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create token: {str(e)}")

@app.post("/consent/tokens", response_model=ConsentTokenResponse)  
async def create_consent_token_plural(request: ConsentTokenRequest):
    """Create a consent token for agent operations (plural endpoint)."""
    try:
        # Convert scope string to ConsentScope enum
        scope_enum = getattr(ConsentScope, request.scope.replace(".", "_").upper(), None)
        if not scope_enum:
            raise HTTPException(status_code=400, detail=f"Invalid scope: {request.scope}")
        
        # Issue token
        token_obj = issue_token(
            user_id=request.user_id,
            agent_id=request.agent_id, 
            scope=scope_enum
        )
        
        return ConsentTokenResponse(
            token=token_obj.token,
            expires_at=token_obj.expires_at,
            scope=str(token_obj.scope)
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
        
        # Extract dynamic API keys for agent initialization
        api_keys = {}
        if request.google_api_key:
            api_keys['google_api_key'] = request.google_api_key
        if request.api_keys:
            api_keys.update(request.api_keys)
            
        # Initialize agent with dynamic API keys
        agent = AddToCalendarAgent(api_keys=api_keys)
        
        # Execute agent with dynamic API keys
        result = agent.handle(
            user_id=request.user_id,
            email_token_str=request.email_token,
            calendar_token_str=request.calendar_token,
            google_access_token=request.google_access_token,
            action=request.action,
            manual_event=request.manual_event,
            confidence_threshold=request.confidence_threshold,
            max_emails=request.max_emails,
            **api_keys  # Pass API keys as keyword arguments
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
        
        # Extract dynamic API keys for agent initialization
        api_keys = {}
        if request.google_api_key:
            api_keys['google_api_key'] = request.google_api_key
        if request.mailjet_api_key:
            api_keys['mailjet_api_key'] = request.mailjet_api_key
        if request.mailjet_api_secret:
            api_keys['mailjet_api_secret'] = request.mailjet_api_secret
        if request.api_keys:
            api_keys.update(request.api_keys)
            
        # Initialize agent with dynamic API keys
        agent = MassMailerAgent(api_keys=api_keys)
        
        # Store session for potential human-in-the-loop workflows
        active_sessions[session_id] = {
            "agent": agent,
            "request": request,
            "start_time": start_time,
            "status": "executing"
        }
        
        # Execute agent with dynamic API keys and personalization parameters
        result = agent.handle(
            user_id=request.user_id,
            consent_tokens=request.consent_tokens,
            user_input=request.user_input,
            mode=request.mode,
            enable_description_personalization=request.enable_description_personalization,
            excel_file_path=request.excel_file_path,
            personalization_mode=request.personalization_mode,
            **api_keys  # Pass API keys as keyword arguments
        )
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        # 🚀 [CRITICAL FIX] Construct proper email_template structure for frontend
        email_template_body = result.get("email_template")
        subject = result.get("subject", "Email Campaign")
        
        # Construct email_template with proper structure for frontend
        if email_template_body:
            email_template = {
                "subject": subject,
                "body": email_template_body
            }
        else:
            email_template = None
        
        print(f"🔍 [DEBUG] Agent result email_template: {email_template_body}")
        print(f"🔍 [DEBUG] Agent result subject: {subject}")
        print(f"🔍 [DEBUG] Constructed email_template: {email_template}")
        
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
                email_template=email_template,
                requires_approval=True,
                approval_status="pending",
                feedback_required=True,
                processing_time=processing_time,
                personalized_count=result.get("personalized_count", 0),
                standard_count=result.get("standard_count", 0),
                description_column_detected=result.get("description_column_detected", False)
            )
        else:
            # Complete execution
            active_sessions[session_id]["status"] = "completed"
            
            response = MailerPandaResponse(
                status="completed",
                user_id=request.user_id,
                mode=request.mode,
                campaign_id=session_id,
                email_template=email_template,
                requires_approval=False,
                emails_sent=result.get("emails_sent", 0),
                send_status=result.get("send_status", []),
                vault_storage_key=result.get("vault_storage_key"),
                trust_links=result.get("trust_links", []),
                processing_time=processing_time,
                personalized_count=result.get("personalized_count", 0),
                standard_count=result.get("standard_count", 0),
                description_column_detected=result.get("description_column_detected", False)
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

@app.post("/agents/mailerpanda/approve", response_model=MassEmailResponse)
async def approve_mailerpanda_campaign(request: MailerPandaApprovalRequest):
    """Handle human-in-the-loop approval for MailerPanda campaigns."""
    start_time = datetime.now(timezone.utc)
    
    if request.campaign_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Campaign session not found")
    
    session = active_sessions[request.campaign_id]
    
    try:
        agent = session["agent"]
        original_request = session["request"]
        saved_state = session.get("final_state", {})
        
        # Use the resume method to continue the workflow
        result = agent.resume_from_approval(
            saved_state=saved_state,
            approval_action=request.action,
            feedback=request.feedback or ""
        )
        
        # Convert numpy types to avoid serialization errors
        result = convert_numpy_types(result)
        
        # Also convert any remaining numpy types in nested structures
        if isinstance(result, dict):
            def clean_numpy_recursive(obj):
                if isinstance(obj, dict):
                    return {k: clean_numpy_recursive(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [clean_numpy_recursive(item) for item in obj]
                elif hasattr(obj, 'item'):  # numpy scalar
                    return obj.item()
                elif str(type(obj)).startswith('<class \'numpy.'):
                    return int(obj) if 'int' in str(type(obj)) else float(obj)
                else:
                    return obj
            result = clean_numpy_recursive(result)
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        # 🚀 [CRITICAL FIX] Construct proper email_template structure for frontend 
        email_template_body = result.get("email_template")
        # Get subject from agent result first, then fall back to saved_state
        subject = result.get("subject") or saved_state.get("subject", "Email Campaign")
        
        # Construct email_template with proper structure for frontend
        if isinstance(email_template_body, str):
            email_template = {
                "subject": subject,
                "body": email_template_body
            }
        elif email_template_body is None:
            email_template = None
        else:
            # If email_template is already a dict, ensure it has both subject and body
            email_template = email_template_body
            if "subject" not in email_template:
                email_template["subject"] = subject
        
        print(f"🔍 [DEBUG] Agent result email_template: {email_template_body}")
        print(f"🔍 [DEBUG] Agent result subject: {result.get('subject')}")
        print(f"🔍 [DEBUG] Saved state subject: {saved_state.get('subject')}")
        print(f"🔍 [DEBUG] Final subject used: {subject}")
        print(f"🔍 [DEBUG] Final email_template: {email_template}")
        
        # Update session status
        if request.action == "approve":
            session["status"] = "completed"
            status = "completed"
        elif request.action == "reject":
            session["status"] = "rejected"
            status = "rejected"
        else:
            session["status"] = "modified"
            status = "modified"
        
        return MassEmailResponse(
            status=status,
            user_id=request.user_id,
            campaign_id=request.campaign_id,
            context_personalization_enabled=session.get("enable_description_personalization", False),
            excel_analysis=session.get("excel_analysis", {}),
            email_template=email_template,
            emails_sent=result.get("emails_sent", 0),
            personalized_count=saved_state.get("personalized_count", 0),
            standard_count=saved_state.get("standard_count", 0),
            requires_approval=False,
            approval_status=request.action,
            processing_time=processing_time
        )
        
    except Exception as e:
        return MassEmailResponse(
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
            "mode": "Execution mode (interactive, headless)"
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
# MAILERPANDA MASS EMAIL WITH CONTEXT TOGGLE ENDPOINT
# ============================================================================

class MassEmailRequest(BaseModel):
    """Request model for mass email with context toggle functionality."""
    user_id: str = Field(..., description="User identifier")
    user_input: str = Field(..., description="Email campaign description")
    
    # Consent tokens
    consent_tokens: Dict[str, str] = Field(..., description="Consent tokens for various scopes")
    
    # Frontend toggle for context-based personalization
    use_context_personalization: bool = Field(False, description="Toggle: True = use descriptions for personalization, False = send standard emails")
    
    # Excel file (required for mass email)
    excel_file_data: Optional[str] = Field(None, description="Base64 encoded Excel file data")
    excel_file_name: Optional[str] = Field(None, description="Excel file name")
    
    # Campaign settings
    mode: str = Field(default="interactive", description="Execution mode")
    personalization_mode: str = Field(default="smart", description="Personalization intensity when context is enabled")
    
    # API keys
    google_api_key: Optional[str] = Field(None, description="Google API key for AI generation")
    mailjet_api_key: Optional[str] = Field(None, description="Mailjet API key")
    mailjet_api_secret: Optional[str] = Field(None, description="Mailjet API secret")
    
    @field_validator('mode')
    @classmethod
    def validate_mode(cls, v):
        allowed_modes = ["interactive", "headless"]
        if v not in allowed_modes:
            raise ValueError(f"Mode must be one of: {allowed_modes}")
        return v

class MassEmailResponse(BaseModel):
    """Response model for mass email with context information."""
    status: str = Field(..., description="Operation status")
    user_id: str = Field(..., description="User identifier")
    campaign_id: Optional[str] = Field(None, description="Generated campaign ID")
    
    # Context usage information
    context_personalization_enabled: bool = Field(..., description="Whether context personalization was used")
    excel_analysis: Dict[str, Any] = Field(..., description="Analysis of uploaded Excel file")
    
    # Email results
    email_template: Optional[Dict[str, str]] = Field(None, description="Generated email template")
    emails_sent: Optional[int] = Field(None, description="Number of emails sent")
    
    # Personalization statistics
    personalized_count: Optional[int] = Field(None, description="Number of personalized emails")
    standard_count: Optional[int] = Field(None, description="Number of standard emails")
    
    # Approval workflow
    requires_approval: Optional[bool] = Field(None, description="Whether approval is needed")
    approval_status: Optional[str] = Field(None, description="Approval status")
    
    # Processing info
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    errors: Optional[List[str]] = Field(None, description="Any errors encountered")

@app.post("/agents/mailerpanda/mass-email", response_model=MassEmailResponse)
async def mass_email_with_context_toggle(request: MassEmailRequest):
    """
    Send mass emails with context toggle functionality.
    
    Frontend can toggle between:
    - Context ON: Use description column for AI personalization
    - Context OFF: Send standard emails to all recipients
    """
    start_time = datetime.now(timezone.utc)
    session_id = f"mass_email_{request.user_id}_{int(start_time.timestamp())}"
    
    try:
        import base64
        import tempfile
        
        try:
            import pandas as pd
            PANDAS_AVAILABLE = True
        except ImportError:
            PANDAS_AVAILABLE = False
            
        from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
        
        # Analyze the Excel file first
        excel_analysis = {
            "file_uploaded": False,
            "total_contacts": 0,
            "columns_found": [],
            "description_column_exists": False,
            "contacts_with_descriptions": 0,
            "context_toggle_status": "OFF" if not request.use_context_personalization else "ON"
        }
        
        excel_file_path = None
        
        # Handle Excel file upload
        if request.excel_file_data:
            try:
                # Decode base64 file data
                file_data = base64.b64decode(request.excel_file_data)
                
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                    tmp_file.write(file_data)
                    excel_file_path = tmp_file.name
                
                # Analyze the Excel file
                if PANDAS_AVAILABLE:
                    df = pd.read_excel(excel_file_path)
                    excel_analysis.update({
                        "file_uploaded": True,
                        "total_contacts": int(len(df)),  # Convert to Python int
                        "columns_found": list(df.columns),
                        "description_column_exists": 'description' in df.columns
                    })
                    
                    if excel_analysis["description_column_exists"]:
                        excel_analysis["contacts_with_descriptions"] = int(df['description'].notna().sum())  # Convert to Python int
                else:
                    # Basic analysis without pandas
                    excel_analysis.update({
                        "file_uploaded": True,
                        "total_contacts": 0,
                        "columns_found": [],
                        "description_column_exists": False,
                        "contacts_with_descriptions": 0
                    })
                
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error processing Excel file: {str(e)}")
        
        # Prepare API keys
        api_keys = {}
        if request.google_api_key:
            api_keys['google_api_key'] = request.google_api_key
        if request.mailjet_api_key:
            api_keys['mailjet_api_key'] = request.mailjet_api_key
        if request.mailjet_api_secret:
            api_keys['mailjet_api_secret'] = request.mailjet_api_secret
        
        # Initialize MailerPanda agent
        agent = MassMailerAgent(api_keys=api_keys)
        
        # Determine personalization settings based on toggle
        if request.use_context_personalization and excel_analysis["description_column_exists"]:
            # Context personalization enabled and description column exists
            enable_description_personalization = True
            personalization_mode = request.personalization_mode
            context_message = f"Context personalization ENABLED - Using description column to personalize {excel_analysis['contacts_with_descriptions']} emails"
        else:
            # Context personalization disabled or no description column
            enable_description_personalization = False
            personalization_mode = "conservative"
            if request.use_context_personalization and not excel_analysis["description_column_exists"]:
                context_message = "Context personalization requested but NO description column found - Using standard emails"
            else:
                context_message = "Context personalization DISABLED - Using standard emails for all recipients"
        
        # Store session
        active_sessions[session_id] = {
            "agent": agent,
            "request": request,
            "start_time": start_time,
            "status": "executing",
            "context_message": context_message
        }
        
        # Execute the campaign
        result = agent.handle(
            user_id=request.user_id,
            consent_tokens=request.consent_tokens,
            user_input=request.user_input,
            mode=request.mode,
            enable_description_personalization=enable_description_personalization,
            excel_file_path=excel_file_path,
            personalization_mode=personalization_mode,
            **api_keys
        )
        
        # Convert numpy types to avoid serialization errors
        result = convert_numpy_types(result)
        
        # Also convert any remaining numpy types in nested structures
        if isinstance(result, dict):
            def clean_numpy_recursive(obj):
                if isinstance(obj, dict):
                    return {k: clean_numpy_recursive(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [clean_numpy_recursive(item) for item in obj]
                elif hasattr(obj, 'item'):  # numpy scalar
                    return obj.item()
                elif str(type(obj)).startswith('<class \'numpy.'):
                    return int(obj) if 'int' in str(type(obj)) else float(obj)
                else:
                    return obj
            result = clean_numpy_recursive(result)
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        # Fix email_template format - convert string to dict if needed
        email_template = result.get("email_template")
        subject = result.get("subject", "Email Campaign")
        
        if isinstance(email_template, str):
            # If it's a string, create dict with subject and body
            email_template = {
                "subject": subject,  # Use the actual subject from result
                "body": email_template
            }
        elif isinstance(email_template, dict):
            # If it's already a dict, ensure subject is populated
            if not email_template.get("subject"):
                email_template["subject"] = subject
        elif email_template is None:
            # If no template, create one with the subject
            email_template = {
                "subject": subject,
                "body": ""
            }
        
        # Debug the email template structure
        print(f"🔍 [DEBUG] Email template structure: {email_template}")
        print(f"🔍 [DEBUG] Subject from result: {subject}")
        
        # Check if human approval is required
        requires_approval = result.get("requires_approval", False)
        
        if requires_approval and request.mode == "interactive":
            # Store session for approval workflow with complete state
            active_sessions[session_id]["status"] = "awaiting_approval"
            active_sessions[session_id]["result"] = result
            active_sessions[session_id]["final_state"] = result.get("final_state", {})
            active_sessions[session_id]["excel_analysis"] = excel_analysis
            active_sessions[session_id]["enable_description_personalization"] = enable_description_personalization
            
            response = MassEmailResponse(
                status="awaiting_approval",
                user_id=request.user_id,
                campaign_id=session_id,
                context_personalization_enabled=enable_description_personalization,
                excel_analysis=excel_analysis,
                email_template=email_template,
                emails_sent=0,
                personalized_count=int(result.get("personalized_count", 0)),
                standard_count=int(result.get("standard_count", 0)),
                requires_approval=True,
                approval_status="pending",
                processing_time=processing_time
            )
        else:
            # Complete execution
            active_sessions[session_id]["status"] = "completed"
            
            response = MassEmailResponse(
                status=result.get("status", "completed"),
                user_id=request.user_id,
                campaign_id=session_id,
                context_personalization_enabled=enable_description_personalization,
                excel_analysis=excel_analysis,
                email_template=email_template,
                emails_sent=int(result.get("emails_sent", 0)),
                personalized_count=int(result.get("personalized_count", 0)),
                standard_count=int(result.get("standard_count", 0)),
                requires_approval=False,
                approval_status=result.get("approval_status"),
                processing_time=processing_time
            )
        
        return response
        
    except Exception as e:
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        return MassEmailResponse(
            status="error",
            user_id=request.user_id,
            context_personalization_enabled=False,
            excel_analysis={"error": str(e)},
            errors=[str(e)],
            processing_time=processing_time
        )

class ExcelAnalysisRequest(BaseModel):
    excel_file_data: str = Field(..., description="Base64 encoded Excel file")

@app.post("/agents/mailerpanda/analyze-excel")
async def analyze_excel_for_context(request: ExcelAnalysisRequest):
    """
    Analyze uploaded Excel file to show context personalization options.
    This helps the frontend decide whether to show the context toggle.
    """
    try:
        import base64
        import tempfile
        import pandas as pd
        
        # Decode and analyze the Excel file
        file_data = base64.b64decode(request.excel_file_data)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            tmp_file.write(file_data)
            excel_path = tmp_file.name
        
        df = pd.read_excel(excel_path)
        
        analysis = {
            "total_contacts": len(df),
            "columns_found": list(df.columns),
            "has_email_column": any('email' in col.lower() for col in df.columns),
            "has_name_column": any('name' in col.lower() for col in df.columns),
            "has_description_column": 'description' in df.columns,
            "contacts_with_descriptions": 0,
            "context_personalization_available": False,
            "sample_descriptions": []
        }
        
        if analysis["has_description_column"]:
            descriptions = df['description'].dropna()
            analysis["contacts_with_descriptions"] = len(descriptions)
            analysis["context_personalization_available"] = len(descriptions) > 0
            analysis["sample_descriptions"] = descriptions.head(3).tolist()
        
        # Cleanup
        import os
        os.unlink(excel_path)
        
        return {
            "status": "success",
            "analysis": analysis,
            "recommendation": {
                "show_context_toggle": analysis["context_personalization_available"],
                "message": f"Found {analysis['contacts_with_descriptions']} contacts with descriptions. Context personalization recommended!" if analysis["context_personalization_available"] else "No description column found. Only standard emails available."
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "analysis": None
        }

@app.post("/agents/mailerpanda/mass-email/approve", response_model=MassEmailResponse)
async def approve_mass_email_campaign(request: MailerPandaApprovalRequest):
    """Handle human-in-the-loop approval for mass email campaigns."""
    start_time = datetime.now(timezone.utc)
    
    if request.campaign_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Campaign session not found")
    
    session = active_sessions[request.campaign_id]
    
    try:
        agent = session["agent"]
        original_request = session["request"]
        stored_result = session.get("result", {})
        excel_analysis = session.get("excel_analysis", {})
        enable_description_personalization = session.get("enable_description_personalization", False)
        
        if request.action == "approve":
            # Extract template and subject from stored results with proper format handling
            stored_result_template = stored_result.get("email_template", "")
            stored_subject = stored_result.get("subject", "")
            
            # Handle different email_template formats
            if isinstance(stored_result_template, dict):
                # If email_template is a dict, extract the body and subject
                stored_template = stored_result_template.get("body", "")
                if not stored_subject:  # Use dict subject if no direct subject
                    stored_subject = stored_result_template.get("subject", "Email Campaign")
            elif isinstance(stored_result_template, str):
                # If email_template is a string, use it directly
                stored_template = stored_result_template
            else:
                # Fallback to empty template
                stored_template = ""
            
            # If still no subject, try to get it from the final_state
            if not stored_subject:
                final_state = stored_result.get("final_state", {})
                stored_subject = final_state.get("subject", "Email Campaign")
            
            # Debug template extraction
            print(f"🔍 [API DEBUG] Stored result template type: {type(stored_result_template)}")
            print(f"🔍 [API DEBUG] Using template: {stored_template[:100] if stored_template else 'Empty'}...")
            print(f"🔍 [API DEBUG] Using subject: {stored_subject}")
            
            # Continue with email sending - call the agent again to actually send
            print(f"🔍 [API DEBUG] APPROVE ENDPOINT CALLED! Calling agent with frontend_approved=True")
            result = agent.handle(
                user_id=request.user_id,
                consent_tokens=original_request.consent_tokens,
                user_input=original_request.user_input,
                mode="headless",  # Skip approval since human already approved
                enable_description_personalization=enable_description_personalization,
                excel_file_path=stored_result.get("excel_file_path"),
                personalization_mode=original_request.personalization_mode,
                frontend_approved=True,  # ✅ KEY FIX: Tell agent emails are approved
                send_approved=True,      # ✅ KEY FIX: Tell agent to actually send
                pre_approved_template=stored_template,  # ✅ Pass the stored template
                pre_approved_subject=stored_subject,    # ✅ Pass the stored subject
                google_api_key=original_request.google_api_key,
                mailjet_api_key=original_request.mailjet_api_key,
                mailjet_api_secret=original_request.mailjet_api_secret
            )
            
            session["status"] = "completed"
            
            response = MassEmailResponse(
                status="completed",
                user_id=request.user_id,
                campaign_id=request.campaign_id,
                context_personalization_enabled=enable_description_personalization,
                excel_analysis=excel_analysis,
                email_template=stored_result.get("email_template"),
                emails_sent=result.get("emails_sent", 0),
                personalized_count=result.get("personalized_count", 0),
                standard_count=result.get("standard_count", 0),
                requires_approval=False,
                approval_status="approved",
                processing_time=(datetime.now(timezone.utc) - start_time).total_seconds()
            )
            
        elif request.action == "reject":
            session["status"] = "rejected"
            
            response = MassEmailResponse(
                status="rejected",
                user_id=request.user_id,
                campaign_id=request.campaign_id,
                context_personalization_enabled=enable_description_personalization,
                excel_analysis=excel_analysis,
                email_template=stored_result.get("email_template"),
                emails_sent=0,
                personalized_count=0,
                standard_count=0,
                requires_approval=False,
                approval_status="rejected",
                processing_time=(datetime.now(timezone.utc) - start_time).total_seconds()
            )
            
        elif request.action == "modify":
            # Handle modifications - regenerate with feedback
            modified_user_input = f"{original_request.user_input}\n\nModification feedback: {request.feedback}"
            
            result = agent.handle(
                user_id=request.user_id,
                consent_tokens=original_request.consent_tokens,
                user_input=modified_user_input,
                mode="interactive",  # Still needs approval after modification
                enable_description_personalization=enable_description_personalization,
                excel_file_path=stored_result.get("excel_file_path"),
                personalization_mode=original_request.personalization_mode,
                google_api_key=original_request.google_api_key,
                mailjet_api_key=original_request.mailjet_api_key,
                mailjet_api_secret=original_request.mailjet_api_secret
            )
            
            # Fix email_template format
            email_template = result.get("email_template")
            if isinstance(email_template, str):
                email_template = {
                    "subject": result.get("subject", "Email Campaign"),
                    "body": email_template
                }
            
            session["result"] = result
            session["status"] = "awaiting_approval"
            
            response = MassEmailResponse(
                status="awaiting_approval",
                user_id=request.user_id,
                campaign_id=request.campaign_id,
                context_personalization_enabled=enable_description_personalization,
                excel_analysis=excel_analysis,
                email_template=email_template,
                emails_sent=0,
                personalized_count=result.get("personalized_count", 0),
                standard_count=result.get("standard_count", 0),
                requires_approval=True,
                approval_status="pending",
                processing_time=(datetime.now(timezone.utc) - start_time).total_seconds()
            )
            
        elif request.action == "regenerate":
            # Regenerate content completely
            result = agent.handle(
                user_id=request.user_id,
                consent_tokens=original_request.consent_tokens,
                user_input=original_request.user_input,
                mode="interactive",  # Still needs approval after regeneration
                enable_description_personalization=enable_description_personalization,
                excel_file_path=stored_result.get("excel_file_path"),
                personalization_mode=original_request.personalization_mode,
                google_api_key=original_request.google_api_key,
                mailjet_api_key=original_request.mailjet_api_key,
                mailjet_api_secret=original_request.mailjet_api_secret
            )
            
            # Fix email_template format
            email_template = result.get("email_template")
            if isinstance(email_template, str):
                email_template = {
                    "subject": result.get("subject", "Email Campaign"),
                    "body": email_template
                }
            
            session["result"] = result
            session["status"] = "awaiting_approval"
            
            response = MassEmailResponse(
                status="awaiting_approval",
                user_id=request.user_id,
                campaign_id=request.campaign_id,
                context_personalization_enabled=enable_description_personalization,
                excel_analysis=excel_analysis,
                email_template=email_template,
                emails_sent=0,
                personalized_count=result.get("personalized_count", 0),
                standard_count=result.get("standard_count", 0),
                requires_approval=True,
                approval_status="pending",
                processing_time=(datetime.now(timezone.utc) - start_time).total_seconds()
            )
        else:
            raise HTTPException(status_code=400, detail=f"Invalid action: {request.action}")
        
        return response
        
    except Exception as e:
        return MassEmailResponse(
            status="error",
            user_id=request.user_id,
            campaign_id=request.campaign_id,
            context_personalization_enabled=False,
            excel_analysis={},
            errors=[str(e)],
            processing_time=(datetime.now(timezone.utc) - start_time).total_seconds()
        )

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
    
    # API keys and credentials (passed dynamically, not hardcoded)
    gemini_api_key: Optional[str] = Field(None, description="Gemini API key for LLM features (optional)")
    api_keys: Optional[Dict[str, str]] = Field(None, description="Additional API keys as key-value pairs")

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
        
        # Add API keys if provided (not hardcoded)
        if request.gemini_api_key is not None:
            parameters['gemini_api_key'] = request.gemini_api_key
        if request.api_keys is not None:
            parameters['api_keys'] = request.api_keys
        
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
# NEW ENHANCED CHANDUFINANCE AGENT ENDPOINTS
# ============================================================================

# Portfolio Management Models
class PortfolioCreateRequest(BaseModel):
    """Request model for creating a new investment portfolio."""
    user_id: str = Field(..., description="User identifier")
    token: str = Field(..., description="HushhMCP consent token")
    portfolio_name: str = Field(..., description="Name for the portfolio")
    investment_amount: float = Field(..., ge=100, description="Initial investment amount")
    risk_tolerance: str = Field(..., description="Risk tolerance (conservative/moderate/aggressive)")
    investment_goals: List[str] = Field(..., description="Investment goals")
    time_horizon: int = Field(..., ge=1, le=50, description="Investment time horizon in years")
    gemini_api_key: Optional[str] = Field(None, description="Gemini API key for AI features")

class PortfolioAnalyzeRequest(BaseModel):
    """Request model for portfolio analysis."""
    user_id: str = Field(..., description="User identifier")
    token: str = Field(..., description="HushhMCP consent token")
    portfolio_id: Optional[str] = Field(None, description="Portfolio ID to analyze")
    holdings: Optional[List[Dict[str, Any]]] = Field(None, description="Current holdings")
    gemini_api_key: Optional[str] = Field(None, description="Gemini API key for AI features")

class PortfolioRebalanceRequest(BaseModel):
    """Request model for portfolio rebalancing suggestions."""
    user_id: str = Field(..., description="User identifier")
    token: str = Field(..., description="HushhMCP consent token")
    portfolio_id: str = Field(..., description="Portfolio ID to rebalance")
    gemini_api_key: Optional[str] = Field(None, description="Gemini API key for AI features")

# Analytics Models
class CashflowAnalysisRequest(BaseModel):
    """Request model for cash flow analysis."""
    user_id: str = Field(..., description="User identifier")
    token: str = Field(..., description="HushhMCP consent token")
    period_months: int = Field(12, ge=1, le=60, description="Analysis period in months")
    include_projections: bool = Field(True, description="Include future projections")
    gemini_api_key: Optional[str] = Field(None, description="Gemini API key for AI features")

class SpendingAnalysisRequest(BaseModel):
    """Request model for spending pattern analysis."""
    user_id: str = Field(..., description="User identifier")
    token: str = Field(..., description="HushhMCP consent token")
    transactions: Optional[List[Dict[str, Any]]] = Field(None, description="Transaction data")
    analysis_type: str = Field("detailed", description="Analysis type (summary/detailed/predictive)")
    gemini_api_key: Optional[str] = Field(None, description="Gemini API key for AI features")

class TaxOptimizationRequest(BaseModel):
    """Request model for tax optimization analysis."""
    user_id: str = Field(..., description="User identifier")
    token: str = Field(..., description="HushhMCP consent token")
    annual_income: float = Field(..., ge=0, description="Annual income")
    investment_income: float = Field(0, ge=0, description="Investment income")
    tax_year: int = Field(2024, description="Tax year")
    gemini_api_key: Optional[str] = Field(None, description="Gemini API key for AI features")

# Market Data Models
class StockPriceRequest(BaseModel):
    """Request model for stock price lookup."""
    user_id: str = Field(..., description="User identifier")
    token: str = Field(..., description="HushhMCP consent token")
    symbols: List[str] = Field(..., description="Stock symbols to lookup")
    include_analysis: bool = Field(False, description="Include AI analysis")
    gemini_api_key: Optional[str] = Field(None, description="Gemini API key for AI features")

class PortfolioValueRequest(BaseModel):
    """Request model for portfolio valuation."""
    user_id: str = Field(..., description="User identifier")
    token: str = Field(..., description="HushhMCP consent token")
    portfolio_id: str = Field(..., description="Portfolio ID")
    include_performance: bool = Field(True, description="Include performance metrics")

# Planning Models
class RetirementPlanningRequest(BaseModel):
    """Request model for retirement planning."""
    user_id: str = Field(..., description="User identifier")
    token: str = Field(..., description="HushhMCP consent token")
    current_age: int = Field(..., ge=18, le=100, description="Current age")
    retirement_age: int = Field(..., ge=50, le=80, description="Desired retirement age")
    desired_retirement_income: float = Field(..., ge=1000, description="Desired monthly retirement income")
    current_savings: float = Field(0, ge=0, description="Current retirement savings")
    gemini_api_key: Optional[str] = Field(None, description="Gemini API key for AI features")

class EmergencyFundRequest(BaseModel):
    """Request model for emergency fund analysis."""
    user_id: str = Field(..., description="User identifier")
    token: str = Field(..., description="HushhMCP consent token")
    monthly_expenses: float = Field(..., ge=500, description="Monthly expenses")
    current_emergency_fund: float = Field(0, ge=0, description="Current emergency fund amount")
    risk_profile: str = Field("moderate", description="Risk profile (conservative/moderate/aggressive)")
    gemini_api_key: Optional[str] = Field(None, description="Gemini API key for AI features")

# Response Models
class FinanceApiResponse(BaseModel):
    """Base response model for finance API endpoints."""
    status: str = Field(..., description="Response status")
    data: Dict[str, Any] = Field(..., description="Response data")
    ai_insights: Optional[str] = Field(None, description="AI-generated insights")
    recommendations: Optional[List[str]] = Field(None, description="Actionable recommendations")
    processing_time: float = Field(..., description="Processing time in seconds")
    errors: Optional[List[str]] = Field(None, description="Any errors encountered")

# ============================================================================
# PORTFOLIO MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/agents/chandufinance/portfolio/create", response_model=FinanceApiResponse)
async def create_portfolio(request: PortfolioCreateRequest):
    """Create a new investment portfolio with AI-powered allocation."""
    start_time = datetime.now(timezone.utc)
    
    try:
        # Validate consent token
        is_valid, error_msg, token_obj = validate_token(request.token, ConsentScope.VAULT_READ_FINANCE)
        if not is_valid:
            raise HTTPException(status_code=403, detail=f"Invalid consent token: {error_msg}")
        
        # Import the enhanced finance agent
        from hushh_mcp.agents.chandufinance.index import run_agent
        
        # Prepare portfolio parameters
        parameters = {
            'command': 'create_portfolio',
            'portfolio_name': request.portfolio_name,
            'investment_amount': request.investment_amount,
            'risk_tolerance': request.risk_tolerance,
            'investment_goals': request.investment_goals,
            'time_horizon': request.time_horizon
        }
        
        # Add API key if provided
        if request.gemini_api_key:
            parameters['gemini_api_key'] = request.gemini_api_key
        
        # Execute the agent
        result = run_agent(
            user_id=request.user_id,
            tokens={
                ConsentScope.VAULT_READ_FINANCE.value: request.token,
                ConsentScope.VAULT_WRITE_FILE.value: request.token
            },
            parameters=parameters
        )
        
        # Process the result
        portfolio_data = {
            'portfolio_id': result.get('portfolio_id', f"portfolio_{request.user_id}_{int(datetime.now().timestamp())}"),
            'allocation': result.get('recommended_allocation', {}),
            'expected_return': result.get('expected_return', 0.08),
            'risk_score': result.get('risk_score', 0.15),
            'created_at': datetime.now().isoformat()
        }
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        return FinanceApiResponse(
            status="success",
            data=portfolio_data,
            ai_insights=result.get('ai_insights', 'Portfolio created successfully with optimized allocation.'),
            recommendations=result.get('recommendations', ['Monitor portfolio performance regularly', 'Consider rebalancing quarterly']),
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        return FinanceApiResponse(
            status="error",
            data={},
            errors=[str(e)],
            processing_time=processing_time
        )

@app.post("/agents/chandufinance/portfolio/analyze", response_model=FinanceApiResponse)
async def analyze_portfolio(request: PortfolioAnalyzeRequest):
    """Analyze portfolio performance and provide AI insights."""
    start_time = datetime.now(timezone.utc)
    
    try:
        # Validate consent token
        is_valid, error_msg, token_obj = validate_token(request.token, ConsentScope.VAULT_READ_FINANCE)
        if not is_valid:
            raise HTTPException(status_code=403, detail=f"Invalid consent token: {error_msg}")
        
        from hushh_mcp.agents.chandufinance.index import run_agent
        
        parameters = {
            'command': 'analyze_portfolio',
            'portfolio_id': request.portfolio_id,
            'holdings': request.holdings or []
        }
        
        if request.gemini_api_key:
            parameters['gemini_api_key'] = request.gemini_api_key
        
        result = run_agent(
            user_id=request.user_id,
            tokens={ConsentScope.VAULT_READ_FINANCE.value: request.token},
            parameters=parameters
        )
        
        analysis_data = {
            'performance_metrics': result.get('performance_metrics', {}),
            'risk_analysis': result.get('risk_analysis', {}),
            'diversification_score': result.get('diversification_score', 0.75),
            'benchmark_comparison': result.get('benchmark_comparison', {}),
            'volatility': result.get('volatility', 0.15)
        }
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        return FinanceApiResponse(
            status="success",
            data=analysis_data,
            ai_insights=result.get('ai_insights', 'Portfolio analysis completed with comprehensive metrics.'),
            recommendations=result.get('recommendations', ['Consider diversification improvements']),
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        return FinanceApiResponse(
            status="error",
            data={},
            errors=[str(e)],
            processing_time=processing_time
        )

@app.post("/agents/chandufinance/portfolio/rebalance", response_model=FinanceApiResponse)
async def rebalance_portfolio(request: PortfolioRebalanceRequest):
    """Get AI-powered portfolio rebalancing suggestions."""
    start_time = datetime.now(timezone.utc)
    
    try:
        # Validate consent token
        is_valid, error_msg, token_obj = validate_token(request.token, ConsentScope.VAULT_READ_FINANCE)
        if not is_valid:
            raise HTTPException(status_code=403, detail=f"Invalid consent token: {error_msg}")
        
        from hushh_mcp.agents.chandufinance.index import run_agent
        
        parameters = {
            'command': 'rebalance_portfolio',
            'portfolio_id': request.portfolio_id
        }
        
        if request.gemini_api_key:
            parameters['gemini_api_key'] = request.gemini_api_key
        
        result = run_agent(
            user_id=request.user_id,
            tokens={ConsentScope.VAULT_READ_FINANCE.value: request.token},
            parameters=parameters
        )
        
        rebalance_data = {
            'current_allocation': result.get('current_allocation', {}),
            'target_allocation': result.get('target_allocation', {}),
            'rebalance_trades': result.get('rebalance_trades', []),
            'estimated_cost': result.get('estimated_cost', 0),
            'expected_benefit': result.get('expected_benefit', 'Improved risk-adjusted returns')
        }
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        return FinanceApiResponse(
            status="success",
            data=rebalance_data,
            ai_insights=result.get('ai_insights', 'Rebalancing analysis completed with optimized suggestions.'),
            recommendations=result.get('recommendations', ['Execute trades during market hours', 'Consider tax implications']),
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        return FinanceApiResponse(
            status="error",
            data={},
            errors=[str(e)],
            processing_time=processing_time
        )

# ============================================================================
# FINANCIAL ANALYTICS ENDPOINTS
# ============================================================================

@app.post("/agents/chandufinance/analytics/cashflow", response_model=FinanceApiResponse)
async def analyze_cashflow(request: CashflowAnalysisRequest):
    """Analyze cash flow patterns with AI insights."""
    start_time = datetime.now(timezone.utc)
    
    try:
        # Validate consent token
        is_valid, error_msg, token_obj = validate_token(request.token, ConsentScope.VAULT_READ_FINANCE)
        if not is_valid:
            raise HTTPException(status_code=403, detail=f"Invalid consent token: {error_msg}")
        
        from hushh_mcp.agents.chandufinance.index import run_agent
        
        parameters = {
            'command': 'analyze_cashflow',
            'period_months': request.period_months,
            'include_projections': request.include_projections
        }
        
        if request.gemini_api_key:
            parameters['gemini_api_key'] = request.gemini_api_key
        
        result = run_agent(
            user_id=request.user_id,
            tokens={ConsentScope.VAULT_READ_FINANCE.value: request.token},
            parameters=parameters
        )
        
        cashflow_data = {
            'monthly_analysis': result.get('monthly_analysis', {}),
            'trends': result.get('trends', {}),
            'projections': result.get('projections', {}) if request.include_projections else {},
            'key_metrics': result.get('key_metrics', {}),
            'seasonal_patterns': result.get('seasonal_patterns', {})
        }
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        return FinanceApiResponse(
            status="success",
            data=cashflow_data,
            ai_insights=result.get('ai_insights', 'Cash flow analysis reveals important spending patterns.'),
            recommendations=result.get('recommendations', ['Optimize irregular expenses', 'Build emergency buffer']),
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        return FinanceApiResponse(
            status="error",
            data={},
            errors=[str(e)],
            processing_time=processing_time
        )

@app.post("/agents/chandufinance/analytics/spending", response_model=FinanceApiResponse)
async def analyze_spending(request: SpendingAnalysisRequest):
    """Analyze spending patterns with AI-powered insights."""
    start_time = datetime.now(timezone.utc)
    
    try:
        # Validate consent token
        is_valid, error_msg, token_obj = validate_token(request.token, ConsentScope.VAULT_READ_FINANCE)
        if not is_valid:
            raise HTTPException(status_code=403, detail=f"Invalid consent token: {error_msg}")
        
        from hushh_mcp.agents.chandufinance.index import run_agent
        
        parameters = {
            'command': 'analyze_spending',
            'transactions': request.transactions or [],
            'analysis_type': request.analysis_type
        }
        
        if request.gemini_api_key:
            parameters['gemini_api_key'] = request.gemini_api_key
        
        result = run_agent(
            user_id=request.user_id,
            tokens={ConsentScope.VAULT_READ_FINANCE.value: request.token},
            parameters=parameters
        )
        
        spending_data = {
            'category_breakdown': result.get('category_breakdown', {}),
            'spending_trends': result.get('spending_trends', {}),
            'unusual_patterns': result.get('unusual_patterns', []),
            'saving_opportunities': result.get('saving_opportunities', []),
            'behavioral_insights': result.get('behavioral_insights', {})
        }
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        return FinanceApiResponse(
            status="success",
            data=spending_data,
            ai_insights=result.get('ai_insights', 'Spending analysis reveals optimization opportunities.'),
            recommendations=result.get('recommendations', ['Reduce discretionary spending', 'Automate savings']),
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        return FinanceApiResponse(
            status="error",
            data={},
            errors=[str(e)],
            processing_time=processing_time
        )

@app.post("/agents/chandufinance/analytics/tax-optimization", response_model=FinanceApiResponse)
async def analyze_tax_optimization(request: TaxOptimizationRequest):
    """Provide AI-powered tax optimization strategies."""
    start_time = datetime.now(timezone.utc)
    
    try:
        # Validate consent token
        is_valid, error_msg, token_obj = validate_token(request.token, ConsentScope.VAULT_READ_FINANCE)
        if not is_valid:
            raise HTTPException(status_code=403, detail=f"Invalid consent token: {error_msg}")
        
        from hushh_mcp.agents.chandufinance.index import run_agent
        
        parameters = {
            'command': 'tax_optimization',
            'annual_income': request.annual_income,
            'investment_income': request.investment_income,
            'tax_year': request.tax_year
        }
        
        if request.gemini_api_key:
            parameters['gemini_api_key'] = request.gemini_api_key
        
        result = run_agent(
            user_id=request.user_id,
            tokens={ConsentScope.VAULT_READ_FINANCE.value: request.token},
            parameters=parameters
        )
        
        tax_data = {
            'current_tax_bracket': result.get('current_tax_bracket', '22%'),
            'optimization_strategies': result.get('optimization_strategies', []),
            'estimated_savings': result.get('estimated_savings', 0),
            'retirement_contributions': result.get('retirement_contributions', {}),
            'tax_loss_harvesting': result.get('tax_loss_harvesting', {})
        }
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        return FinanceApiResponse(
            status="success",
            data=tax_data,
            ai_insights=result.get('ai_insights', 'Tax optimization analysis identifies potential savings.'),
            recommendations=result.get('recommendations', ['Maximize retirement contributions', 'Consider tax-advantaged accounts']),
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        return FinanceApiResponse(
            status="error",
            data={},
            errors=[str(e)],
            processing_time=processing_time
        )

# ============================================================================
# MARKET DATA ENDPOINTS
# ============================================================================

@app.post("/agents/chandufinance/market/stock-price", response_model=FinanceApiResponse)
async def get_stock_prices(request: StockPriceRequest):
    """Get real-time stock prices with optional AI analysis."""
    start_time = datetime.now(timezone.utc)
    
    try:
        # Validate consent token
        is_valid, error_msg, token_obj = validate_token(request.token, ConsentScope.VAULT_READ_FINANCE)
        if not is_valid:
            raise HTTPException(status_code=403, detail=f"Invalid consent token: {error_msg}")
        
        from hushh_mcp.agents.chandufinance.index import run_agent
        
        parameters = {
            'command': 'get_stock_prices',
            'symbols': request.symbols,
            'include_analysis': request.include_analysis
        }
        
        if request.gemini_api_key:
            parameters['gemini_api_key'] = request.gemini_api_key
        
        result = run_agent(
            user_id=request.user_id,
            tokens={ConsentScope.VAULT_READ_FINANCE.value: request.token},
            parameters=parameters
        )
        
        stock_data = {
            'prices': result.get('prices', {}),
            'market_data': result.get('market_data', {}),
            'analysis': result.get('analysis', {}) if request.include_analysis else {},
            'last_updated': datetime.now().isoformat()
        }
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        return FinanceApiResponse(
            status="success",
            data=stock_data,
            ai_insights=result.get('ai_insights', 'Stock price data retrieved successfully.'),
            recommendations=result.get('recommendations', []) if request.include_analysis else [],
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        return FinanceApiResponse(
            status="error",
            data={},
            errors=[str(e)],
            processing_time=processing_time
        )

@app.post("/agents/chandufinance/market/portfolio-value", response_model=FinanceApiResponse)
async def get_portfolio_value(request: PortfolioValueRequest):
    """Get live portfolio valuation with performance metrics."""
    start_time = datetime.now(timezone.utc)
    
    try:
        # Validate consent token
        is_valid, error_msg, token_obj = validate_token(request.token, ConsentScope.VAULT_READ_FINANCE)
        if not is_valid:
            raise HTTPException(status_code=403, detail=f"Invalid consent token: {error_msg}")
        
        from hushh_mcp.agents.chandufinance.index import run_agent
        
        parameters = {
            'command': 'get_portfolio_value',
            'portfolio_id': request.portfolio_id,
            'include_performance': request.include_performance
        }
        
        result = run_agent(
            user_id=request.user_id,
            tokens={ConsentScope.VAULT_READ_FINANCE.value: request.token},
            parameters=parameters
        )
        
        portfolio_data = {
            'current_value': result.get('current_value', 0),
            'total_return': result.get('total_return', {}),
            'daily_change': result.get('daily_change', {}),
            'performance_metrics': result.get('performance_metrics', {}) if request.include_performance else {},
            'last_updated': datetime.now().isoformat()
        }
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        return FinanceApiResponse(
            status="success",
            data=portfolio_data,
            ai_insights=result.get('ai_insights', 'Portfolio valuation completed successfully.'),
            recommendations=result.get('recommendations', []),
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        return FinanceApiResponse(
            status="error",
            data={},
            errors=[str(e)],
            processing_time=processing_time
        )

# ============================================================================
# ADVANCED PLANNING ENDPOINTS
# ============================================================================

@app.post("/agents/chandufinance/planning/retirement", response_model=FinanceApiResponse)
async def analyze_retirement_planning(request: RetirementPlanningRequest):
    """Comprehensive retirement planning with AI insights."""
    start_time = datetime.now(timezone.utc)
    
    try:
        # Validate consent token
        is_valid, error_msg, token_obj = validate_token(request.token, ConsentScope.VAULT_READ_FINANCE)
        if not is_valid:
            raise HTTPException(status_code=403, detail=f"Invalid consent token: {error_msg}")
        
        from hushh_mcp.agents.chandufinance.index import run_agent
        
        parameters = {
            'command': 'retirement_planning',
            'current_age': request.current_age,
            'retirement_age': request.retirement_age,
            'desired_retirement_income': request.desired_retirement_income,
            'current_savings': request.current_savings
        }
        
        if request.gemini_api_key:
            parameters['gemini_api_key'] = request.gemini_api_key
        
        result = run_agent(
            user_id=request.user_id,
            tokens={ConsentScope.VAULT_READ_FINANCE.value: request.token},
            parameters=parameters
        )
        
        retirement_data = {
            'required_savings': result.get('required_savings', 0),
            'monthly_contribution_needed': result.get('monthly_contribution_needed', 0),
            'retirement_readiness_score': result.get('retirement_readiness_score', 0),
            'projection_scenarios': result.get('projection_scenarios', {}),
            'recommended_strategies': result.get('recommended_strategies', [])
        }
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        return FinanceApiResponse(
            status="success",
            data=retirement_data,
            ai_insights=result.get('ai_insights', 'Retirement planning analysis provides comprehensive roadmap.'),
            recommendations=result.get('recommendations', ['Increase savings rate', 'Diversify retirement accounts']),
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        return FinanceApiResponse(
            status="error",
            data={},
            errors=[str(e)],
            processing_time=processing_time
        )

@app.post("/agents/chandufinance/planning/emergency-fund", response_model=FinanceApiResponse)
async def analyze_emergency_fund(request: EmergencyFundRequest):
    """Emergency fund analysis with personalized recommendations."""
    start_time = datetime.now(timezone.utc)
    
    try:
        # Validate consent token
        is_valid, error_msg, token_obj = validate_token(request.token, ConsentScope.VAULT_READ_FINANCE)
        if not is_valid:
            raise HTTPException(status_code=403, detail=f"Invalid consent token: {error_msg}")
        
        from hushh_mcp.agents.chandufinance.index import run_agent
        
        parameters = {
            'command': 'emergency_fund_analysis',
            'monthly_expenses': request.monthly_expenses,
            'current_emergency_fund': request.current_emergency_fund,
            'risk_profile': request.risk_profile
        }
        
        if request.gemini_api_key:
            parameters['gemini_api_key'] = request.gemini_api_key
        
        result = run_agent(
            user_id=request.user_id,
            tokens={ConsentScope.VAULT_READ_FINANCE.value: request.token},
            parameters=parameters
        )
        
        emergency_data = {
            'recommended_amount': result.get('recommended_amount', request.monthly_expenses * 6),
            'current_coverage_months': result.get('current_coverage_months', 0),
            'funding_gap': result.get('funding_gap', 0),
            'recommended_timeline': result.get('recommended_timeline', '12 months'),
            'best_accounts': result.get('best_accounts', [])
        }
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        return FinanceApiResponse(
            status="success",
            data=emergency_data,
            ai_insights=result.get('ai_insights', 'Emergency fund analysis provides security assessment.'),
            recommendations=result.get('recommendations', ['Build emergency fund gradually', 'Use high-yield savings account']),
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        return FinanceApiResponse(
            status="error",
            data={},
            errors=[str(e)],
            processing_time=processing_time
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
    
    # Dynamic API key support
    gemini_api_key: Optional[str] = Field(None, description="Dynamic Gemini API key for LLM operations")
    api_keys: Optional[Dict[str, str]] = Field(None, description="Additional API keys for various services")

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
        
        # Extract dynamic API keys for agent initialization
        api_keys = {}
        if request.gemini_api_key:
            api_keys['gemini_api_key'] = request.gemini_api_key
        if request.api_keys:
            api_keys.update(request.api_keys)
            
        # Execute the agent with dynamic API keys
        result = run(
            user_id=request.user_id,
            tokens=request.tokens,
            user_input=request.user_input,
            vault_key=request.vault_key,
            is_startup=request.is_startup,
            **api_keys  # Pass API keys as keyword arguments
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
# RELATIONSHIP MEMORY AGENT - INTERACTIVE CHAT ENDPOINTS
# ============================================================================

# In-memory session storage (for production, use Redis or database)
chat_sessions: Dict[str, Dict[str, Any]] = {}

class ChatSessionRequest(BaseModel):
    """Request model for starting a new chat session."""
    user_id: str = Field(..., min_length=1, description="User identifier")
    tokens: Dict[str, str] = Field(..., description="Dictionary of consent tokens for various scopes")
    vault_key: Optional[str] = Field(None, description="Specific vault key for data access")
    session_name: Optional[str] = Field("default", description="Name for the chat session")
    
    # Dynamic API key support
    gemini_api_key: Optional[str] = Field(None, description="Dynamic Gemini API key for LLM operations")
    api_keys: Optional[Dict[str, str]] = Field(None, description="Additional API keys for various services")

class ChatSessionResponse(BaseModel):
    """Response model for chat session operations."""
    status: str
    session_id: str
    user_id: str
    message: str
    session_info: Optional[Dict[str, Any]] = None

class ChatMessageRequest(BaseModel):
    """Request model for sending a chat message."""
    user_id: str = Field(..., min_length=1, description="User ID")
    message: str = Field(..., min_length=1, description="User message")
    session_id: Optional[str] = Field(None, description="Chat session ID")
    consent_tokens: Optional[Dict[str, str]] = Field(None, description="Consent tokens")

class ChatMessageResponse(BaseModel):
    """Response model for chat messages."""
    status: str
    session_id: str
    user_message: str
    agent_response: str
    conversation_count: int
    processing_time: float
    timestamp: str

class ChatHistoryResponse(BaseModel):
    """Response model for chat history."""
    status: str
    session_id: str
    conversation_history: List[Dict[str, Any]]
    total_messages: int

@app.post("/agents/relationship_memory/chat/start", response_model=ChatSessionResponse)
async def start_relationship_memory_chat(request: ChatSessionRequest):
    """Start a new interactive chat session with the Relationship Memory agent."""
    try:
        # Generate unique session ID
        session_id = f"{request.user_id}_{request.session_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize session data
        session_data = {
            "user_id": request.user_id,
            "tokens": request.tokens,
            "vault_key": request.vault_key,
            "session_name": request.session_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "conversation_history": [],
            "conversation_count": 0,
            "api_keys": {}
        }
        
        # Store dynamic API keys
        if request.gemini_api_key:
            session_data["api_keys"]["gemini_api_key"] = request.gemini_api_key
        if request.api_keys:
            session_data["api_keys"].update(request.api_keys)
        
        # Store session
        chat_sessions[session_id] = session_data
        
        return ChatSessionResponse(
            status="success",
            session_id=session_id,
            user_id=request.user_id,
            message=f"Interactive chat session started successfully. Session ID: {session_id}",
            session_info={
                "session_name": request.session_name,
                "created_at": session_data["created_at"],
                "available_commands": [
                    "Add contacts: 'add John with email john@example.com'",
                    "Add memories: 'remember that Sarah loves photography'",
                    "Set reminders: 'remind me to call Mike tomorrow'",
                    "Show data: 'show my contacts', 'show memories'",
                    "Get advice: 'what should I get John for his birthday?'",
                    "Proactive check: 'proactive check'"
                ]
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start chat session: {str(e)}"
        )

@app.post("/agents/relationship_memory/chat/message", response_model=ChatMessageResponse)
async def send_relationship_memory_chat_message(request: ChatMessageRequest):
    """Send a message in an existing chat session."""
    start_time = datetime.now(timezone.utc)
    
    # Check if session exists
    if request.session_id not in chat_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session {request.session_id} not found"
        )
    
    session_data = chat_sessions[request.session_id]
    
    try:
        # Import and execute the Relationship Memory agent
        from hushh_mcp.agents.relationship_memory.index import run
        
        # Execute the agent with session context
        result = run(
            user_id=session_data["user_id"],
            tokens=session_data["tokens"],
            user_input=request.message,
            vault_key=session_data["vault_key"],
            is_startup=False,
            **session_data["api_keys"]  # Pass stored API keys
        )
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Extract agent response
        agent_response = result.get("message", "No response from agent")
        
        # Update conversation history
        session_data["conversation_count"] += 1
        conversation_entry = {
            "id": session_data["conversation_count"],
            "timestamp": timestamp,
            "user_message": request.message,
            "agent_response": agent_response,
            "agent_result": result,
            "processing_time": processing_time
        }
        session_data["conversation_history"].append(conversation_entry)
        
        # Keep only last 50 messages to prevent memory bloat
        if len(session_data["conversation_history"]) > 50:
            session_data["conversation_history"] = session_data["conversation_history"][-50:]
        
        return ChatMessageResponse(
            status="success",
            session_id=request.session_id,
            user_message=request.message,
            agent_response=agent_response,
            conversation_count=session_data["conversation_count"],
            processing_time=processing_time,
            timestamp=timestamp
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(e)}"
        )

@app.get("/agents/relationship_memory/chat/{session_id}/history", response_model=ChatHistoryResponse)
async def get_relationship_memory_chat_history(session_id: str):
    """Get the conversation history for a chat session."""
    if session_id not in chat_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session {session_id} not found"
        )
    
    session_data = chat_sessions[session_id]
    
    return ChatHistoryResponse(
        status="success",
        session_id=session_id,
        conversation_history=session_data["conversation_history"],
        total_messages=session_data["conversation_count"]
    )

@app.delete("/agents/relationship_memory/chat/{session_id}")
async def end_relationship_memory_chat(session_id: str):
    """End a chat session and clean up resources."""
    if session_id not in chat_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session {session_id} not found"
        )
    
    session_data = chat_sessions.pop(session_id)
    
    return {
        "status": "success",
        "message": f"Chat session {session_id} ended successfully",
        "session_summary": {
            "total_messages": session_data["conversation_count"],
            "duration": f"Started at {session_data['created_at']}",
            "user_id": session_data["user_id"]
        }
    }

@app.get("/agents/relationship_memory/chat/sessions")
async def list_relationship_memory_chat_sessions():
    """List all active chat sessions."""
    sessions_info = []
    for session_id, session_data in chat_sessions.items():
        sessions_info.append({
            "session_id": session_id,
            "user_id": session_data["user_id"],
            "session_name": session_data["session_name"],
            "created_at": session_data["created_at"],
            "conversation_count": session_data["conversation_count"],
            "last_activity": session_data["conversation_history"][-1]["timestamp"] if session_data["conversation_history"] else session_data["created_at"]
        })
    
    return {
        "status": "success",
        "active_sessions": len(sessions_info),
        "sessions": sessions_info
    }
# RESEARCH AGENT ENDPOINTS
# ============================================================================

class ArxivSearchRequest(BaseModel):
    """Request model for arXiv search."""
    user_id: str = Field(..., description="User identifier")
    consent_tokens: Dict[str, str] = Field(..., description="Consent tokens for required scopes")
    query: str = Field(..., description="Natural language research query")

class SnippetProcessRequest(BaseModel):
    """Request model for snippet processing."""
    user_id: str = Field(..., description="User identifier")
    consent_tokens: Dict[str, str] = Field(..., description="Consent tokens for required scopes")
    text: str = Field(..., description="Text snippet to process")
    instruction: str = Field(..., description="Processing instruction")

class NotesRequest(BaseModel):
    """Request model for saving notes."""
    user_id: str = Field(..., description="User identifier")
    consent_tokens: Dict[str, str] = Field(..., description="Consent tokens for required scopes")
    paper_id: str = Field(..., description="Paper identifier")
    editor_id: str = Field(..., description="Editor identifier")
    content: str = Field(..., description="Note content")

@app.post("/agents/research/search/arxiv", response_model=AgentResponse)
async def research_search_arxiv(request: ArxivSearchRequest):
    """
    Search arXiv papers using natural language query optimization.
    
    The research agent will convert natural language queries into optimized
    arXiv search terms for better results.
    """
    start_time = datetime.now(timezone.utc)
    
    try:
        # Import research agent
        from hushh_mcp.agents.research_agent.index import research_agent
        
        # Validate consent tokens
        required_scopes = [ConsentScope.CUSTOM_TEMPORARY]
        for scope in required_scopes:
            scope_key = scope.value
            if scope_key not in request.consent_tokens:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing consent token for scope: {scope_key}"
                )
            
            token = request.consent_tokens[scope_key]
            is_valid, error_msg, token_obj = validate_token(token, scope)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Invalid consent token for scope: {scope_key} - {error_msg}"
                )
        
        # Execute search
        result = await research_agent.search_arxiv(
            user_id=request.user_id,
            consent_tokens=request.consent_tokens,
            query=request.query
        )
        
        return {
            "status": "success" if result["success"] else "error",
            "agent_id": "research_agent",
            "user_id": request.user_id,
            "session_id": result["session_id"],
            "results": {
                "query": result.get("query"),
                "papers": result.get("results", []),
                "total_found": result.get("total_papers", 0)
            },
            "errors": [result["error"]] if result.get("error") else [],
            "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error",
            "agent_id": "research_agent",
            "user_id": request.user_id,
            "errors": [str(e)],
            "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
        }

@app.post("/agents/research/upload")
async def research_upload_paper(
    user_id: str,
    consent_tokens: str,  # JSON string
    file: UploadFile = File(...)
):
    """Upload PDF paper for processing."""
    start_time = datetime.now(timezone.utc)
    
    try:
        import json
        consent_tokens_dict = json.loads(consent_tokens)
        
        # Import research agent
        from hushh_mcp.agents.research_agent.index import research_agent
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported"
            )
        
        # Validate consent tokens
        required_scopes = [ConsentScope.VAULT_READ_FILE, ConsentScope.VAULT_WRITE_FILE]
        for scope in required_scopes:
            scope_key = scope.value
            if scope_key not in consent_tokens_dict:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing consent token for scope: {scope_key}"
                )
        
        # Generate paper ID
        import uuid
        paper_id = f"paper_{uuid.uuid4().hex[:12]}"
        
        # Process upload
        result = await research_agent.process_pdf_upload(
            user_id=user_id,
            consent_tokens=consent_tokens_dict,
            paper_id=paper_id,
            pdf_file=file
        )
        
        return {
            "status": "success" if result["success"] else "error",
            "agent_id": "research_agent",
            "user_id": user_id,
            "session_id": result["session_id"],
            "results": {
                "paper_id": result.get("paper_id"),
                "text_length": result.get("text_extracted", 0)
            },
            "errors": [result["error"]] if result.get("error") else [],
            "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error",
            "agent_id": "research_agent",
            "user_id": user_id,
            "errors": [str(e)],
            "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
        }

@app.get("/agents/research/paper/{paper_id}/summary", response_model=AgentResponse)
async def research_get_summary(
    paper_id: str,
    user_id: str,
    consent_tokens: str  # JSON string of tokens
):
    """Generate AI-powered summary of research paper."""
    start_time = datetime.now(timezone.utc)
    
    try:
        import json
        consent_tokens_dict = json.loads(consent_tokens)
        
        # Import research agent
        from hushh_mcp.agents.research_agent.index import research_agent
        
        # Validate consent tokens
        required_scopes = [ConsentScope.VAULT_READ_FILE, ConsentScope.VAULT_WRITE_FILE, ConsentScope.CUSTOM_TEMPORARY]
        for scope in required_scopes:
            scope_key = scope.value
            if scope_key not in consent_tokens_dict:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing consent token for scope: {scope_key}"
                )
        
        # Generate summary
        result = await research_agent.generate_paper_summary(
            user_id=user_id,
            consent_tokens=consent_tokens_dict,
            paper_id=paper_id
        )
        
        return {
            "status": "success" if result["success"] else "error",
            "agent_id": "research_agent",
            "user_id": user_id,
            "session_id": result["session_id"],
            "results": {
                "paper_id": result.get("paper_id"),
                "summary": result.get("summary")
            },
            "errors": [result["error"]] if result.get("error") else [],
            "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error",
            "agent_id": "research_agent", 
            "user_id": user_id,
            "errors": [str(e)],
            "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
        }

@app.post("/agents/research/paper/{paper_id}/process/snippet", response_model=AgentResponse)
async def research_process_snippet(
    paper_id: str,
    request: SnippetProcessRequest
):
    """Process text snippet with custom instruction."""
    start_time = datetime.now(timezone.utc)
    
    try:
        # Import research agent
        from hushh_mcp.agents.research_agent.index import research_agent
        
        # Validate consent tokens
        required_scopes = [ConsentScope.CUSTOM_TEMPORARY]
        for scope in required_scopes:
            scope_key = scope.value
            if scope_key not in request.consent_tokens:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing consent token for scope: {scope_key}"
                )
        
        # Process snippet
        result = await research_agent.process_text_snippet(
            user_id=request.user_id,
            consent_tokens=request.consent_tokens,
            paper_id=paper_id,
            snippet=request.text,
            instruction=request.instruction
        )
        
        return {
            "status": "success" if result["success"] else "error",
            "agent_id": "research_agent",
            "user_id": request.user_id,
            "session_id": result["session_id"],
            "results": {
                "paper_id": result.get("paper_id"),
                "original_snippet": result.get("original_snippet"),
                "instruction": result.get("instruction"),
                "processed_result": result.get("processed_result")
            },
            "errors": [result["error"]] if result.get("error") else [],
            "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error",
            "agent_id": "research_agent",
            "user_id": request.user_id,
            "errors": [str(e)],
            "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
        }

@app.post("/agents/research/session/notes", response_model=AgentResponse)
async def research_save_notes(request: NotesRequest):
    """Save notes to vault storage."""
    start_time = datetime.now(timezone.utc)
    
    try:
        # Import research agent
        from hushh_mcp.agents.research_agent.index import research_agent
        
        # Validate consent tokens
        required_scopes = [ConsentScope.VAULT_WRITE_FILE]
        for scope in required_scopes:
            scope_key = scope.value
            if scope_key not in request.consent_tokens:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing consent token for scope: {scope_key}"
                )
        
        # Save notes
        result = await research_agent.save_session_notes(
            user_id=request.user_id,
            consent_tokens=request.consent_tokens,
            paper_id=request.paper_id,
            editor_id=request.editor_id,
            content=request.content
        )
        
        return {
            "status": "success" if result["success"] else "error",
            "agent_id": "research_agent",
            "user_id": request.user_id,
            "session_id": result["session_id"],
            "results": {
                "paper_id": result.get("paper_id"),
                "editor_id": result.get("editor_id"),
                "content_length": result.get("content_length")
            },
            "errors": [result["error"]] if result.get("error") else [],
            "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error",
            "agent_id": "research_agent",
            "user_id": request.user_id,
            "errors": [str(e)],
            "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
        }

@app.get("/agents/research/status", response_model=AgentStatusResponse)
async def get_research_agent_status():
    """Get Research agent status and requirements."""
    return AgentStatusResponse(
        agent_id="agent_research",
        name="Research Agent",
        version="1.0.0",
        status="available",
        required_scopes=[
            "custom.temporary", "vault.read.file", "vault.write.file"
        ],
        required_inputs={
            "query": "Natural language research query for arXiv search",
            "paper_file": "PDF file for upload and processing",
            "text_snippet": "Text snippet for AI processing",
            "instruction": "Processing instruction for snippets"
        }
    )

# ============================================================================
# SIMPLIFIED RESEARCH ENDPOINTS FOR FRONTEND
# ============================================================================

class SimpleSearchRequest(BaseModel):
    """Simplified search request for frontend."""
    query: str = Field(..., description="Search query")
    user_id: str = Field(default="demo_user", description="User ID")

class SimpleChatRequest(BaseModel):
    """Simplified chat request for frontend."""
    message: str = Field(..., description="Chat message")
    paper_id: str = Field(..., description="Paper ID")
    user_id: str = Field(default="demo_user", description="User ID")
    conversation_history: List[Dict[str, str]] = Field(default=[], description="Chat history")

@app.get("/test/arxiv")
async def test_arxiv_direct():
    """Test arXiv API directly without workflow."""
    try:
        import requests
        import feedparser
        
        query = "machine learning"
        base_url = "http://export.arxiv.org/api/query?"
        search_query = f"search_query=all:{query}"
        params = f"{search_query}&start=0&max_results=5&sortBy=relevance&sortOrder=descending"
        
        print(f"Testing arXiv API with query: {query}")
        response = requests.get(f"{base_url}{params}", timeout=10)
        
        if response.status_code != 200:
            return {"error": f"arXiv API error: {response.status_code}"}
        
        feed = feedparser.parse(response.content)
        papers = []
        
        for entry in feed.entries:
            arxiv_id = entry.id.split('/abs/')[-1] if '/abs/' in entry.id else entry.id
            authors = []
            if hasattr(entry, 'authors'):
                authors = [author.name for author in entry.authors]
            
            paper = {
                "id": arxiv_id,
                "title": entry.title.replace('\n', ' ').strip(),
                "authors": authors,
                "summary": entry.summary.replace('\n', ' ').strip()[:300] + "...",
                "published": getattr(entry, 'published', '')[:10],
                "arxiv_id": arxiv_id
            }
            papers.append(paper)
        
        return {
            "status": "success",
            "query": query,
            "papers": papers,
            "total": len(papers)
        }
        
    except Exception as e:
        return {"error": f"Test failed: {str(e)}"}

@app.post("/research/search")
async def simple_research_search(request: SimpleSearchRequest):
    """
    Simplified research search endpoint for frontend integration.
    Uses direct arXiv API call for immediate results.
    """
    print(f"🔍 Starting search for: {request.query}")
    
    try:
        import requests
        import feedparser
        
        query = request.query.replace(" ", "+")  # URL encode spaces
        
        # Direct arXiv API call with timeout
        base_url = "http://export.arxiv.org/api/query?"
        search_query = f"search_query=all:{query}"
        params = f"{search_query}&start=0&max_results=10&sortBy=relevance&sortOrder=descending"
        
        print(f"🌐 Calling arXiv API: {base_url}{params}")
        response = requests.get(f"{base_url}{params}", timeout=15)
        print(f"✅ arXiv API responded with status: {response.status_code}")
        
        if response.status_code != 200:
            raise Exception(f"arXiv API error: {response.status_code}")
        
        # Parse XML response
        print("📝 Parsing XML response...")
        feed = feedparser.parse(response.content)
        print(f"📊 Found {len(feed.entries)} entries")
        
        papers = []
        for i, entry in enumerate(feed.entries):
            print(f"Processing entry {i+1}...")
            
            # Extract authors
            authors = []
            if hasattr(entry, 'authors'):
                authors = [author.name for author in entry.authors]
            elif hasattr(entry, 'author'):
                authors = [entry.author]
            
            # Extract arXiv ID
            arxiv_id = entry.id.split('/abs/')[-1] if '/abs/' in entry.id else entry.id
            
            # Extract categories
            categories = []
            if hasattr(entry, 'tags'):
                categories = [tag.term for tag in entry.tags]
            
            paper = {
                "id": arxiv_id,
                "title": entry.title.replace('\n', ' ').strip(),
                "authors": authors,
                "summary": entry.summary.replace('\n', ' ').strip(),
                "published": getattr(entry, 'published', '')[:10] if hasattr(entry, 'published') else "Unknown",
                "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                "arxiv_id": arxiv_id,
                "categories": categories[:3]  # Limit categories
            }
            papers.append(paper)
        
        print(f"🎉 Successfully processed {len(papers)} papers")
        
        result = {
            "query": request.query,
            "papers": papers,
            "metadata": {
                "total_found": len(papers),
                "search_time": 0.5,
                "optimized_query": request.query
            }
        }
        
        print(f"📤 Returning result with {len(papers)} papers")
        return result
            
    except requests.exceptions.Timeout:
        print("⏰ arXiv API timeout")
        return {
            "query": request.query,
            "papers": [],
            "metadata": {
                "total_found": 0,
                "search_time": 0.0,
                "optimized_query": request.query,
                "error": "Search timed out"
            }
        }
    except Exception as e:
        print(f"❌ Search error: {e}")
        return {
            "query": request.query,
            "papers": [],
            "metadata": {
                "total_found": 0,
                "search_time": 0.0,
                "optimized_query": request.query,
                "error": str(e)
            }
        }

@app.post("/research/chat")
async def simple_research_chat(request: SimpleChatRequest):
    """
    Simplified chat endpoint for frontend integration.
    Automatically handles consent tokens for demo purposes.
    """
    try:
        # Import research agent
        from hushh_mcp.agents.research_agent.index import research_agent
        
        # Create temporary consent tokens for demo
        consent_tokens = {
            "custom.temporary": "demo_token",
            "vault.read.file": "demo_token",
            "vault.write.file": "demo_token"
        }
        
        # Execute chat with research agent
        result = await research_agent.chat_about_paper(
            user_id=request.user_id,
            consent_tokens=consent_tokens,
            paper_id=request.paper_id,
            message=request.message,
            conversation_history=request.conversation_history
        )
        
        if result["success"]:
            return {
                "response": result.get("response", "I'm sorry, I couldn't process your message."),
                "paper_id": request.paper_id,
                "conversation_id": result.get("session_id")
            }
        else:
            return {
                "response": "I'm sorry, I encountered an error processing your message. Please try again.",
                "paper_id": request.paper_id,
                "error": result.get("error")
            }
            
    except Exception as e:
        print(f"Chat error: {e}")
        return {
            "response": "I'm sorry, I encountered a technical error. Please try again later.",
            "paper_id": request.paper_id,
            "error": str(e)
        }

@app.get("/research/paper/{paper_id}/content")
async def get_paper_content(paper_id: str):
    """
    Fetch and extract content from a paper PDF.
    Returns the full text content of the paper.
    """
    print(f"📄 Fetching content for paper: {paper_id}")
    
    try:
        import requests
        import PyPDF2
        from io import BytesIO
        
        # Construct PDF URL
        pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
        print(f"🌐 Downloading PDF from: {pdf_url}")
        
        # Download PDF with timeout
        response = requests.get(pdf_url, timeout=30)
        
        if response.status_code != 200:
            raise Exception(f"Failed to download PDF: {response.status_code}")
        
        print(f"✅ PDF downloaded, size: {len(response.content)} bytes")
        
        # Extract text from PDF
        pdf_file = BytesIO(response.content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text_content = ""
        total_pages = len(pdf_reader.pages)
        print(f"📖 Extracting text from {total_pages} pages...")
        
        for page_num in range(total_pages):
            try:
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                text_content += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            except Exception as e:
                print(f"⚠️ Error extracting page {page_num + 1}: {e}")
                text_content += f"\n--- Page {page_num + 1} ---\n[Error extracting text from this page]\n"
        
        print(f"✅ Extracted {len(text_content)} characters from PDF")
        
        # Clean up the text
        cleaned_text = text_content.replace('\x00', '').strip()
        
        return {
            "paper_id": paper_id,
            "content": cleaned_text,
            "pages": total_pages,
            "content_length": len(cleaned_text),
            "pdf_url": pdf_url,
            "status": "success"
        }
        
    except requests.exceptions.Timeout:
        print("⏰ PDF download timed out")
        return {
            "paper_id": paper_id,
            "content": "Error: PDF download timed out. The paper may be too large or the server is slow.",
            "error": "timeout",
            "status": "error"
        }
    except Exception as e:
        print(f"❌ Error fetching paper content: {e}")
        return {
            "paper_id": paper_id,
            "content": f"Error loading paper content: {str(e)}",
            "error": str(e),
            "status": "error"
        }

# ============================================================================
# MAIN APPLICATION
# ============================================================================

# ============================================================================
# GENERAL CHAT AGENT ENDPOINTS  
# ============================================================================

@app.post("/agents/chat/message", response_model=Dict[str, Any])
async def general_chat_message(request: ChatMessageRequest):
    """
    General chat endpoint that routes to appropriate agents based on message content.
    This provides a unified interface for all agent interactions through chat.
    """
    start_time = datetime.now(timezone.utc)
    
    try:
        # Validate request
        user_id = getattr(request, 'user_id', None)
        message = getattr(request, 'message', None)
        session_id = getattr(request, 'session_id', None)
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        user_message = message.lower().strip()
        
        # Simple routing based on message content keywords
        # Finance-related keywords
        if any(keyword in user_message for keyword in [
            'finance', 'financial', 'money', 'income', 'expense', 'budget', 
            'investment', 'stock', 'portfolio', 'analysis', 'goal', 'saving'
        ]):
            try:
                # Process financial query using enhanced index
                # Extract financial information from the message
                import re
                income_match = re.search(r'income[:\s]*\$?(\d+)', user_message)
                expense_match = re.search(r'expense[s]?[:\s]*\$?(\d+)', user_message)
                net_match = re.search(r'net[:\s]*\$?(\d+)', user_message)
                
                analysis_prompt = f"""
Financial Analysis for: {message}

Based on your financial query, here's my analysis:

"""
                
                if income_match and expense_match:
                    income = int(income_match.group(1))
                    expenses = int(expense_match.group(1))
                    net = income - expenses
                    
                    analysis_prompt += f"""
💰 **Your Financial Snapshot:**
- Monthly Income: ${income:,}
- Monthly Expenses: ${expenses:,}
- Net Income: ${net:,}

📊 **Financial Health Analysis:**
- Savings Rate: {(net/income*100):.1f}% (Excellent if >20%, Good if >10%)
- Expense Ratio: {(expenses/income*100):.1f}%

💡 **Personalized Recommendations:**
"""
                    if net/income > 0.2:
                        analysis_prompt += "✅ Excellent savings rate! Consider investing surplus funds.\n"
                    elif net/income > 0.1:
                        analysis_prompt += "✅ Good savings rate! Build emergency fund first, then invest.\n"
                    else:
                        analysis_prompt += "⚠️ Low savings rate. Review expenses and find areas to cut.\n"
                    
                    analysis_prompt += f"""
🎯 **Next Steps:**
1. Build emergency fund: ${expenses*3:,} - ${expenses*6:,}
2. Invest surplus: ${max(0, net-500):,}/month recommended
3. Review and optimize largest expense categories
"""
                else:
                    analysis_prompt += """
For effective financial management:
- Track income and expenses regularly  
- Set clear, measurable financial goals
- Build an emergency fund (3-6 months of expenses)
- Consider diversified investment options
- Review and adjust your budget monthly

Please share your specific income, expenses, and goals for detailed personalized recommendations!
"""
                
                return {
                    "status": "success",
                    "response": analysis_prompt,
                    "agent_used": "chandufinance",
                    "session_id": session_id or f"chat_{int(start_time.timestamp())}",
                    "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
                }
                
            except Exception as e:
                return {
                    "status": "success",
                    "response": f"I can help with your financial query! For effective financial management, consider tracking your income and expenses, setting clear financial goals, and building an emergency fund. Would you like specific advice on budgeting, investments, or financial planning?",
                    "agent_used": "chandufinance",
                    "session_id": session_id or f"chat_{int(start_time.timestamp())}",
                    "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
                }
        
        # Relationship/contact-related keywords  
        elif any(keyword in user_message for keyword in [
            'contact', 'relationship', 'friend', 'family', 'remember', 'reminder',
            'birthday', 'anniversary', 'meeting', 'person', 'people', 'add'
        ]):
            try:
                response_text = f"I can help you manage relationships and contacts! Based on your request to '{message}', I can assist with:\n\n" \
                              "✅ Adding new contacts with details\n" \
                              "✅ Setting reminders for important dates\n" \
                              "✅ Organizing personal connections\n" \
                              "✅ Tracking interactions and memories\n\n" \
                              "What specific action would you like me to take with your contacts or relationships?"
                
                return {
                    "status": "success", 
                    "response": response_text,
                    "agent_used": "relationship_memory",
                    "session_id": session_id or f"chat_{int(start_time.timestamp())}",
                    "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
                }
                
            except Exception as e:
                return {
                    "status": "success",
                    "response": f"I can help you manage relationships and contacts! What specific action would you like me to take?",
                    "agent_used": "relationship_memory", 
                    "session_id": session_id or f"chat_{int(start_time.timestamp())}",
                    "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
                }
        
        # Research-related keywords
        elif any(keyword in user_message for keyword in [
            'research', 'paper', 'study', 'academic', 'arxiv', 'journal',
            'publication', 'article', 'scientific', 'search'
        ]):
            try:
                response_text = f"I can help with research! Based on your query '{message}', I can:\n\n" \
                              "🔍 Search academic databases and arXiv\n" \
                              "📄 Analyze research papers and documents\n" \
                              "💡 Provide research insights and summaries\n" \
                              "📚 Help organize your research notes\n\n" \
                              "Would you like me to search for specific topics or analyze particular papers?"
                
                return {
                    "status": "success",
                    "response": response_text,
                    "agent_used": "research",
                    "session_id": session_id or f"chat_{int(start_time.timestamp())}",
                    "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
                }
                
            except Exception as e:
                return {
                    "status": "success",
                    "response": f"I can help with research! I have access to academic databases and can search for papers related to your query. What specific research topic are you interested in?",
                    "agent_used": "research",
                    "session_id": session_id or f"chat_{int(start_time.timestamp())}",
                    "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
                }
        
        # Default general response with agent suggestions
        else:
            return {
                "status": "success",
                "response": """I'm ready to help you! I can assist with:

🧮 **Financial Analysis** - Ask about budgets, investments, financial goals, or income/expense analysis
👥 **Relationship Management** - Add contacts, set reminders, or manage personal relationships  
📚 **Research** - Search academic papers, analyze documents, or find scientific information
📧 **Email Campaigns** - Create and manage mass email campaigns (use the MailerPanda agent)
📅 **Calendar Management** - Extract events from emails and manage your schedule

What would you like help with today?""",
                "agent_used": "general",
                "session_id": request.session_id or f"chat_{int(start_time.timestamp())}",
                "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"General chat error: {str(e)}")
        return {
            "status": "error",
            "response": f"I encountered an unexpected error: {str(e)}. Please try again.",
            "error": str(e),
            "session_id": request.session_id or f"chat_{int(start_time.timestamp())}",
            "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
        }

@app.get("/agents/chat/status", response_model=AgentStatusResponse)
async def get_general_chat_status():
    """Get general chat agent status."""
    return AgentStatusResponse(
        agent_id="agent_chat",
        name="General Chat Agent",
        version="1.0.0",
        status="available",
        required_scopes=["custom.temporary"],
        required_inputs={
            "user_id": "User identifier",
            "message": "Chat message content"
        }
    )

@app.get("/agents/chat/sessions/{session_id}")
async def get_chat_session(session_id: str):
    """Get chat session details."""
    # For now, return a simple response to avoid 404 errors
    # In a real implementation, this would fetch session data
    return {
        "session_id": session_id,
        "status": "active",
        "created_at": "2025-08-24T00:00:00Z",
        "messages": []
    }

@app.get("/agents/chat/sessions/{user_id}/list")
async def get_user_chat_sessions(user_id: str):
    """Get user's chat sessions."""
    # For now, return empty list to avoid 404 errors
    # In a real implementation, this would fetch user's sessions
    return {
        "user_id": user_id,
        "sessions": []
    }

if __name__ == "__main__":
    print("Starting HushMCP Agent API Server...")
    print("API Documentation: http://127.0.0.1:8001/docs")
    print("Alternative Docs: http://127.0.0.1:8001/redoc")
    print("Supported Agents:")
    print("   - AddToCalendar Agent: /agents/addtocalendar/")
    print("   - MailerPanda Agent: /agents/mailerpanda/")
    print("   - ChanduFinance Agent: /agents/chandufinance/")
    print("   - Relationship Memory Agent: /agents/relationship_memory/")
    print("   - Research Agent: /agents/research/")
    print("   - General Chat Agent: /agents/chat/")
    
    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8001,
        reload=False,
        log_level="info"
    )
