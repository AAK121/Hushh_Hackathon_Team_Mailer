#!/usr/bin/env python3
"""
Vercel Entry Point for HushMCP Agent API Server
==============================================
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import and configure the FastAPI application
try:
    from api import app as fastapi_application
    
    # Export for Vercel (using different variable name to avoid conflicts)
    app = fastapi_application
    
    print("✅ Successfully loaded FastAPI application")
    
except Exception as e:
    print(f"❌ Error loading application: {e}")
    
    # Create minimal fallback
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="HushMCP API - Error")
    
    @app.get("/")
    async def error_root():
        return JSONResponse(
            status_code=500,
            content={"error": "Application load failed", "detail": str(e)}
        )
    
    @app.get("/health")
    async def error_health():
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )