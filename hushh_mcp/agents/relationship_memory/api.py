"""
FastAPI Backend for Proactive Relationship Manager Agent
Provides REST API endpoints for frontend communication with full HushhMCP compliance
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from hushh_mcp.agents.relationship_memory.index import (
    RelationshipMemoryAgent, run, run_proactive_check
)
from hushh_mcp.constants import ConsentScope
from hushh_mcp.consent.token import issue_token, validate_token
from hushh_mcp.types import UserID, AgentID

# Initialize FastAPI app
app = FastAPI(
    title="Proactive Relationship Manager API",
    description="REST API for the Proactive Relationship Manager Agent with full HushhMCP compliance",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# ==================== Pydantic Models for API ====================

class UserSession(BaseModel):
    """User session information"""
    user_id: str
    vault_key: str
    tokens: Dict[str, str]

class AgentRequest(BaseModel):
    """Base request model for agent operations"""
    user_input: str
    user_id: str
    vault_key: Optional[str] = None
    is_startup: Optional[bool] = False

class ContactRequest(BaseModel):
    """Request model for contact operations"""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    priority: Optional[str] = "medium"
    dates: Optional[Dict[str, str]] = None

class BatchContactRequest(BaseModel):
    """Request model for batch contact operations"""
    contacts: List[ContactRequest]
    user_id: str
    vault_key: Optional[str] = None

class MemoryRequest(BaseModel):
    """Request model for memory operations"""
    contact_name: str
    summary: str
    location: Optional[str] = None
    date: Optional[str] = None
    tags: Optional[List[str]] = []
    user_id: str
    vault_key: Optional[str] = None

class ReminderRequest(BaseModel):
    """Request model for reminder operations"""
    contact_name: str
    title: str
    date: Optional[str] = None
    priority: Optional[str] = "medium"
    description: Optional[str] = None
    user_id: str
    vault_key: Optional[str] = None

class AdviceRequest(BaseModel):
    """Request model for advice generation"""
    contact_name: str
    question: str
    user_id: str
    vault_key: Optional[str] = None

class ProactiveCheckRequest(BaseModel):
    """Request model for proactive checks"""
    user_id: str
    vault_key: Optional[str] = None

class AgentResponse(BaseModel):
    """Standard response model for agent operations"""
    status: str
    message: str
    data: Optional[List[Dict[str, Any]]] = None
    action_taken: Optional[str] = None
    agent_id: Optional[str] = None
    user_id: Optional[str] = None
    validated_scopes: Optional[List[str]] = None
    timestamp: Optional[str] = None

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: str

# ==================== Helper Functions ====================

def create_user_session(user_id: str) -> UserSession:
    """Create a user session with valid tokens"""
    agent_id = AgentID("agent_relationship_memory")
    vault_key = f"vault_key_{user_id}_{int(datetime.now().timestamp())}"
    
    required_scopes = [
        ConsentScope.VAULT_READ_CONTACTS,
        ConsentScope.VAULT_WRITE_CONTACTS,
        ConsentScope.VAULT_READ_MEMORY,
        ConsentScope.VAULT_WRITE_MEMORY,
    ]
    
    tokens = {}
    for scope in required_scopes:
        try:
            token_obj = issue_token(
                user_id=UserID(user_id),
                agent_id=agent_id,
                scope=scope,
                expires_in_ms=24 * 60 * 60 * 1000  # 24 hours
            )
            tokens[scope.value] = token_obj.token
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create token for {scope.value}: {str(e)}"
            )
    
    return UserSession(
        user_id=user_id,
        vault_key=vault_key,
        tokens=tokens
    )

def validate_user_session(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Validate user session and return user info"""
    try:
        # For demo purposes, we'll extract user_id from the token
        # In production, implement proper JWT validation
        token = credentials.credentials
        
        # Simple validation - in production use proper JWT validation
        if not token or len(token) < 10:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        # Extract user_id (in production, decode from JWT)
        user_id = token.split('_')[0] if '_' in token else "demo_user"
        
        return {
            "user_id": user_id,
            "token": token
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

def format_agent_response(result: Dict[str, Any]) -> AgentResponse:
    """Format agent result into API response"""
    return AgentResponse(
        status=result.get("status", "unknown"),
        message=result.get("message", ""),
        data=result.get("data"),
        action_taken=result.get("action_taken"),
        agent_id=result.get("agent_id"),
        user_id=result.get("user_id"),
        validated_scopes=result.get("validated_scopes"),
        timestamp=datetime.now().isoformat()
    )

# ==================== API Endpoints ====================

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Proactive Relationship Manager API",
        "version": "1.0.0",
        "description": "REST API for relationship management with proactive capabilities",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Proactive Relationship Manager API"
    }

@app.post("/auth/session", response_model=UserSession)
async def create_session(user_id: str):
    """Create a new user session with tokens"""
    try:
        session = create_user_session(user_id)
        return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )

