@echo off
echo Starting Research Agent Backend Server in Background...
echo =====================================================

REM Start server in background using global Python
start "Research Agent Server" cmd /k "python api.py"

echo.
echo ✅ Server started in background window
echo 🌐 Server URL: http://localhost:8001
echo 📚 API Docs: http://localhost:8001/docs
echo.
echo You can now use this terminal for testing!
echo To stop the server, close the "Research Agent Server" window
echo.

pause
