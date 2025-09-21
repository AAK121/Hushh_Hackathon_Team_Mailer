#!/usr/bin/env python3
"""
HushMCP Grand API Gateway
========================

Main API gateway that routes requests to individual agent microservices.
Acts as a central entry point for all agent operations.
"""

import os
import sys
import json
import httpx
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv('.env')
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️ python-dotenv not installed, using system environment variables")

# Agent service URLs from environment
AGENT_SERVICES = {
    "addtocalendar": os.getenv("ADDTOCALENDAR_SERVICE_URL", "http://localhost:8001"),
    "mailerpanda": os.getenv("MAILERPANDA_SERVICE_URL", "http://localhost:8002"),
    "research": os.getenv("RESEARCH_SERVICE_URL", "http://localhost:8003"),
    "finance": os.getenv("FINANCE_SERVICE_URL", "http://localhost:8004"),
    "memory": os.getenv("MEMORY_SERVICE_URL", "http://localhost:8005"),
}

# Initialize FastAPI app
app = FastAPI(
    title="HushMCP Grand API Gateway",
    description="Central API gateway for HushMCP agent microservices",
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

# HTTP client for service communication
http_client = httpx.AsyncClient(timeout=60.0)

class AgentRequest(BaseModel):
    """Generic request model for agent operations."""
    user_id: str = Field(..., description="User identifier")
    data: Dict[str, Any] = Field(default_factory=dict, description="Agent-specific data")
    token: Optional[str] = Field(None, description="Authorization token")

class ServiceResponse(BaseModel):
    """Standard response model for all services."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    service: str
    timestamp: str

async def forward_to_service(service_name: str, endpoint: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Forward request to appropriate microservice."""
    service_url = AGENT_SERVICES.get(service_name)
    if not service_url:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service_name}' not found or not configured"
        )
    
    try:
        url = f"{service_url}{endpoint}"
        response = await http_client.post(url, json=request_data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Service error: {response.text}"
            )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=408,
            detail=f"Service '{service_name}' timeout"
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service '{service_name}' unavailable: {str(e)}"
        )

@app.get("/")
async def root():
    """Root endpoint with service status."""
    return {
        "message": "HushMCP Grand API Gateway",
        "version": "1.0.0",
        "services": list(AGENT_SERVICES.keys()),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check for all services."""
    service_status = {}
    
    for service_name, service_url in AGENT_SERVICES.items():
        try:
            response = await http_client.get(f"{service_url}/health", timeout=5.0)
            service_status[service_name] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "url": service_url,
                "response_time": response.elapsed.total_seconds()
            }
        except Exception as e:
            service_status[service_name] = {
                "status": "unavailable",
                "url": service_url,
                "error": str(e)
            }
    
    return {
        "gateway_status": "healthy",
        "services": service_status,
        "timestamp": datetime.now().isoformat()
    }

# AddToCalendar Agent Routes
@app.post("/agents/addtocalendar/extract")
async def addtocalendar_extract(request: AgentRequest):
    """Extract calendar events from email content."""
    return await forward_to_service("addtocalendar", "/extract", request.dict())

@app.post("/agents/addtocalendar/add")
async def addtocalendar_add(request: AgentRequest):
    """Add event to Google Calendar."""
    return await forward_to_service("addtocalendar", "/add", request.dict())

# MailerPanda Agent Routes
@app.post("/agents/mailerpanda/personalize")
async def mailerpanda_personalize(request: AgentRequest):
    """Personalize email content for recipients."""
    return await forward_to_service("mailerpanda", "/personalize", request.dict())

@app.post("/agents/mailerpanda/send")
async def mailerpanda_send(request: AgentRequest):
    """Send personalized emails."""
    return await forward_to_service("mailerpanda", "/send", request.dict())

@app.post("/agents/mailerpanda/upload")
async def mailerpanda_upload(request: Request):
    """Upload contacts file for email campaign."""
    # Forward file upload to service
    content = await request.body()
    headers = dict(request.headers)
    
    service_url = AGENT_SERVICES["mailerpanda"]
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{service_url}/upload",
            content=content,
            headers=headers
        )
        return response.json()

# Research Agent Routes
@app.post("/agents/research/search")
async def research_search(request: AgentRequest):
    """Search for research papers."""
    return await forward_to_service("research", "/search", request.dict())

@app.post("/agents/research/analyze")
async def research_analyze(request: AgentRequest):
    """Analyze research papers."""
    return await forward_to_service("research", "/analyze", request.dict())

@app.post("/agents/research/chat")
async def research_chat(request: AgentRequest):
    """Chat with research agent about papers."""
    return await forward_to_service("research", "/chat", request.dict())

# Finance Agent Routes
@app.post("/agents/finance/analyze")
async def finance_analyze(request: AgentRequest):
    """Analyze financial data."""
    return await forward_to_service("finance", "/analyze", request.dict())

@app.post("/agents/finance/portfolio")
async def finance_portfolio(request: AgentRequest):
    """Get portfolio analysis."""
    return await forward_to_service("finance", "/portfolio", request.dict())

@app.post("/agents/finance/recommendations")
async def finance_recommendations(request: AgentRequest):
    """Get investment recommendations."""
    return await forward_to_service("finance", "/recommendations", request.dict())

# Memory Agent Routes
@app.post("/agents/memory/store")
async def memory_store(request: AgentRequest):
    """Store relationship memory."""
    return await forward_to_service("memory", "/store", request.dict())

@app.post("/agents/memory/retrieve")
async def memory_retrieve(request: AgentRequest):
    """Retrieve relationship memory."""
    return await forward_to_service("memory", "/retrieve", request.dict())

@app.post("/agents/memory/proactive")
async def memory_proactive(request: AgentRequest):
    """Run proactive memory checks."""
    return await forward_to_service("memory", "/proactive", request.dict())

# Vault operations (can be centralized or distributed)
@app.post("/vault/store")
async def vault_store(request: AgentRequest):
    """Store data in user vault."""
    # This could be handled by a separate vault service or distributed
    return await forward_to_service("memory", "/vault/store", request.dict())

@app.post("/vault/retrieve")
async def vault_retrieve(request: AgentRequest):
    """Retrieve data from user vault."""
    return await forward_to_service("memory", "/vault/retrieve", request.dict())

# Token management
@app.post("/auth/token")
async def issue_token(request: AgentRequest):
    """Issue authentication token."""
    # This could be centralized or handled by individual services
    return {"token": "gateway_token", "expires_in": 3600}

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom exception handler for better error responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "service": "gateway",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )