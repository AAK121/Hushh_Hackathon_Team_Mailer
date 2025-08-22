# PowerShell script to start server in background
Write-Host "🚀 Starting Research Agent Backend Server..." -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Start server in new PowerShell window using global Python
$serverScript = @"
python api.py
"@

# Create a new PowerShell window for the server
Start-Process powershell -ArgumentList "-NoExit", "-Command", $serverScript -WindowStyle Normal

Start-Sleep 3

Write-Host ""
Write-Host "✅ Server started in separate window" -ForegroundColor Green
Write-Host "🌐 Server URL: http://localhost:8001" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 This terminal is now free for testing!" -ForegroundColor Yellow
Write-Host "   You can run tests while server runs in background" -ForegroundColor Yellow
Write-Host ""
Write-Host "🛑 To stop server: Close the server PowerShell window" -ForegroundColor Red
Write-Host ""
