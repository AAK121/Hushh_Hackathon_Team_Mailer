@echo off
echo Deploying HushMCP Agent API to Vercel...
echo.

REM Check if vercel is installed
where vercel >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Vercel CLI is not installed
    echo Please install it with: npm install -g vercel
    pause
    exit /b 1
)

REM Navigate to backend directory
cd /d "%~dp0"

echo Current directory: %CD%
echo.

REM Deploy to Vercel
echo Starting deployment...
vercel --prod

echo.
echo Deployment completed!
echo Check the Vercel dashboard for deployment status and URL.
pause