@app.post("/agent/process", response_model=AgentResponse)
async def process_natural_language(
    request: AgentRequest,
    user_info: Dict[str, Any] = Depends(validate_user_session)
):
    """Process natural language input through the agent"""
    try:
        # Create session for the request
        session = create_user_session(request.user_id)
        
        # Process through agent
        result = run(
            user_id=request.user_id,
            tokens=session.tokens,
            user_input=request.user_input,
            vault_key=request.vault_key or session.vault_key,
            is_startup=request.is_startup
        )
        
        return format_agent_response(result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent processing failed: {str(e)}"
        )

@app.post("/agent/proactive-check", response_model=AgentResponse)
async def proactive_check(
    request: ProactiveCheckRequest,
    user_info: Dict[str, Any] = Depends(validate_user_session)
):
    """Run proactive check for upcoming events and reconnection suggestions"""
    try:
        # Create session for the request
        session = create_user_session(request.user_id)
        
        # Run proactive check
        result = run_proactive_check(
            user_id=request.user_id,
            tokens=session.tokens,
            vault_key=request.vault_key or session.vault_key
        )
        
        return format_agent_response(result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Proactive check failed: {str(e)}"
        )

@app.post("/contacts/add", response_model=AgentResponse)
async def add_contact(
    request: ContactRequest,
    user_info: Dict[str, Any] = Depends(validate_user_session)
):
    """Add a single contact"""
    try:
        # Create session
        session = create_user_session(user_info["user_id"])
        
        # Format as natural language
        contact_parts = [f"add contact {request.name}"]
        if request.email:
            contact_parts.append(f"with email {request.email}")
        if request.phone:
            contact_parts.append(f"and phone {request.phone}")
        if request.company:
            contact_parts.append(f"from {request.company}")
        if request.priority != "medium":
            contact_parts.append(f"as {request.priority} priority")
        
        user_input = " ".join(contact_parts)
        
        # Process through agent
        result = run(
            user_id=user_info["user_id"],
            tokens=session.tokens,
            user_input=user_input,
            vault_key=session.vault_key
        )
        
        return format_agent_response(result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add contact: {str(e)}"
        )

@app.post("/contacts/batch", response_model=AgentResponse)
async def add_batch_contacts(
    request: BatchContactRequest,
    user_info: Dict[str, Any] = Depends(validate_user_session)
):
    """Add multiple contacts in batch"""
    try:
        # Create session
        session = create_user_session(request.user_id)
        
        # Format as natural language batch command
        contact_descriptions = []
        for contact in request.contacts:
            desc = contact.name
            if contact.email:
                desc += f" with email {contact.email}"
            if contact.phone:
                desc += f" and phone {contact.phone}"
            contact_descriptions.append(desc)
        
        user_input = f"add contacts: {', '.join(contact_descriptions)}"
        
        # Process through agent
        result = run(
            user_id=request.user_id,
            tokens=session.tokens,
            user_input=user_input,
            vault_key=request.vault_key or session.vault_key
        )
        
        return format_agent_response(result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add batch contacts: {str(e)}"
        )

@app.get("/contacts", response_model=AgentResponse)
async def get_contacts(
    user_id: str,
    user_info: Dict[str, Any] = Depends(validate_user_session)
):
    """Get all contacts for a user"""
    try:
        # Create session
        session = create_user_session(user_id)
        
        # Process through agent
        result = run(
            user_id=user_id,
            tokens=session.tokens,
            user_input="show me all my contacts",
            vault_key=session.vault_key
        )
        
        return format_agent_response(result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get contacts: {str(e)}"
        )

@app.post("/memories/add", response_model=AgentResponse)
async def add_memory(
    request: MemoryRequest,
    user_info: Dict[str, Any] = Depends(validate_user_session)
):
    """Add a memory about a contact"""
    try:
        # Create session
        session = create_user_session(request.user_id)
        
        # Format as natural language
        user_input = f"remember that {request.contact_name} {request.summary}"
        if request.location:
            user_input += f" at {request.location}"
        
        # Process through agent
        result = run(
            user_id=request.user_id,
            tokens=session.tokens,
            user_input=user_input,
            vault_key=request.vault_key or session.vault_key
        )
        
        return format_agent_response(result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add memory: {str(e)}"
        )

@app.get("/memories", response_model=AgentResponse)
async def get_memories(
    user_id: str,
    contact_name: Optional[str] = None,
    user_info: Dict[str, Any] = Depends(validate_user_session)
):
    """Get memories for a user or specific contact"""
    try:
        # Create session
        session = create_user_session(user_id)
        
        # Format query
        if contact_name:
            user_input = f"show memories about {contact_name}"
        else:
            user_input = "show my memories"
        
        # Process through agent
        result = run(
            user_id=user_id,
            tokens=session.tokens,
            user_input=user_input,
            vault_key=session.vault_key
        )
        
        return format_agent_response(result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get memories: {str(e)}"
        )

