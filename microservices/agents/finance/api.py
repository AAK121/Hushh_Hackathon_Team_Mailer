#!/usr/bin/env python3
"""
Finance Agent Microservice
==========================

Dedicated microservice for financial analysis and investment operations.
"""

import os
import sys
import json
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
    print("✅ Finance service environment loaded")
except ImportError:
    print("⚠️ python-dotenv not installed")

# Add backend path for imports
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Initialize FastAPI app
app = FastAPI(
    title="Finance Agent API",
    description="Microservice for financial analysis and investment operations",
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

class FinanceRequest(BaseModel):
    """Request model for finance operations."""
    user_id: str = Field(..., description="User identifier")
    symbol: Optional[str] = Field(None, description="Stock symbol")
    symbols: Optional[List[str]] = Field(None, description="Multiple stock symbols")
    analysis_type: Optional[str] = Field("basic", description="Type of analysis")
    timeframe: Optional[str] = Field("1y", description="Analysis timeframe")
    token: Optional[str] = Field(None, description="Authorization token")

class FinanceResponse(BaseModel):
    """Response model for finance operations."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    service: str = "finance"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Finance Agent",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "finance",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/analyze")
async def analyze_stock(request: FinanceRequest):
    """Analyze financial data for a stock."""
    try:
        # Import the agent
        from hushh_mcp.agents.chandufinance.index import run_agent
        
        # Run financial analysis
        result = await run_agent(
            user_id=request.user_id,
            symbol=request.symbol,
            analysis_type=request.analysis_type
        )
        
        return FinanceResponse(
            success=True,
            data=result
        )
        
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Finance module not available: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Financial analysis failed: {str(e)}"
        )

@app.post("/portfolio")
async def analyze_portfolio(request: FinanceRequest):
    """Analyze portfolio of stocks."""
    try:
        # Import the agent
        from hushh_mcp.agents.chandufinance.index import run_agent
        
        if not request.symbols:
            raise HTTPException(
                status_code=400,
                detail="Symbols list required for portfolio analysis"
            )
        
        # Analyze each symbol
        portfolio_analysis = {}
        for symbol in request.symbols:
            try:
                result = await run_agent(
                    user_id=request.user_id,
                    symbol=symbol,
                    analysis_type="portfolio"
                )
                portfolio_analysis[symbol] = result
            except Exception as e:
                portfolio_analysis[symbol] = {"error": str(e)}
        
        return FinanceResponse(
            success=True,
            data={
                "portfolio": portfolio_analysis,
                "symbols": request.symbols,
                "analysis_date": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Portfolio analysis failed: {str(e)}"
        )

@app.post("/recommendations")
async def get_recommendations(request: FinanceRequest):
    """Get investment recommendations."""
    try:
        # Import the agent
        from hushh_mcp.agents.chandufinance.index import run_agent
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # Initialize AI model
        llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Get financial data for analysis
        financial_data = {}
        if request.symbols:
            for symbol in request.symbols[:5]:  # Limit to 5 symbols
                try:
                    result = await run_agent(
                        user_id=request.user_id,
                        symbol=symbol,
                        analysis_type="recommendation"
                    )
                    financial_data[symbol] = result
                except:
                    pass
        
        # Generate recommendations
        prompt = f"""
        As a financial advisor, provide investment recommendations based on the following data:
        
        Financial Data: {json.dumps(financial_data, indent=2)}
        
        User Profile: {request.analysis_type}
        Timeframe: {request.timeframe}
        
        Provide:
        1. Overall portfolio assessment
        2. Individual stock recommendations
        3. Risk analysis
        4. Suggested actions
        """
        
        response = llm.invoke(prompt)
        
        return FinanceResponse(
            success=True,
            data={
                "recommendations": response.content,
                "analysis_data": financial_data,
                "timeframe": request.timeframe
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Recommendation generation failed: {str(e)}"
        )

@app.post("/valuation")
async def stock_valuation(request: FinanceRequest):
    """Get stock valuation analysis."""
    try:
        # Import the agent
        from hushh_mcp.agents.chandufinance.index import run_agent
        
        # Run valuation analysis
        result = await run_agent(
            user_id=request.user_id,
            symbol=request.symbol,
            analysis_type="valuation"
        )
        
        return FinanceResponse(
            success=True,
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Valuation analysis failed: {str(e)}"
        )

@app.post("/news")
async def financial_news(request: FinanceRequest):
    """Get financial news for a stock."""
    try:
        import requests
        import feedparser
        
        # Get news from multiple sources
        news_sources = [
            f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={request.symbol}&region=US&lang=en-US",
            "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"
        ]
        
        all_news = []
        for source in news_sources:
            try:
                feed = feedparser.parse(source)
                for entry in feed.entries[:5]:  # Limit to 5 articles per source
                    all_news.append({
                        "title": entry.title,
                        "link": entry.link,
                        "published": entry.published if hasattr(entry, 'published') else None,
                        "summary": entry.summary if hasattr(entry, 'summary') else None
                    })
            except:
                continue
        
        return FinanceResponse(
            success=True,
            data={
                "news": all_news[:10],  # Limit to 10 total articles
                "symbol": request.symbol
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"News retrieval failed: {str(e)}"
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8004))
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )