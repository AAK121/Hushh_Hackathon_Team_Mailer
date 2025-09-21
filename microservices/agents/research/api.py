#!/usr/bin/env python3
"""
Research Agent Microservice
===========================

Dedicated microservice for research paper analysis and academic research operations.
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
    print("✅ Research service environment loaded")
except ImportError:
    print("⚠️ python-dotenv not installed")

# Add backend path for imports
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Initialize FastAPI app
app = FastAPI(
    title="Research Agent API",
    description="Microservice for research paper analysis and academic research",
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

class ResearchRequest(BaseModel):
    """Request model for research operations."""
    user_id: str = Field(..., description="User identifier")
    query: Optional[str] = Field(None, description="Research query")
    paper_ids: Optional[List[str]] = Field(None, description="Paper IDs to analyze")
    keywords: Optional[List[str]] = Field(None, description="Keywords for search")
    max_results: Optional[int] = Field(10, description="Maximum results")
    token: Optional[str] = Field(None, description="Authorization token")

class ResearchResponse(BaseModel):
    """Response model for research operations."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    service: str = "research"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Research Agent",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "research",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/search")
async def search_papers(request: ResearchRequest):
    """Search for research papers."""
    try:
        # Import the agent
        from hushh_mcp.agents.research_agent.index import research_agent
        import arxiv
        import feedparser
        
        # Search arxiv
        search = arxiv.Search(
            query=request.query,
            max_results=request.max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        
        papers = []
        for result in search.results():
            papers.append({
                "id": result.entry_id.split('/')[-1],
                "title": result.title,
                "summary": result.summary,
                "authors": [author.name for author in result.authors],
                "published": result.published.isoformat(),
                "pdf_url": result.pdf_url,
                "categories": result.categories
            })
        
        return ResearchResponse(
            success=True,
            data={
                "papers": papers,
                "count": len(papers),
                "query": request.query
            }
        )
        
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Research module not available: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Paper search failed: {str(e)}"
        )

@app.post("/analyze")
async def analyze_papers(request: ResearchRequest):
    """Analyze research papers."""
    try:
        # Import the agent
        from hushh_mcp.agents.research_agent.index import research_agent
        
        # Run research agent
        result = await research_agent(
            user_id=request.user_id,
            query=request.query,
            paper_ids=request.paper_ids
        )
        
        return ResearchResponse(
            success=True,
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Paper analysis failed: {str(e)}"
        )

@app.post("/chat")
async def chat_with_papers(request: ResearchRequest):
    """Chat with research agent about papers."""
    try:
        # Import required modules
        import requests
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # Initialize AI model
        llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Get paper context if paper_ids provided
        context = ""
        if request.paper_ids:
            # Fetch paper content
            for paper_id in request.paper_ids[:3]:  # Limit to 3 papers
                try:
                    # Get paper from vault if available
                    from hushh_mcp.vault.user_vault import UserVault
                    vault = UserVault(request.user_id)
                    paper_data = vault.get(f"paper_text_{paper_id}")
                    if paper_data:
                        context += f"\n\nPaper {paper_id}:\n{paper_data[:2000]}..."
                except:
                    pass
        
        # Generate response
        prompt = f"""
        You are a research assistant. Answer the following question about research papers.
        
        Context from papers: {context}
        
        Question: {request.query}
        
        Provide a comprehensive answer based on the research papers.
        """
        
        response = llm.invoke(prompt)
        
        return ResearchResponse(
            success=True,
            data={
                "response": response.content,
                "query": request.query,
                "paper_count": len(request.paper_ids) if request.paper_ids else 0
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}"
        )

@app.post("/download")
async def download_paper(request: ResearchRequest):
    """Download and store research paper."""
    try:
        import requests
        from io import BytesIO
        
        if not request.paper_ids or len(request.paper_ids) == 0:
            raise HTTPException(
                status_code=400,
                detail="Paper ID required"
            )
        
        paper_id = request.paper_ids[0]
        
        # Download paper PDF
        pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
        response = requests.get(pdf_url)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=404,
                detail="Paper not found"
            )
        
        # Store in vault
        from hushh_mcp.vault.user_vault import UserVault
        vault = UserVault(request.user_id)
        
        # Store PDF content
        vault.store(f"paper_pdf_{paper_id}", response.content)
        
        return ResearchResponse(
            success=True,
            data={
                "paper_id": paper_id,
                "size": len(response.content),
                "status": "downloaded"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Paper download failed: {str(e)}"
        )

@app.post("/extract")
async def extract_paper_text(request: ResearchRequest):
    """Extract text from research paper PDF."""
    try:
        import PyPDF2
        from io import BytesIO
        
        if not request.paper_ids:
            raise HTTPException(
                status_code=400,
                detail="Paper ID required"
            )
        
        paper_id = request.paper_ids[0]
        
        # Get PDF from vault
        from hushh_mcp.vault.user_vault import UserVault
        vault = UserVault(request.user_id)
        
        pdf_content = vault.get(f"paper_pdf_{paper_id}")
        if not pdf_content:
            raise HTTPException(
                status_code=404,
                detail="Paper not found in vault"
            )
        
        # Extract text
        pdf_file = BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text_content = ""
        for page_num in range(len(pdf_reader.pages)):
            try:
                page = pdf_reader.pages[page_num]
                text_content += page.extract_text() + "\n"
            except:
                text_content += f"\n[Error extracting page {page_num + 1}]\n"
        
        # Store extracted text
        vault.store(f"paper_text_{paper_id}", text_content)
        
        return ResearchResponse(
            success=True,
            data={
                "paper_id": paper_id,
                "text_length": len(text_content),
                "pages": len(pdf_reader.pages),
                "status": "extracted"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Text extraction failed: {str(e)}"
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8003))
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )