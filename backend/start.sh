#!/bin/bash
# Backend startup script for HushMCP API Server

# Install dependencies
pip install -r requirements.txt

# Start the API server
python api.py
