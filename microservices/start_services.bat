@echo off
REM Start all microservices for development on Windows

echo 🚀 Starting HushMCP Microservices...

REM Create PID directory
if not exist "pids" mkdir pids

REM Start Gateway
echo Starting Gateway on port 8000...
cd gateway
start "Gateway" python api.py
cd ..

REM Start AddToCalendar
echo Starting AddToCalendar on port 8001...
cd agents\addtocalendar
start "AddToCalendar" python api.py
cd ..\..

REM Start MailerPanda
echo Starting MailerPanda on port 8002...
cd agents\mailerpanda
start "MailerPanda" python api.py
cd ..\..

REM Start Research
echo Starting Research on port 8003...
cd agents\research
start "Research" python api.py
cd ..\..

REM Start Finance
echo Starting Finance on port 8004...
cd agents\finance
start "Finance" python api.py
cd ..\..

REM Start Memory
echo Starting Memory on port 8005...
cd agents\memory
start "Memory" python api.py
cd ..\..

echo ✅ All services started!
echo.
echo 📊 Service URLs:
echo   Gateway:        http://localhost:8000
echo   AddToCalendar:  http://localhost:8001
echo   MailerPanda:    http://localhost:8002
echo   Research:       http://localhost:8003
echo   Finance:        http://localhost:8004
echo   Memory:         http://localhost:8005
echo.
echo 📖 API Documentation:
echo   Gateway Docs:   http://localhost:8000/docs
echo.
echo 🔍 Health Check:  http://localhost:8000/health
echo.
echo Each service is running in its own window. Close the windows to stop services.
pause