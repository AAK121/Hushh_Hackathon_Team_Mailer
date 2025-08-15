"""
Script to run the Relationship Memory Agent
"""
import uvicorn
from fastapi import FastAPI
from hushh_mcp.agents.relationship_memory import init_agent
from hushh_mcp.agents.relationship_memory.utils.api import router

# Initialize FastAPI app
app = FastAPI(title="Relationship Memory Agent API")

# Register routes
app.include_router(router)

# Initialize agent on startup
@app.on_event("startup")
async def startup_event():
    init_agent()

if __name__ == "__main__":
    uvicorn.run("run_agent:app", host="0.0.0.0", port=8000, reload=True)
