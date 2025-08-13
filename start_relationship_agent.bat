@echo off
REM Start Redis Server (Make sure Redis is installed)
echo Starting Redis Server...
start redis-server

REM Start Celery Worker
echo Starting Celery Worker...
start celery -A hushh_mcp.agents.relationship_memory.reminder_engine worker --loglevel=info

REM Start Celery Beat
echo Starting Celery Beat...
start celery -A hushh_mcp.agents.relationship_memory.reminder_engine beat --loglevel=info

REM Start the FastAPI server
echo Starting Relationship Memory Agent API...
python run_agent.py
