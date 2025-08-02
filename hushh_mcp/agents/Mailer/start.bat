@echo off
title Hushh Email Agent
cls

echo ========================================
echo    Hushh Email Agent - Quick Start
echo ========================================
echo.

echo 🚀 Starting Email Agent...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8 or higher.
    echo 📥 Download from: https://python.org/downloads
    pause
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip not found! Please ensure pip is installed.
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Install dependencies if requirements.txt exists
if exist requirements.txt (
    echo 📦 Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies!
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed
    echo.
)

REM Create sample Excel file if it doesn't exist
if not exist sample_recipients.xlsx (
    echo 📊 Creating sample Excel file...
    python create_sample_excel.py
    echo.
)

echo 🌟 Features Available:
echo    ✨ AI-powered email generation
echo    📊 Excel file integration  
echo    📧 Mass email sending
echo    🎨 Modern web interface
echo.

echo 🌐 Opening web browser...
echo    URL: http://localhost:5000
echo    Setup: http://localhost:5000/setup
echo.

echo 📝 Important: Configure your API keys at /setup
echo    - Google Gemini API Key
echo    - Mailjet API Keys
echo.

echo ⏳ Starting server...
echo Press Ctrl+C to stop the server
echo.

REM Open browser (optional)
timeout /t 3 /nobreak >nul
start http://localhost:5000

REM Start the Flask application
python run.py

echo.
echo 👋 Email Agent stopped. Press any key to exit...
pause >nul
