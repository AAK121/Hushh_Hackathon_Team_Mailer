#!/usr/bin/env python3
"""
Human-in-the-Loop AI Backend API
FastAPI server that handles chat requests with tool confirmation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import json
import os
from datetime import datetime

app = FastAPI(
    title="Human-in-the-Loop AI API",
    description="Backend API for human-in-the-loop AI interactions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatMessage(BaseModel):
    role: str
    content: str
    id: Optional[str] = None

class ChatRequest(BaseModel):
    messages: List[Dict[str, Any]]

class ToolExecutionRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
    approved: bool

# Simple in-memory storage for demo
conversation_history = []

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Human-in-the-Loop AI API"
    }

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint that handles messages and tool confirmations
    This is a simplified version - in production you'd integrate with OpenAI API
    """
    try:
        messages = request.messages
        
        # For demo purposes, return a mock response
        # In production, this would integrate with OpenAI API and the HITL logic
        
        response = {
            "id": f"msg_{datetime.now().timestamp()}",
            "role": "assistant", 
            "content": "I understand you want to use the human-in-the-loop functionality. This is a demo backend. To fully implement this, you would need to integrate with OpenAI API and implement the tool confirmation logic here.",
            "parts": [
                {
                    "type": "text",
                    "text": "Hello! I'm your AI assistant with human-in-the-loop capabilities. I can help you with various tasks, but I'll always ask for your approval before taking any actions. What would you like me to help you with today?"
                }
            ]
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

@app.post("/api/tools/execute")
async def execute_tool(request: ToolExecutionRequest):
    """Execute a tool after human approval"""
    try:
        if not request.approved:
            return {"status": "denied", "message": "Tool execution was denied by user"}
        
        tool_name = request.tool_name
        parameters = request.parameters
        
        # Mock tool execution
        if tool_name == "getWeatherInformation":
            city = parameters.get("city", "Unknown")
            weather_conditions = ["sunny", "cloudy", "rainy", "snowy"]
            import random
            condition = random.choice(weather_conditions)
            result = f"The weather in {city} is {condition}."
            
        elif tool_name == "sendEmail":
            to = parameters.get("to", "")
            subject = parameters.get("subject", "")
            result = f"Email sent successfully to {to} with subject '{subject}'"
            
        elif tool_name == "scheduleCalendarEvent":
            title = parameters.get("title", "")
            date = parameters.get("date", "")
            time = parameters.get("time", "")
            result = f"Calendar event '{title}' scheduled for {date} at {time}"
            
        else:
            result = f"Tool '{tool_name}' executed with parameters: {json.dumps(parameters)}"
        
        return {
            "status": "success",
            "result": result,
            "tool_name": tool_name,
            "parameters": parameters
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing tool: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Human-in-the-Loop AI Backend API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat",
            "tool_execution": "/api/tools/execute",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    print("🚀 Starting Human-in-the-Loop AI Backend API...")
    print("📚 API Documentation available at: http://127.0.0.1:8001/docs")
    print("🔍 Health check available at: http://127.0.0.1:8001/health")
    print("💬 Chat endpoint: http://127.0.0.1:8001/api/chat")
    print("🔧 Tool execution endpoint: http://127.0.0.1:8001/api/tools/execute")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    uvicorn.run(
        "backend_api:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )
