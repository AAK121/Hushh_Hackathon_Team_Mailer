#!/usr/bin/env python3
"""
Simple ASGI Entry Point for Vercel
==================================

A minimal entry point that should be more compatible with Vercel's Python runtime.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Import the FastAPI app
    from api import app
    
    # ASGI application for Vercel
    def application(scope, receive, send):
        """ASGI application wrapper."""
        return app(scope, receive, send)
        
    # Also export as app for compatibility
    app = app
    
except Exception as e:
    # Fallback minimal ASGI app
    import json
    from datetime import datetime
    
    async def fallback_app(scope, receive, send):
        """Minimal fallback ASGI app."""
        if scope["type"] == "http":
            response_body = json.dumps({
                "error": "Failed to load main application",
                "detail": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }).encode()
            
            await send({
                "type": "http.response.start",
                "status": 500,
                "headers": [[b"content-type", b"application/json"]],
            })
            await send({
                "type": "http.response.body",
                "body": response_body,
            })
    
    application = fallback_app
    app = fallback_app
