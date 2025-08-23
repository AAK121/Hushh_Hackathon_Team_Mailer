@echo off
echo ========================================
echo  HushMCP Platform Startup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

echo ✅ Python and Node.js are available
echo.

REM Navigate to backend directory
echo 📂 Setting up Backend...
cd /d "%~dp0Pda_mailer"

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo 🔧 Creating Python virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment and install dependencies
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat

echo 📦 Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)

REM Start backend server in background
echo 🚀 Starting Backend API Server on http://localhost:8001...
start "HushMCP Backend" cmd /k "call .venv\Scripts\activate.bat && python api.py"

REM Wait a moment for backend to start
timeout /t 5 /nobreak >nul

REM Navigate to frontend directory
echo 📂 Setting up Frontend...
cd frontend

REM Install Node.js dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo 📦 Installing Node.js dependencies...
    npm install
    if errorlevel 1 (
        echo ❌ Failed to install Node.js dependencies
        pause
        exit /b 1
    )
)

REM Create frontend .env file if it doesn't exist
if not exist ".env" (
    echo 🔧 Creating frontend environment file...
    echo VITE_HUSHMCP_API_URL=http://localhost:8001 > .env
)

REM Start frontend development server
echo 🚀 Starting Frontend on http://localhost:5173...
start "HushMCP Frontend" cmd /k "npm run dev"

REM Wait a moment and open browser
timeout /t 3 /nobreak >nul
start "" http://localhost:5173

echo.
echo ========================================
echo ✅ HushMCP Platform Started Successfully!
echo ========================================
echo.
echo 🌐 Frontend: http://localhost:5173
echo 🛠️  Backend API: http://localhost:8001
echo 📚 API Docs: http://localhost:8001/docs
echo.
echo Press any key to close this window...
echo (The servers will continue running in separate windows)
pause >nul