@app.post("/reminders/add", response_model=AgentResponse)
async def add_reminder(
    request: ReminderRequest,
    user_info: Dict[str, Any] = Depends(validate_user_session)
):
    """Add a reminder about a contact"""
    try:
        # Create session
        session = create_user_session(request.user_id)
        
        # Format as natural language
        user_input = f"remind me to {request.title} for {request.contact_name}"
        if request.date:
            user_input += f" on {request.date}"
        
        # Process through agent
        result = run(
            user_id=request.user_id,
            tokens=session.tokens,
            user_input=user_input,
            vault_key=request.vault_key or session.vault_key
        )
        
        return format_agent_response(result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add reminder: {str(e)}"
        )

@app.get("/reminders", response_model=AgentResponse)
async def get_reminders(
    user_id: str,
    user_info: Dict[str, Any] = Depends(validate_user_session)
):
    """Get all reminders for a user"""
    try:
        # Create session
        session = create_user_session(user_id)
        
        # Process through agent
        result = run(
            user_id=user_id,
            tokens=session.tokens,
            user_input="show my reminders",
            vault_key=session.vault_key
        )
        
        return format_agent_response(result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get reminders: {str(e)}"
        )

@app.post("/advice", response_model=AgentResponse)
async def get_advice(
    request: AdviceRequest,
    user_info: Dict[str, Any] = Depends(validate_user_session)
):
    """Get conversational advice about a contact"""
    try:
        # Create session
        session = create_user_session(request.user_id)
        
        # Process through agent
        result = run(
            user_id=request.user_id,
            tokens=session.tokens,
            user_input=request.question,
            vault_key=request.vault_key or session.vault_key
        )
        
        return format_agent_response(result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get advice: {str(e)}"
        )

@app.get("/dates/upcoming", response_model=AgentResponse)
async def get_upcoming_dates(
    user_id: str,
    user_info: Dict[str, Any] = Depends(validate_user_session)
):
    """Get upcoming birthdays and important dates"""
    try:
        # Create session
        session = create_user_session(user_id)
        
        # Process through agent
        result = run(
            user_id=user_id,
            tokens=session.tokens,
            user_input="show upcoming birthdays and important dates",
            vault_key=session.vault_key
        )
        
        return format_agent_response(result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get upcoming dates: {str(e)}"
        )

@app.post("/dates/add", response_model=AgentResponse)
async def add_important_date(
    contact_name: str,
    date_type: str,
    date_value: str,
    user_id: str,
    year: Optional[str] = None,
    user_info: Dict[str, Any] = Depends(validate_user_session)
):
    """Add an important date for a contact"""
    try:
        # Create session
        session = create_user_session(user_id)
        
        # Format as natural language
        user_input = f"{contact_name}'s {date_type} is on {date_value}"
        if year:
            user_input += f", {year}"
        
        # Process through agent
        result = run(
            user_id=user_id,
            tokens=session.tokens,
            user_input=user_input,
            vault_key=session.vault_key
        )
        
        return format_agent_response(result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add important date: {str(e)}"
        )

@app.get("/contacts/{contact_name}/details", response_model=AgentResponse)
async def get_contact_details(
    contact_name: str,
    user_id: str,
    user_info: Dict[str, Any] = Depends(validate_user_session)
):
    """Get detailed information about a specific contact"""
    try:
        # Create session
        session = create_user_session(user_id)
        
        # Process through agent
        result = run(
            user_id=user_id,
            tokens=session.tokens,
            user_input=f"tell me about {contact_name}",
            vault_key=session.vault_key
        )
        
        return format_agent_response(result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get contact details: {str(e)}"
        )

@app.get("/search/contacts", response_model=AgentResponse)
async def search_contacts(
    query: str,
    user_id: str,
    user_info: Dict[str, Any] = Depends(validate_user_session)
):
    """Search contacts by name or details"""
    try:
        # Create session
        session = create_user_session(user_id)
        
        # Process through agent
        result = run(
            user_id=user_id,
            tokens=session.tokens,
            user_input=f"search for contacts: {query}",
            vault_key=session.vault_key
        )
        
        return format_agent_response(result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search contacts: {str(e)}"
        )

# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return ErrorResponse(
        error=exc.detail,
        detail=f"HTTP {exc.status_code}",
        timestamp=datetime.now().isoformat()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    return ErrorResponse(
        error="Internal server error",
        detail=str(exc),
        timestamp=datetime.now().isoformat()
    )

# ==================== Main ====================

if __name__ == "__main__":
    # Check environment
    gemini_key = os.getenv('GEMINI_API_KEY')
    secret_key = os.getenv('SECRET_KEY')
    
    if not gemini_key:
        print("❌ Error: GEMINI_API_KEY not found in environment variables.")
        exit(1)
    
    if not secret_key:
        print("❌ Error: SECRET_KEY not found in environment variables.")
        exit(1)
    
    print("🚀 Starting Proactive Relationship Manager API...")
    print("✅ Environment check passed")
    print("📋 API Documentation: http://localhost:8001/docs")
    print("🔄 Interactive API: http://localhost:8001/redoc")
    
    # Run the server on port 8001 to avoid conflicts
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )