#!/usr/bin/env python3
"""
MailerPanda Agent Microservice
==============================

Dedicated microservice for email personalization and mass mailing operations.
"""

import os
import sys
import json
import base64
import tempfile
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv('.env')
    print("✅ MailerPanda service environment loaded")
except ImportError:
    print("⚠️ python-dotenv not installed")

# Add backend path for imports
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Initialize FastAPI app
app = FastAPI(
    title="MailerPanda Agent API",
    description="Microservice for email personalization and mass mailing",
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

class MailerRequest(BaseModel):
    """Request model for mailer operations."""
    user_id: str = Field(..., description="User identifier")
    email_template: Optional[str] = Field(None, description="Email template")
    contacts: Optional[List[Dict[str, Any]]] = Field(None, description="Contact list")
    personalization_data: Optional[Dict[str, Any]] = Field(None, description="Personalization context")
    token: Optional[str] = Field(None, description="Authorization token")

class MailerResponse(BaseModel):
    """Response model for mailer operations."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    service: str = "mailerpanda"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "MailerPanda Agent",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "mailerpanda",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/personalize")
async def personalize_emails(request: MailerRequest):
    """Personalize email content for recipients."""
    try:
        # Import the agent
        from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
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
        
        # Initialize agent
        agent = MassMailerAgent(request.user_id)
        
        # Personalize emails
        result = await agent.personalize_emails(
            template=request.email_template,
            contacts=request.contacts,
            context=request.personalization_data
        )
        
        return MailerResponse(
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
            detail=f"Email personalization failed: {str(e)}"
        )

@app.post("/send")
async def send_emails(request: MailerRequest):
    """Send personalized emails."""
    try:
        # Import the agent
        from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
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
        
        # Initialize agent
        agent = MassMailerAgent(request.user_id)
        
        # Send emails
        result = await agent.send_emails(request.contacts)
        
        return MailerResponse(
            success=True,
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Email sending failed: {str(e)}"
        )

@app.post("/upload")
async def upload_contacts(file: UploadFile = File(...)):
    """Upload contacts file for email campaign."""
    try:
        # Import pandas for file processing
        import pandas as pd
        
        # Read uploaded file
        content = await file.read()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Process file based on extension
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension == '.csv':
            df = pd.read_csv(tmp_file_path)
        elif file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(tmp_file_path)
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Please upload CSV or Excel files."
            )
        
        # Convert to contacts format
        contacts = []
        for _, row in df.iterrows():
            contact = {}
            for col in df.columns:
                contact[col.lower().replace(' ', '_')] = str(row[col]) if pd.notna(row[col]) else ""
            contacts.append(contact)
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        
        return MailerResponse(
            success=True,
            data={
                "contacts": contacts,
                "count": len(contacts),
                "columns": list(df.columns)
            }
        )
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'tmp_file_path' in locals():
            try:
                os.unlink(tmp_file_path)
            except:
                pass
        
        raise HTTPException(
            status_code=500,
            detail=f"File upload failed: {str(e)}"
        )

@app.post("/template")
async def generate_template(request: MailerRequest):
    """Generate email template based on context."""
    try:
        # Import the agent
        from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
        
        # Initialize agent
        agent = MassMailerAgent(request.user_id)
        
        # Generate template
        result = await agent.generate_template(request.personalization_data)
        
        return MailerResponse(
            success=True,
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Template generation failed: {str(e)}"
        )

@app.post("/preview")
async def preview_email(request: MailerRequest):
    """Preview personalized email for a contact."""
    try:
        # Import the agent
        from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
        
        # Initialize agent
        agent = MassMailerAgent(request.user_id)
        
        # Preview email
        result = await agent.preview_email(
            template=request.email_template,
            contact=request.contacts[0] if request.contacts else {},
            context=request.personalization_data
        )
        
        return MailerResponse(
            success=True,
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Email preview failed: {str(e)}"
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8002))
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )