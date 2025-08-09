#!/usr/bin/env python3
"""
HushMCP Agent API Server
=======================

A FastAPI-based REST API server for interacting with HushMCP agents.
Designed to be scalable and support multiple agents with a unified interface.

Features:
- Agent registry and discovery
- Consent token validation
- Async request handling
- Comprehensive error handling
- API documentation with Swagger
- Request/response validation with Pydantic
- Agent health monitoring
"""

import os
import sys
import asyncio
import importlib
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import uvicorn

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# HushMCP framework imports
from hushh_mcp.consent.token import validate_token, issue_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.config import SECRET_KEY, ENVIRONMENT
from hushh_mcp.frontend_integration import frontend_integration, CredentialRequest, ConsentRequest

# Initialize FastAPI app
app = FastAPI(
    title="HushMCP Agent API",
    description="Privacy-first AI agent orchestration platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware for web interface integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Configuration is already loaded in hushh_mcp.config module

# ==================== PYDANTIC MODELS ====================

class ConsentTokenRequest(BaseModel):
    """Request model for consent token generation."""
    user_id: str = Field(..., description="Unique user identifier")
    scopes: List[str] = Field(..., description="List of consent scopes")
    duration_hours: int = Field(default=24, description="Token validity duration in hours")

class ConsentTokenResponse(BaseModel):
    """Response model for consent token generation."""
    token: str = Field(..., description="Generated consent token")
    expires_at: datetime = Field(..., description="Token expiration timestamp")
    scopes: List[str] = Field(..., description="Granted scopes")

class AgentRequest(BaseModel):
    """Base model for agent requests."""
    user_id: str = Field(..., description="User identifier")
    agent_id: str = Field(..., description="Agent identifier")
    consent_tokens: Dict[str, str] = Field(..., description="Required consent tokens")
    parameters: Dict[str, Any] = Field(default={}, description="Agent-specific parameters")

class AgentResponse(BaseModel):
    """Base model for agent responses."""
    status: str = Field(..., description="Request status")
    agent_id: str = Field(..., description="Agent that processed the request")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
    error: Optional[str] = Field(default=None, description="Error message if any")

class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    agents_available: int
    version: str

class AgentInfo(BaseModel):
    """Agent information model."""
    id: str
    name: str
    description: str
    version: str
    required_scopes: List[str]
    status: str

# ==================== AGENT REGISTRY ====================

class AgentRegistry:
    """Registry for managing available agents."""
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self._load_agents()
    
    def _load_agents(self):
        """Dynamically load all available agents."""
        # Update the agents directory path to be relative to current working directory
        current_dir = Path(__file__).parent
        agents_dir = current_dir / "hushh_mcp" / "agents"
        
        for agent_path in agents_dir.iterdir():
            if agent_path.is_dir() and (agent_path / "index.py").exists():
                try:
                    agent_module = f"hushh_mcp.agents.{agent_path.name}.index"
                    module = importlib.import_module(agent_module)
                    
                    # Look for agent classes (ending with 'Agent')
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            attr_name.endswith('Agent') and 
                            hasattr(attr, 'handle')):
                            
                            agent_instance = attr()
                            self.agents[agent_instance.agent_id] = {
                                'instance': agent_instance,
                                'class': attr,
                                'module': module,
                                'path': agent_path
                            }
                            print(f"✅ Loaded agent: {agent_instance.agent_id}")
                            
                except Exception as e:
                    print(f"❌ Failed to load agent from {agent_path}: {e}")
    
    def get_agent(self, agent_id: str):
        """Get agent instance by ID."""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[AgentInfo]:
        """List all available agents."""
        agent_infos = []
        for agent_id, agent_data in self.agents.items():
            try:
                manifest_module = f"hushh_mcp.agents.{agent_data['path'].name}.manifest"
                manifest = importlib.import_module(manifest_module).manifest
                
                agent_infos.append(AgentInfo(
                    id=agent_id,
                    name=manifest.get('name', agent_id),
                    description=manifest.get('description', 'No description available'),
                    version=manifest.get('version', '1.0.0'),
                    required_scopes=manifest.get('required_scopes', []),
                    status='active'
                ))
            except Exception as e:
                agent_infos.append(AgentInfo(
                    id=agent_id,
                    name=agent_id,
                    description=f'Agent loaded but manifest unavailable: {e}',
                    version='unknown',
                    required_scopes=[],
                    status='limited'
                ))
        
        return agent_infos

