# ⚡ Quick Start Commands

## 🚀 One-Click Startup (Recommended)

**From the `Pda_mailer` directory:**
```bash
.\start_platform.bat
```

## 🔧 Manual Startup (2 Terminals)

### Terminal 1: Backend API Server
```bash
cd Pda_mailer
.\.venv\Scripts\Activate.ps1  # or activate.bat for cmd
python api.py
```

### Terminal 2: Frontend Development Server  
```bash
cd Pda_mailer\frontend
npm run dev
```

## 🌐 Access URLs

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

## 🛠️ First Time Setup

### Prerequisites Check
```bash
python --version    # Should be 3.8+
node --version      # Should be 16+
npm --version       # Should be 8+
```

### Backend Setup (First Time Only)
```bash
cd Pda_mailer
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Frontend Setup (First Time Only)
```bash
cd Pda_mailer\frontend
npm install
```

## 🎯 Testing the Platform

1. Visit http://localhost:5173
2. Navigate to "Agent Store" 
3. Activate any agent (MailerPanda, AddToCalendar, Finance, Relationship, Research)
4. Test basic functionality - all agents work in demo mode!

## 🔄 Stopping Services

**Backend:** Press `Ctrl+C` in backend terminal  
**Frontend:** Press `Ctrl+C` in frontend terminal

---

*That's it! The platform is fully integrated and ready to use! 🎉*
