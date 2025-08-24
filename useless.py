# research_agent_api.py

"""
Research Agent FastAPI Backend
=====================================

A comprehensive academic research assistant API built on the HushMCP framework.
Provides arXiv search, PDF processing, AI-powered analysis, and note management.

Features:
- Natural language arXiv search optimization  
- PDF upload and text extraction
- AI-powered paper summarization
- Interactive snippet processing
- Multi-editor note management with vault storage
- Full HushMCP consent validation
"""

import os
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# FastAPI imports
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# HushMCP imports
from hushh_mcp.constants import ConsentScope
from hushh_mcp.consent.token import issue_token, validate_token
from hushh_mcp.agents.research_agent.index import research_agent
from hushh_mcp.agents.research_agent.manifest import manifest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Research Agent API",
    description="AI-powered academic research assistant with arXiv integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Request/Response Models ====================

class ArxivSearchRequest(BaseModel):
    """Request model for arXiv search."""
    user_id: str = Field(..., description="User identifier")
    consent_tokens: Dict[str, str] = Field(..., description="Consent tokens for required scopes")
    query: str = Field(..., description="Natural language research query")

class ArxivSearchResponse(BaseModel):
    """Response model for arXiv search."""
    success: bool
    session_id: str
    query: str
    results: List[Dict[str, Any]]
    total_papers: int
    error: Optional[str] = None

class PdfUploadResponse(BaseModel):
    """Response model for PDF upload."""
    success: bool
    session_id: str
    paper_id: str
    text_extracted: int
    error: Optional[str] = None

class SummaryRequest(BaseModel):
    """Request model for paper summary."""
    user_id: str = Field(..., description="User identifier")
    consent_tokens: Dict[str, str] = Field(..., description="Consent tokens for required scopes")

class SummaryResponse(BaseModel):
    """Response model for paper summary."""
    success: bool
    session_id: str
    paper_id: str
    summary: str
    error: Optional[str] = None

class SnippetProcessRequest(BaseModel):
    """Request model for snippet processing."""
    user_id: str = Field(..., description="User identifier")
    consent_tokens: Dict[str, str] = Field(..., description="Consent tokens for required scopes")
    text: str = Field(..., description="Text snippet to process")
    instruction: str = Field(..., description="Processing instruction (e.g., 'Summarize this', 'Explain for beginners')")

class SnippetProcessResponse(BaseModel):
    """Response model for snippet processing."""
    success: bool
    session_id: str
    paper_id: str
    original_snippet: str
    instruction: str
    processed_result: str
    error: Optional[str] = None

class NotesRequest(BaseModel):
    """Request model for saving notes."""
    user_id: str = Field(..., description="User identifier")
    consent_tokens: Dict[str, str] = Field(..., description="Consent tokens for required scopes")
    paper_id: str = Field(..., description="Paper identifier")
    editor_id: str = Field(..., description="Editor identifier (e.g., 'methodology_notes')")
    content: str = Field(..., description="Note content")

class NotesResponse(BaseModel):
    """Response model for saving notes."""
    success: bool
    session_id: str
    paper_id: str
    editor_id: str
    content_length: int
    error: Optional[str] = None

class ConsentTokenRequest(BaseModel):
    """Request model for generating consent tokens."""
    user_id: str = Field(..., description="User identifier")
    scopes: List[str] = Field(..., description="Required consent scopes")
    duration_hours: int = Field(default=24, description="Token validity duration in hours")

# ==================== Helper Functions ====================

def validate_consent_tokens(user_id: str, consent_tokens: Dict[str, str], required_scopes: List[ConsentScope]) -> bool:
    """Validate that all required consent tokens are valid."""
    try:
        for scope in required_scopes:
            scope_key = scope.value
            if scope_key not in consent_tokens:
                logger.error(f"Missing consent token for scope: {scope_key}")
                return False
            
            token = consent_tokens[scope_key]
            if not validate_token(token, user_id, [scope]):
                logger.error(f"Invalid consent token for scope: {scope_key}")
                return False
        
        return True
    except Exception as e:
        logger.error(f"Consent validation error: {e}")
        return False

def generate_paper_id() -> str:
    """Generate unique paper ID."""
    return f"paper_{uuid.uuid4().hex[:12]}"

# ==================== API Endpoints ====================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Research Agent API",
        "version": manifest["version"],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/agent/info")
async def get_agent_info():
    """Get research agent information and capabilities."""
    return {
        "agent": manifest,
        "status": "active",
        "endpoints": {
            "arxiv_search": "/paper/search/arxiv",
            "pdf_upload": "/paper/upload",
            "paper_summary": "/paper/{paper_id}/summary",
            "snippet_processing": "/paper/{paper_id}/process/snippet",
            "notes_management": "/session/notes"
        }
    }

@app.post("/consent/tokens", response_model=Dict[str, Any])
async def generate_consent_tokens(request: ConsentTokenRequest):
    """Generate consent tokens for research agent operations."""
    try:
        tokens = {}
        
        for scope_str in request.scopes:
            try:
                scope = ConsentScope(scope_str)
                token, expires_at = issue_token(
                    user_id=request.user_id,
                    scopes=[scope],
                    duration_hours=request.duration_hours
                )
                tokens[scope.value] = token
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid scope: {scope_str}"
                )
        
        return {
            "success": True,
            "user_id": request.user_id,
            "tokens": tokens,
            "expires_in_hours": request.duration_hours,
            "issued_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Consent token generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token generation failed: {str(e)}"
        )

