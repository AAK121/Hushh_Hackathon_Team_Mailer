@echo off
REM Backend startup script for HushMCP API Server (Windows)

REM Install dependencies
pip install -r requirements.txt

REM Start the API server
python api.py
