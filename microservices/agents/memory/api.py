#!/usr/bin/env python3
"""
Memory Agent Microservice
=========================

Dedicated microservice for relationship memory management and proactive interactions.
"""

import os
import sys
import json
import uuid
from typing import Dict, Any, Optional, List
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
    print("✅ Memory service environment loaded")
except ImportError:
    print("⚠️ python-dotenv not installed")

# Add backend path for imports
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Initialize FastAPI app
app = FastAPI(
    title="Memory Agent API",
    description="Microservice for relationship memory management and proactive interactions",
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

class MemoryRequest(BaseModel):
    """Request model for memory operations."""
    user_id: str = Field(..., description="User identifier")
    contact_email: Optional[str] = Field(None, description="Contact email")
    interaction_data: Optional[Dict[str, Any]] = Field(None, description="Interaction data to store")
    query: Optional[str] = Field(None, description="Query for memory retrieval")
    token: Optional[str] = Field(None, description="Authorization token")

class MemoryResponse(BaseModel):
    """Response model for memory operations."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    service: str = "memory"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Memory Agent",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "memory",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/store")
async def store_memory(request: MemoryRequest):
    """Store relationship memory."""
    try:
        # Import the agent
        from hushh_mcp.agents.relationship_memory.index import run
        from hushh_mcp.consent.token import validate_token
        from hushh_mcp.constants import ConsentScope
        
        # Validate token
        if request.token:
            token_validation = validate_token(
                request.token, 
                request.user_id, 
                ConsentScope.VAULT_WRITE_EMAIL
            )
            if not token_validation.get("valid"):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                )
        
        # Store memory
        result = await run(
            user_id=request.user_id,
            operation="store",
            data=request.interaction_data
        )
        
        return MemoryResponse(
            success=True,
            data=result
        )
        
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Memory module not available: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Memory storage failed: {str(e)}"
        )

@app.post("/retrieve")
async def retrieve_memory(request: MemoryRequest):
    """Retrieve relationship memory."""
    try:
        # Import the agent
        from hushh_mcp.agents.relationship_memory.index import run
        
        # Retrieve memory
        result = await run(
            user_id=request.user_id,
            operation="retrieve",
            query=request.query,
            contact_email=request.contact_email
        )
        
        return MemoryResponse(
            success=True,
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Memory retrieval failed: {str(e)}"
        )

@app.post("/proactive")
async def proactive_check(request: MemoryRequest):
    """Run proactive memory checks."""
    try:
        # Import the agent
        from hushh_mcp.agents.relationship_memory.index import run_proactive_check
        
        # Run proactive check
        result = await run_proactive_check(
            user_id=request.user_id
        )
        
        return MemoryResponse(
            success=True,
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Proactive check failed: {str(e)}"
        )

@app.post("/analyze")
async def analyze_relationships(request: MemoryRequest):
    """Analyze relationship patterns."""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from hushh_mcp.vault.user_vault import UserVault
        
        # Initialize AI model
        llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Get user's relationship data
        vault = UserVault(request.user_id)
        memory_data = vault.get("relationship_memory") or {}
        
        # Analyze patterns
        prompt = f"""
        Analyze the following relationship memory data and provide insights:
        
        Data: {json.dumps(memory_data, indent=2)}
        
        Provide:
        1. Relationship patterns
        2. Communication frequency analysis
        3. Important upcoming events or follow-ups
        4. Relationship health assessment
        5. Recommendations for maintaining relationships
        """
        
        response = llm.invoke(prompt)
        
        return MemoryResponse(
            success=True,
            data={
                "analysis": response.content,
                "memory_count": len(memory_data),
                "analysis_date": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Relationship analysis failed: {str(e)}"
        )

@app.post("/vault/store")
async def vault_store(request: MemoryRequest):
    """Store data in user vault."""
    try:
        from hushh_mcp.vault.user_vault import UserVault
        from hushh_mcp.consent.token import validate_token
        from hushh_mcp.constants import ConsentScope
        
        # Validate token
        if request.token:
            token_validation = validate_token(
                request.token, 
                request.user_id, 
                ConsentScope.VAULT_WRITE_EMAIL
            )
            if not token_validation.get("valid"):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                )
        
        # Store in vault
        vault = UserVault(request.user_id)
        
        # Generate storage key
        storage_key = request.interaction_data.get("key", f"data_{uuid.uuid4()}")
        data_to_store = request.interaction_data.get("data")
        
        vault.store(storage_key, data_to_store)
        
        return MemoryResponse(
            success=True,
            data={
                "key": storage_key,
                "stored_at": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Vault storage failed: {str(e)}"
        )

@app.post("/vault/retrieve")
async def vault_retrieve(request: MemoryRequest):
    """Retrieve data from user vault."""
    try:
        from hushh_mcp.vault.user_vault import UserVault
        from hushh_mcp.consent.token import validate_token
        from hushh_mcp.constants import ConsentScope
        
        # Validate token
        if request.token:
            token_validation = validate_token(
                request.token, 
                request.user_id, 
                ConsentScope.VAULT_READ_EMAIL
            )
            if not token_validation.get("valid"):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                )
        
        # Retrieve from vault
        vault = UserVault(request.user_id)
        storage_key = request.query
        
        data = vault.get(storage_key)
        
        return MemoryResponse(
            success=True,
            data={
                "key": storage_key,
                "data": data,
                "retrieved_at": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Vault retrieval failed: {str(e)}"
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8005))
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )