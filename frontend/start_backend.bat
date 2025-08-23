@echo off
echo 🚀 Starting Calendar Integration Backend API...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Check if FastAPI is installed
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing required dependencies...
    python -m pip install -r backend_requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed successfully
    echo.
)

echo 🏃 Starting the API server...
echo 📚 API Documentation will be available at: http://127.0.0.1:8001/docs
echo 🔍 Health check available at: http://127.0.0.1:8001/health
echo 📅 Calendar endpoint: http://127.0.0.1:8001/agents/addtocalendar/execute
echo.
echo Press Ctrl+C to stop the server
echo.

python backend_api.py