@app.post("/paper/search/arxiv", response_model=ArxivSearchResponse)
async def search_arxiv_papers(request: ArxivSearchRequest):
    """
    Search arXiv papers using natural language query.
    
    The agent will optimize your natural language query for better arXiv search results.
    Example: "waste management research" → "waste management OR solid waste OR municipal waste"
    """
    try:
        # Validate consent tokens
        required_scopes = [ConsentScope.CUSTOM_TEMPORARY]
        if not validate_consent_tokens(request.user_id, request.consent_tokens, required_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or missing consent tokens"
            )
        
        # Execute search
        result = await research_agent.search_arxiv(
            user_id=request.user_id,
            consent_tokens=request.consent_tokens,
            query=request.query
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return ArxivSearchResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ArXiv search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@app.post("/paper/upload", response_model=PdfUploadResponse)
async def upload_paper(
    user_id: str,
    consent_tokens: str,  # JSON string of consent tokens
    file: UploadFile = File(...)
):
    """
    Upload a PDF paper for processing.
    
    Accepts PDF files and extracts text content for analysis.
    Returns a unique paper_id for future operations.
    """
    try:
        import json
        consent_tokens_dict = json.loads(consent_tokens)
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported"
            )
        
        # Validate consent tokens
        required_scopes = [ConsentScope.VAULT_READ_FILE, ConsentScope.VAULT_WRITE_FILE]
        if not validate_consent_tokens(user_id, consent_tokens_dict, required_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or missing consent tokens"
            )
        
        # Generate paper ID
        paper_id = generate_paper_id()
        
        # Process upload
        result = await research_agent.process_pdf_upload(
            user_id=user_id,
            consent_tokens=consent_tokens_dict,
            paper_id=paper_id,
            pdf_file=file
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return PdfUploadResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )

@app.get("/paper/{paper_id}/summary", response_model=SummaryResponse)
async def get_paper_summary(
    paper_id: str,
    request: SummaryRequest
):
    """
    Generate AI-powered summary of a research paper.
    
    Creates comprehensive summary with sections for objectives, methodology,
    findings, contributions, implications, and future work.
    """
    try:
        # Validate consent tokens
        required_scopes = [ConsentScope.VAULT_READ_FILE, ConsentScope.VAULT_WRITE_FILE, ConsentScope.CUSTOM_TEMPORARY]
        if not validate_consent_tokens(request.user_id, request.consent_tokens, required_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or missing consent tokens"
            )
        
        # Generate summary
        result = await research_agent.generate_paper_summary(
            user_id=request.user_id,
            consent_tokens=request.consent_tokens,
            paper_id=paper_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return SummaryResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summary generation failed: {str(e)}"
        )

@app.post("/paper/{paper_id}/process/snippet", response_model=SnippetProcessResponse)
async def process_text_snippet(
    paper_id: str,
    request: SnippetProcessRequest
):
    """
    Process text snippet with custom instruction.
    
    Examples:
    - "Explain this for a beginner"
    - "Summarize the key points"
    - "Extract the methodology" 
    - "Identify the main contributions"
    """
    try:
        # Validate consent tokens
        required_scopes = [ConsentScope.CUSTOM_TEMPORARY]
        if not validate_consent_tokens(request.user_id, request.consent_tokens, required_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or missing consent tokens"
            )
        
        # Process snippet
        result = await research_agent.process_text_snippet(
            user_id=request.user_id,
            consent_tokens=request.consent_tokens,
            paper_id=paper_id,
            snippet=request.text,
            instruction=request.instruction
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return SnippetProcessResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Snippet processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Snippet processing failed: {str(e)}"
        )

@app.post("/session/notes", response_model=NotesResponse) 
async def save_session_notes(request: NotesRequest):
    """
    Save notes to vault storage.
    
    Supports multiple editors/notebooks per session with encrypted storage.
    """
    try:
        # Validate consent tokens
        required_scopes = [ConsentScope.VAULT_WRITE_FILE]
        if not validate_consent_tokens(request.user_id, request.consent_tokens, required_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or missing consent tokens"
            )
        
        # Save notes
        result = await research_agent.save_session_notes(
            user_id=request.user_id,
            consent_tokens=request.consent_tokens,
            paper_id=request.paper_id,
            editor_id=request.editor_id,
            content=request.content
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return NotesResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Note saving failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Note saving failed: {str(e)}"
        )

# ==================== Additional Utility Endpoints ====================

@app.get("/paper/{paper_id}/info")
async def get_paper_info(paper_id: str):
    """Get information about a processed paper."""
    try:
        papers_dir = Path("vault/research_papers")
        pdf_path = papers_dir / f"{paper_id}.pdf"
        
        if not pdf_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paper not found: {paper_id}"
            )
        
        # Get file stats
        stat = pdf_path.stat()
        
        return {
            "paper_id": paper_id,
            "file_size": stat.st_size,
            "uploaded_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "status": "processed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Paper info retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Info retrieval failed: {str(e)}"
        )

@app.get("/session/{session_id}/status")
async def get_session_status(session_id: str):
    """Get status of a research session."""
    return {
        "session_id": session_id,
        "status": "active",
        "created_at": datetime.utcnow().isoformat()
    }

# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Ensure required directories exist
    Path("vault/research_papers").mkdir(parents=True, exist_ok=True)
    
    logger.info("🔬 Starting Research Agent API Server...")
    uvicorn.run(
        "research_agent_api:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