# Initialize agent registry
agent_registry = AgentRegistry()

# ==================== DEPENDENCY INJECTION ====================

async def verify_consent_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify consent token from Authorization header."""
    token = credentials.credentials
    is_valid, reason, _ = validate_token(token)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid consent token: {reason}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token

# ==================== API ENDPOINTS ====================

@app.get("/", response_model=HealthCheckResponse)
async def root():
    """Health check and API info endpoint."""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        agents_available=len(agent_registry.agents),
        version="1.0.0"
    )

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Detailed health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        agents_available=len(agent_registry.agents),
        version="1.0.0"
    )

@app.get("/agents", response_model=List[AgentInfo])
async def list_agents():
    """List all available agents and their capabilities."""
    return agent_registry.list_agents()

@app.get("/agents/{agent_id}", response_model=AgentInfo)
async def get_agent_info(agent_id: str):
    """Get detailed information about a specific agent."""
    agent_data = agent_registry.get_agent(agent_id)
    if not agent_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' not found"
        )
    
    agents = agent_registry.list_agents()
    agent_info = next((agent for agent in agents if agent.id == agent_id), None)
    
    if not agent_info:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not retrieve info for agent '{agent_id}'"
        )
    
    return agent_info

@app.post("/consent/token", response_model=ConsentTokenResponse)
async def generate_consent_token(request: ConsentTokenRequest):
    """Generate a consent token for agent operations."""
    try:
        # Convert string scopes to ConsentScope enums
        scope_enums = []
        for scope_str in request.scopes:
            try:
                scope_enum = ConsentScope(scope_str)
                scope_enums.append(scope_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid consent scope: {scope_str}"
                )
        
        token, expires_at = issue_token(
            user_id=request.user_id,
            scopes=scope_enums,
            duration_hours=request.duration_hours
        )
        
        return ConsentTokenResponse(
            token=token,
            expires_at=expires_at,
            scopes=request.scopes
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like invalid scope validation)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate consent token: {str(e)}"
        )

@app.post("/agents/{agent_id}/execute", response_model=AgentResponse)
async def execute_agent(
    agent_id: str,
    request: AgentRequest,
    background_tasks: BackgroundTasks
):
    """Execute an agent with the provided parameters."""
    
    # Validate agent exists
    agent_data = agent_registry.get_agent(agent_id)
    if not agent_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' not found"
        )
    
    # Validate request
    if request.agent_id != agent_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent ID in request body must match URL parameter"
        )
    
    try:
        agent_instance = agent_data['instance']
        
        # Handle different agent types with their specific interfaces
        if agent_id == "addtocalendar":
            # Enhanced AddToCalendarAgent with multiple action support
            email_token = request.consent_tokens.get('email_token')
            calendar_token = request.consent_tokens.get('calendar_token')
            
            if not email_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="AddToCalendarAgent requires 'email_token' in consent_tokens"
                )
            
            # Extract action and additional parameters
            action = request.parameters.get('action', 'comprehensive_analysis')
            
            # Validate action-specific requirements
            if action in ['comprehensive_analysis', 'manual_event'] and not calendar_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Action '{action}' requires 'calendar_token' in consent_tokens"
                )
            
            if action == 'manual_event':
                event_description = request.parameters.get('event_description')
                if not event_description:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="manual_event action requires 'event_description' parameter"
                    )
            
            # Execute enhanced agent
            result = agent_instance.handle(
                user_id=request.user_id,
                email_token_str=email_token,
                calendar_token_str=calendar_token,
                action=action,
                **{k: v for k, v in request.parameters.items() 
                   if k not in ['action']}
            )
            
        elif agent_id == "mailerpanda":
            # Enhanced MailerPanda agent with comprehensive HushMCP integration
            required_tokens = {
                'email_token': ConsentScope.VAULT_READ_EMAIL,
                'file_token': ConsentScope.VAULT_READ_FILE,
                'write_token': ConsentScope.VAULT_WRITE_EMAIL,
                'temp_token': ConsentScope.CUSTOM_TEMPORARY
            }
            
            # Check for required consent tokens
            consent_tokens = {}
            missing_tokens = []
            
            for token_name, expected_scope in required_tokens.items():
                token_value = request.consent_tokens.get(token_name)
                if token_value:
                    try:
                        is_valid, reason, parsed = validate_token(token_value, expected_scope=expected_scope)
                        if is_valid and parsed.user_id == request.user_id:
                            consent_tokens[token_name] = token_value
                        else:
                            missing_tokens.append(f"{token_name} (invalid: {reason})")
                    except Exception as e:
                        missing_tokens.append(f"{token_name} (error: {str(e)})")
                else:
                    # Try to use any available token as fallback
                    for fallback_name, fallback_token in request.consent_tokens.items():
                        if fallback_token:
                            try:
                                is_valid, reason, parsed = validate_token(fallback_token, expected_scope=ConsentScope.CUSTOM_TEMPORARY)
                                if is_valid and parsed.user_id == request.user_id:
                                    consent_tokens[token_name] = fallback_token
                                    break
                            except Exception:
                                continue
                    
                    if token_name not in consent_tokens:
                        missing_tokens.append(token_name)
            
            if not consent_tokens:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"MailerPanda requires consent tokens. Missing: {', '.join(missing_tokens)}"
                )
            
            # Extract user input
            user_input = request.parameters.get('user_input', '')
            mode = request.parameters.get('mode', 'interactive')
            
            if not user_input:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="MailerPanda requires 'user_input' parameter with email campaign description"
                )
            
            # Execute enhanced MailerPanda agent
            result = agent_instance.handle(
                user_id=request.user_id,
                consent_tokens=consent_tokens,
                user_input=user_input,
                mode=mode
            )
            
        else:
            # Generic agent execution
            if hasattr(agent_instance, 'handle'):
                result = agent_instance.handle(**request.parameters)
            else:
                raise HTTPException(
                    status_code=status.HTTP_501_NOT_IMPLEMENTED,
                    detail=f"Agent '{agent_id}' does not implement the required interface"
                )
        
        return AgentResponse(
            status="success",
            agent_id=agent_id,
            data=result
        )
        
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        return AgentResponse(
            status="error",
            agent_id=agent_id,
            error=str(e)
        )

async def execute_mailerpanda_agent(agent_instance, request: AgentRequest):
    """Handle MailerPanda agent execution with its LangGraph workflow."""
    
    # Extract required parameters
    user_input = request.parameters.get('user_input', '')
    user_email = request.parameters.get('user_email', '')
    receiver_emails = request.parameters.get('receiver_emails', [])
    mass_email = request.parameters.get('mass_email', False)
    
    # Get consent token
    consent_token = request.consent_tokens.get('email_token')
    if not consent_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MailerPanda requires 'email_token' in consent_tokens"
        )
    
    # Create initial state for LangGraph workflow
    initial_state = {
        'user_input': user_input,
        'user_email': user_email,
        'receiver_email': receiver_emails,
        'mass': mass_email,
        'consent_token': consent_token,
        'user_id': request.user_id,
        'email_template': '',
        'subject': '',
        'user_feedback': '',
        'approved': False
    }
    
    # Execute the workflow
    workflow = agent_instance._build_workflow()
    result = workflow.invoke(initial_state)
    
    return result

# ==================== SPECIFIC AGENT ENDPOINTS ====================

@app.post("/agents/addtocalendar/process-emails")
async def process_emails_to_calendar(
    user_id: str,
    email_token: str,
    calendar_token: str
):
    """Specific endpoint for AddToCalendar agent."""
    agent_data = agent_registry.get_agent("addtocalendar")
    if not agent_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AddToCalendar agent not available"
        )
    
    try:
        result = agent_data['instance'].handle(
            user_id=user_id,
            email_token_str=email_token,
            calendar_token_str=calendar_token
        )
        
        return AgentResponse(
            status="success",
            agent_id="addtocalendar",
            data=result
        )
    except Exception as e:
        return AgentResponse(
            status="error",
            agent_id="addtocalendar",
            error=str(e)
        )

@app.post("/agents/mailerpanda/draft")
async def draft_email_content(
    user_input: str,
    user_email: str,
    consent_token: str,
    receiver_emails: Optional[List[str]] = None,
    mass_email: bool = False
):
    """Specific endpoint for MailerPanda email drafting."""
    agent_data = agent_registry.get_agent("mailerpanda")
    if not agent_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MailerPanda agent not available"
        )
    
    try:
        # Create request for the generic execute endpoint
        request = AgentRequest(
            user_id="api_user",  # Could be extracted from token
            agent_id="mailerpanda",
            consent_tokens={"email_token": consent_token},
            parameters={
                "user_input": user_input,
                "user_email": user_email,
                "receiver_emails": receiver_emails or [],
                "mass_email": mass_email
            }
        )
        
        result = await execute_mailerpanda_agent(agent_data['instance'], request)
        
        return AgentResponse(
            status="success",
            agent_id="mailerpanda",
            data=result
        )
    except Exception as e:
        return AgentResponse(
            status="error",
            agent_id="mailerpanda",
            error=str(e)
        )

# ==================== ERROR HANDLERS ====================

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

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "error": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# ==================== STARTUP/SHUTDOWN ====================

@app.on_event("startup")
async def startup_event():
    """Initialize the API server."""
    print("🚀 Starting HushMCP Agent API Server")
    print(f"📋 Loaded {len(agent_registry.agents)} agents:")
    for agent_id in agent_registry.agents.keys():
        print(f"   - {agent_id}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    print("🛑 Shutting down HushMCP Agent API Server")

# ==================== FRONTEND INTEGRATION ENDPOINTS ====================

@app.post("/frontend/credentials/store")
async def store_user_credentials(request: CredentialRequest):
    """
    Store user credentials securely with Supabase authentication.
    
    This endpoint allows frontend applications to securely store:
    - Google OAuth credentials (credentials.json)
    - Mailjet API keys
    - Other service credentials
    
    All data is encrypted before storage in the vault.
    """
    try:
        result = frontend_integration.store_user_credentials(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store credentials: {str(e)}"
        )

@app.get("/frontend/credentials/{credential_type}")
async def retrieve_user_credentials(
    credential_type: str,
    user_id: str,
    supabase_token: str
):
    """
    Retrieve user credentials with Supabase authentication.
    
    Supported credential types:
    - google: Google OAuth credentials
    - mailjet: Mailjet API credentials
    """
    try:
        result = frontend_integration.retrieve_user_credentials(
            user_id, supabase_token, credential_type
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve credentials: {str(e)}"
        )

@app.post("/frontend/consent/generate")
async def generate_frontend_consent_tokens(request: ConsentRequest):
    """
    Generate HushhMCP consent tokens for authenticated frontend users.
    
    This endpoint creates properly scoped consent tokens that can be used
    to execute agents with the user's permission.
    """
    try:
        result = frontend_integration.generate_consent_tokens(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate consent tokens: {str(e)}"
        )

@app.post("/frontend/sessions/create")
async def create_agent_session(
    user_id: str,
    supabase_token: str,
    agent_id: str
):
    """
    Create a complete agent execution session.
    
    This endpoint creates:
    - Required consent tokens for the agent
    - Credential vault references
    - Session metadata
    
    Returns everything needed to execute an agent.
    """
    try:
        result = frontend_integration.create_agent_session(
            user_id, supabase_token, agent_id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent session: {str(e)}"
        )

@app.get("/frontend/agents/available")
async def get_available_agents_for_frontend():
    """
    Get list of available agents with their required scopes.
    
    This endpoint provides frontend applications with:
    - Agent metadata
    - Required consent scopes
    - Credential requirements
    """
    agents = agent_registry.list_agents()
    
    # Enhance with scope and credential requirements
    enhanced_agents = []
    for agent in agents:
        # Get manifest data for scopes
        agent_data = agent_registry.get_agent(agent.id)
        manifest = agent_data.get('manifest', {}) if agent_data else {}
        
        enhanced_agent = {
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "version": agent.version,
            "scopes": [scope.value for scope in manifest.get('scopes', [])],
            "required_credentials": [],
            "trust_links": manifest.get('trust_links', {}),
            "frontend_ready": True
        }
        
        # Determine required credentials based on agent ID
        if agent.id == "agent_mailerpanda":
            enhanced_agent["required_credentials"] = ["mailjet"]
        elif agent.id == "agent_addtocalendar":
            enhanced_agent["required_credentials"] = ["google"]
        
        enhanced_agents.append(enhanced_agent)
    
    return {
        "status": "success",
        "agents": enhanced_agents,
        "total_agents": len(enhanced_agents)
    }

# ==================== MAIN ENTRY POINT ====================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="HushMCP Agent API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--log-level", default="info", help="Log level")
    
    args = parser.parse_args()
    
    print(f"🎮 HushMCP Agent API Server")
    print(f"🌐 Starting server at http://{args.host}:{args.port}")
    print(f"📚 API Documentation: http://{args.host}:{args.port}/docs")
    print(f"🔄 Reload: {args.reload}")
    
    uvicorn.run(
        "api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )
