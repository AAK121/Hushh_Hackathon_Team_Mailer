#!/usr/bin/env python3
"""
Vercel Entry Point for HushMCP Agent API Server
==============================================

This module exports the FastAPI application for Vercel serverless deployment.
Vercel looks for 'app', 'application', or 'handler' at the module level.
"""

import sys
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Initialize app with fallback
app = None

print("🚀 Initializing Vercel entry point...")

# Try to load the main FastAPI application
try:
    from api import app as main_app
    app = main_app
    print("✅ Successfully loaded FastAPI application from api.py")
    
except ImportError as e:
    print(f"❌ Import error loading api.py: {e}")
    import traceback
    traceback.print_exc()
    
    # Create fallback app
    app = FastAPI(title="HushMCP API - Import Error Fallback")
    
    @app.get("/")
    async def root():
        return JSONResponse({
            "error": "Failed to import api.py",
            "detail": str(e),
            "type": "ImportError"
        }, status_code=500)
    
    @app.get("/health")
    async def health():
        return JSONResponse({
            "status": "error",
            "message": "Import failed"
        }, status_code=500)

except Exception as e:
    print(f"❌ Unexpected error loading api.py: {e}")
    import traceback
    traceback.print_exc()
    
    # Create fallback app for any other error
    app = FastAPI(title="HushMCP API - Error Fallback")
    
    @app.get("/")
    async def root():
        return JSONResponse({
            "error": "Application initialization failed",
            "detail": str(e),
            "type": type(e).__name__
        }, status_code=500)
    
    @app.get("/health")
    async def health():
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

# Ensure app is defined and exported
if app is None:
    print("❌ Failed to initialize app - creating minimal fallback")
    app = FastAPI(title="HushMCP API - Critical Error")
    
    @app.get("/")
    async def root():
        return JSONResponse({
            "error": "Critical error: app not initialized",
            "type": "InitializationError"
        }, status_code=500)

print("✅ Vercel entry point initialization complete")
print(f"✅ App exported: {app.title if app else 'FAILED'}")