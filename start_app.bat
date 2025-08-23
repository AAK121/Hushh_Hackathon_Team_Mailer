@echo off
echo ========================================
echo Starting Personal Agent Stack
echo ========================================
echo.

echo Starting Backend API Server (Port 8000)...
start cmd /k "cd /d %~dp0 && python api.py"

echo Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

echo Starting Frontend Development Server...
start cmd /k "cd /d %~dp0\frontend && npm run dev"

echo.
echo ========================================
echo Application Started Successfully!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit...
pause > nul
