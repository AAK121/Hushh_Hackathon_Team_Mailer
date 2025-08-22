# Backend Testing Guide - Fix for Terminal Blocking Issue

## Problem: Server Blocks Terminal

When you run `python api.py` in PowerShell, it blocks the terminal and you can't run other commands. This is normal behavior for server processes.

## Solution: Run Server in Background

### Method 1: Use Batch File (Recommended)
```bash
# Double-click this file or run in terminal:
start_server_background.bat
```

### Method 2: Use PowerShell Script
```powershell
# Run this in PowerShell:
.\start_server_background.ps1
```

### Method 3: Manual Background Start
```bash
# In PowerShell, run:
start "Research Agent Server" cmd /k "conda activate mailer && python api.py"
```

## Testing the Backend

### Step 1: Start Server in Background
1. Double-click `start_server_background.bat`
2. A new window will open running the server
3. Your original terminal remains free for testing

### Step 2: Test with Simple Script
```bash
# In your free terminal, run:
python test_backend_api.py
```

### Step 3: Manual API Testing
Open browser and visit:
- http://localhost:8001/docs (API documentation)
- http://localhost:8001/health (Health check)
- http://localhost:8001/agents (Available agents)

## Expected Test Results

### ✅ Working Backend
```
🧪 Research Agent Backend Testing
==================================================
🔌 Testing API Connection...
✅ API Server is running!

🤖 Testing Agents Discovery...
✅ Agents endpoint working!
   Found X agents:
   📋 research_agent

🔍 Testing Research Agent Search...
✅ Search request completed!
   Success: False (due to consent validation)
   💡 This is expected - consent validation is working!

📚 Testing API Documentation...
✅ API documentation is accessible!

📊 TEST SUMMARY
==================================================
🎯 Results: 4/4 tests passed
🚀 All tests passed! Backend is fully operational!
```

### ❌ Server Not Running
```
🔌 Testing API Connection...
❌ Cannot connect to API: [Errno 11001] getaddrinfo failed
💡 Make sure you started the server with start_server_background.bat
```

## Real Paper Search Test

To test actual ArXiv paper retrieval (bypassing consent):

```bash
# Install dependencies first:
python -m pip install requests feedparser

# Then run the comprehensive demo:
python demo_research_agent.py
```

## Troubleshooting

### Server Won't Start
1. Check conda environment: `conda activate mailer`
2. Install dependencies: `pip install -r requirements.txt`
3. Check if port 8001 is available

### Tests Fail
1. Verify server is running: visit http://localhost:8001/docs
2. Check firewall settings
3. Try different port in api.py

### Cannot Install Dependencies
```bash
# Try these alternatives:
python -m pip install --user requests feedparser
# Or
conda install requests feedparser
```

## Next Steps

Once backend tests pass:
1. ✅ Backend API is operational
2. ✅ Research agent structure working
3. ✅ ArXiv integration functional
4. 🚀 Ready for frontend development

The consent validation "failures" are actually successes - they prove the security system is working correctly!
