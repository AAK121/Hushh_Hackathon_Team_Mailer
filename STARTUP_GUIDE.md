# HushMCP Platform Startup Guide

## Quick Start (Recommended)

### Option 1: Use the Automated Startup Scripts

From the root directory (`C:\Users\Dell\Downloads\Pda_mailer`):

```bash
# For Windows PowerShell
.\start_platform.bat

# Or for Git Bash/WSL
./start_platform.sh
```

## Manual Setup (Step by Step)

### Prerequisites
- Python 3.8+ installed
- Node.js 16+ and npm installed
- Git (optional, for version control)

---

## 🎯 Backend API Server Setup

### Step 1: Navigate to Backend Directory
```bash
cd Pda_mailer
```

### Step 2: Create Python Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# OR for Command Prompt
.\.venv\Scripts\activate.bat

# OR for Git Bash
source .venv/Scripts/activate
```

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration (Optional but Recommended)
```bash
# Copy environment template
copy .env.example .env

# Edit .env file with your API keys (optional for demo mode)
notepad .env
```

**Optional API Keys (for full functionality):**
- `GEMINI_API_KEY` - For AI features (get from Google AI Studio)
- `MAILJET_API_KEY` & `MAILJET_API_SECRET` - For email sending
- `GOOGLE_API_KEY` - For additional Google services

### Step 5: Start Backend API Server
```bash
# Method 1: Direct Python execution
python api.py

# Method 2: Using uvicorn (more robust)
uvicorn api:app --host 0.0.0.0 --port 8001 --reload

# Method 3: Use the provided batch file
start_server.bat
```

**✅ Backend API server will start on:** `http://localhost:8001`
- API Documentation: `http://localhost:8001/docs`
- Health Check: `http://localhost:8001/health`

---

## 🎨 Frontend Setup

### Step 1: Navigate to Frontend Directory
```bash
# Open a NEW terminal/PowerShell window
cd Pda_mailer\frontend
```

### Step 2: Install Node.js Dependencies
```bash
npm install
```

### Step 3: Environment Configuration (Optional)
```bash
# Copy environment template if it exists
copy .env.example .env

# Create .env file for frontend configuration
echo "VITE_HUSHMCP_API_URL=http://localhost:8001" > .env
```

### Step 4: Start Frontend Development Server
```bash
# Start Vite development server
npm run dev
```

**✅ Frontend will start on:** `http://localhost:5173`

---

## 🚀 Verification & Testing

### 1. Check Backend API
Visit `http://localhost:8001/docs` to see the interactive API documentation.

Test the health endpoint:
```bash
curl http://localhost:8001/health
```

### 2. Check Frontend
Visit `http://localhost:5173` to see the frontend application.

### 3. Test Integration
1. Navigate to the Agent Store in the frontend
2. Try activating different agents (MailerPanda, AddToCalendar, Finance, Relationship, Research)
3. Test basic functionality in demo mode

---

## 🛠️ Available Agents

### 1. **MailerPanda Agent** 🐼
- **Endpoint:** `/agents/mailerpanda/execute`
- **Features:** AI email campaigns, personalization, approval workflows
- **Frontend Component:** `MailerPandaAgent.tsx`

### 2. **AddToCalendar Agent** 📅
- **Endpoint:** `/agents/addtocalendar/execute`
- **Features:** Email→Calendar automation, Google Calendar sync
- **Frontend Component:** `AddToCalendarAgent.tsx`

### 3. **Relationship Manager** 🤝
- **Endpoint:** `/agents/relationship_memory/execute`
- **Features:** Contact management, chat sessions, proactive reminders
- **Frontend Component:** `RelationshipAgent.tsx`

### 4. **Finance Manager** 💰
- **Endpoint:** `/agents/chandufinance/execute`
- **Features:** Financial planning, goal tracking, stock analysis
- **Frontend Component:** `FinanceAgent.tsx`

### 5. **Research Assistant** 🔬
- **Endpoint:** `/agents/research/search/arxiv`
- **Features:** ArXiv search, PDF processing, note-taking
- **Frontend Component:** `ResearchAgent.tsx`

---

## 🔧 Troubleshooting

### Backend Issues

**Port 8001 already in use:**
```bash
# Find process using port 8001
netstat -ano | findstr :8001
# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Python virtual environment issues:**
```bash
# Delete and recreate virtual environment
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Import errors:**
```bash
# Make sure you're in the correct directory and venv is activated
cd Pda_mailer
.\.venv\Scripts\Activate.ps1
python -c "import fastapi; print('FastAPI installed successfully')"
```

### Frontend Issues

**Port 5173 already in use:**
```bash
# Kill process using port 5173
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

**Node modules issues:**
```bash
# Clean install
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

**TypeScript compilation errors:**
```bash
# Clear TypeScript cache
npx tsc --build --clean
npm run build
```

### Connection Issues

**Frontend can't connect to backend:**
1. Ensure backend is running on `http://localhost:8001`
2. Check `.env` file in frontend: `VITE_HUSHMCP_API_URL=http://localhost:8001`
3. Disable browser ad-blockers/extensions
4. Check browser console for CORS errors

---

## 🎯 Development Mode Features

### Demo Mode
- All agents work in demo mode without API keys
- Mock responses for testing UI/UX
- No actual emails sent or calendar events created

### Full Mode (with API keys)
- Real AI generation with Gemini
- Actual email sending via Mailjet
- Google Calendar integration
- ArXiv paper search and processing

---

## 📚 Next Steps

1. **Explore the Agent Store** - Browse and activate different agents
2. **Try Demo Workflows** - Test each agent's functionality
3. **Add API Keys** - Enable full functionality with real services
4. **Customize Agents** - Modify configurations for your use case
5. **Deploy** - Use production builds for deployment

---

## 🆘 Need Help?

1. **API Documentation:** Visit `http://localhost:8001/docs`
2. **Check Logs:** Look at terminal outputs for both backend and frontend
3. **Browser DevTools:** Check Network and Console tabs for errors
4. **Test Endpoints:** Use curl or Postman to test backend APIs directly

---

## 🔄 Stopping the Servers

### Backend:
- Press `Ctrl+C` in the backend terminal

### Frontend:
- Press `Ctrl+C` in the frontend terminal

### Clean Shutdown:
```bash
# In backend terminal
Ctrl+C

# In frontend terminal  
Ctrl+C

# Deactivate Python virtual environment
deactivate
```

---

*Happy coding! 🚀*
