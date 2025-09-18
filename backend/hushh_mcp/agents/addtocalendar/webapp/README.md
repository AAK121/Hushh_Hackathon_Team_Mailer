# 🐱 GmailCat PDA - Web Interface

**Personal Digital Assistant powered by HushMCP Framework**

A beautiful, modern web interface for the GmailCat PDA that automatically scans your Gmail inbox, extracts events using AI, and creates them in your Google Calendar.

## ✨ Features

- **🎨 Modern UI**: Beautiful, responsive design with smooth animations
- **🤖 AI-Powered**: Uses OpenAI GPT-4 to intelligently extract events from emails
- **🔒 Privacy-First**: Built with HushMCP consent framework for data security
- **📱 Responsive**: Works perfectly on desktop, tablet, and mobile devices
- **⚡ Real-time**: Live updates and progress tracking
- **📊 Analytics**: Clear visualization of processing results

## 🚀 Quick Start

### Option 1: Windows Batch File (Easiest)
1. Double-click `start_gmailcat.bat`
2. The script will automatically install dependencies and start the server
3. Open your browser to `http://127.0.0.1:8000`

### Option 2: Python Script
```bash
cd webapp
python start_server.py
```

### Option 3: Manual Django
```bash
cd webapp
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## 📋 Prerequisites

- Python 3.8+
- Google account with Gmail and Calendar access
- OpenAI API key (set in `.env` file in the parent directory)
- Google OAuth credentials (`credentials.json` in the addtocalendar folder)

## 🔧 Configuration

1. **OpenAI API Key**: Make sure `OPENAI_API_KEY` is set in your `.env` file
2. **Google Credentials**: Ensure `credentials.json` is present in the parent directory
3. **First Run**: You may need to authenticate with Google when first running

## 🎯 Usage

1. **Start the Server**: Use one of the startup methods above
2. **Open Browser**: Navigate to `http://127.0.0.1:8000`
3. **Process Emails**: Click the "Process Emails & Create Events" button
4. **Authentication**: Complete Google OAuth if prompted
5. **View Results**: See created calendar events and links

## 🏗️ Architecture

```
webapp/
├── 📁 gmailcat_app/          # Main Django application
│   ├── 📁 static/           # CSS, JavaScript, images
│   ├── 📁 templates/        # HTML templates
│   ├── 📄 views.py          # Request handlers
│   └── 📄 urls.py           # URL routing
├── 📁 project_settings/     # Django project configuration
├── 📄 manage.py            # Django management script
├── 📄 start_server.py      # Automated startup script
├── 📄 start_gmailcat.bat   # Windows batch file
└── 📄 requirements.txt     # Python dependencies
```

## 🎨 Design Features

- **Gradient Background**: Beautiful blue-purple gradient
- **Card-based Layout**: Clean, modern card design
- **Interactive Elements**: Hover effects and smooth transitions
- **Loading Animations**: Engaging progress indicators
- **Toast Notifications**: User-friendly error and success messages
- **Responsive Grid**: Adapts to all screen sizes

## 🔄 API Endpoints

- `GET /` - Main interface
- `POST /run-agent/` - Process emails and create calendar events

## 🛠️ Development

The webapp integrates seamlessly with the HushMCP framework:

- **Token Management**: Handles both email and calendar consent tokens
- **Agent Integration**: Directly calls the AddToCalendarAgent
- **Error Handling**: Comprehensive error reporting and user feedback
- **Security**: CSRF protection and secure token validation

## 📊 Status Indicators

- 🟢 **Ready**: System ready to process emails
- 🟡 **Processing**: Currently analyzing emails and creating events
- 🔴 **Error**: Something went wrong (check logs)
- ✅ **Success**: Events successfully created

## 🎭 Customization

The webapp is fully customizable:

- **Colors**: Modify CSS variables in `static/css/style.css`
- **Layout**: Update HTML structure in `templates/index.html`
- **Functionality**: Extend JavaScript in `static/js/app.js`
- **Backend**: Modify views in `gmailcat_app/views.py`

## 🚨 Troubleshooting

**Server won't start?**
- Check Python version (3.8+)
- Ensure all dependencies are installed
- Verify `.env` file exists with OPENAI_API_KEY

**Google authentication issues?**
- Ensure `credentials.json` is present
- Check Google API quotas
- Verify OAuth consent screen configuration

**No events created?**
- Check if you have unread emails
- Verify OpenAI API key is valid
- Ensure Google Calendar permissions are granted

## 📄 License

Part of the Hushh_Hackathon_Team_Mailer project. See project root for license information.

---

**Built with ❤️ using Django, HushMCP, and modern web technologies**
