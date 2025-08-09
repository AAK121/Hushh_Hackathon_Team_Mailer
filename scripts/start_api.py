#!/usr/bin/env python3
"""
HushMCP Agent API Launcher
=========================

Easy launcher script for the HushMCP Agent API server with pre-configured settings
and environment validation.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check if the environment is properly configured."""
    print("🔍 Checking environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check required environment variables
    required_vars = [
        "OPENAI_API_KEY",
        "MAILJET_API_KEY", 
        "MAILJET_API_SECRET",
        "GEMINI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file or environment")
        return False
    
    print("✅ Environment variables configured")
    
    # Check if fastapi is installed
    try:
        import fastapi
        print(f"✅ FastAPI {fastapi.__version__}")
    except ImportError:
        print("❌ FastAPI not installed. Run: pip install -r api_requirements.txt")
        return False
    
    return True

def install_dependencies():
    """Install API dependencies."""
    print("📦 Installing API dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "api_requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def main():
    """Main launcher function."""
    print("🎮 HushMCP Agent API Launcher")
    print("=" * 50)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check if dependencies need to be installed
    try:
        import fastapi
    except ImportError:
        print("🔧 FastAPI not found, installing dependencies...")
        if not install_dependencies():
            sys.exit(1)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        sys.exit(1)
    
    print("\n🚀 Starting HushMCP Agent API Server...")
    print("=" * 50)
    
    # Default configuration
    host = os.environ.get("API_HOST", "127.0.0.1")
    port = int(os.environ.get("API_PORT", "8001"))
    reload = os.environ.get("API_RELOAD", "true").lower() == "true"
    log_level = os.environ.get("API_LOG_LEVEL", "info")
    
    print(f"🌐 Server URL: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"🔄 Auto-reload: {reload}")
    print(f"📝 Log level: {log_level}")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print()
    
    # Start the server
    try:
        import uvicorn
        uvicorn.run(
            "api:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
