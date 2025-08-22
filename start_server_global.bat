@echo off
echo Starting Research Agent Backend Server (Global Python)...
echo ========================================================

REM Install required dependencies first
echo Installing dependencies...
python -m pip install fastapi uvicorn python-multipart requests feedparser langchain langchain-google-genai langgraph google-generativeai arxiv PyPDF2 cryptography python-dotenv --quiet --disable-pip-version-check

REM Start server in new window
echo Starting server in background window...
start "Research Agent Server" cmd /k "cd /d %~dp0 && python api.py"

echo.
echo ✅ Server starting in background window
echo 🌐 Server URL: http://localhost:8001
echo 📚 API Docs: http://localhost:8001/docs
echo.
echo Waiting 10 seconds for server to start...
timeout /t 10 /nobreak > nul

echo Testing server connection...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8001/health' -TimeoutSec 10; Write-Host '✅ Server is running!' -ForegroundColor Green; Write-Host '📊 Response:' $response.Content -ForegroundColor Cyan } catch { Write-Host '❌ Server not responding:' $_.Exception.Message -ForegroundColor Red }"

echo.
echo You can now use this terminal for testing!
pause
