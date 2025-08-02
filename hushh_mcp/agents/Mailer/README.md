# Hushh Email Agent - Web Frontend

A modern web-based email automation system with AI-powered content generation using LangGraph and Google Gemini.

## Features

- 🤖 **AI-Powered Email Generation**: Uses Google Gemini for intelligent email content creation
- 📊 **Excel Integration**: Upload Excel files with recipient data and dynamic placeholders
- 🎨 **Modern Web Interface**: Beautiful, responsive Bootstrap-based UI
- 📧 **Mass Email Sending**: Send personalized emails to multiple recipients via Mailjet
- ✏️ **Real-time Editing**: Preview and edit generated content before sending
- 📈 **Progress Tracking**: Real-time progress monitoring during email sending
- 💾 **Status Reports**: Download detailed status reports after email campaigns

## Quick Start

### 1. Install Dependencies

```bash
cd hushh_mcp/agents/Mailer
pip install -r requirements.txt
```

### 2. Set Up API Keys

You'll need:
- **Google Gemini API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Mailjet API Keys**: Get from [Mailjet Dashboard](https://app.mailjet.com/account/api_keys)

### 3. Run the Application

```bash
python app.py
```

Open your browser and navigate to `http://localhost:5000`

### 4. Configure API Keys

1. Click on "Setup" in the navigation
2. Enter your API keys
3. Save configuration

### 5. Start Sending Emails

1. Upload an Excel file with recipient data
2. Describe the email you want to send
3. Review the AI-generated content
4. Send to all recipients

## Excel File Format

Your Excel file should contain columns like:

| name | email | company_name | position |
|------|-------|--------------|----------|
| John Doe | john@example.com | Tech Corp | Developer |
| Jane Smith | jane@example.com | Design Co | Designer |

**Required Columns:**
- `email`: Recipient email address

**Optional Columns:**
- `name`: Recipient name
- Any other columns for personalization (company_name, position, etc.)

## Usage Examples

### Welcome Email for New Interns
**Input:** "I want to send a welcome email to all new interns joining next week"

**Generated Output:**
- Subject: Welcome to the Team!
- Personalized content using {name}, {email}, etc.
- Mass email flag: true

### Project Update Email
**Input:** "Send a project status update to all team members with their current assignments"

### Meeting Invitation
**Input:** "Invite all stakeholders to the quarterly review meeting"

## API Endpoints

The Flask app provides these REST endpoints:

- `POST /upload_excel` - Upload Excel file
- `POST /draft_email` - Generate email draft
- `POST /send_emails` - Send emails to recipients
- `GET /preview_excel/<path>` - Preview Excel data
- `GET /download_status/<path>` - Download status report

## File Structure

```
Mailer/
├── app.py                 # Flask web application
├── email_agent.py         # Core email agent logic
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Main dashboard
│   └── setup.html        # API configuration
├── agent.ipynb           # Original notebook (reference)
├── send_emails.ipynb     # Email sending notebook (reference)
└── excel.ipynb           # Excel processing notebook (reference)
```

## Configuration Options

### Environment Variables

Set these environment variables instead of using the web interface:

```bash
export GOOGLE_API_KEY="your-gemini-api-key"
export MAILJET_API_KEY="your-mailjet-public-key"
export MAILJET_SECRET_KEY="your-mailjet-private-key"
```

### Security Notes

- API keys are stored in memory only (not persisted to disk)
- Use environment variables for production deployments
- The application runs on localhost by default
- For production, use a proper WSGI server like Gunicorn

## Troubleshooting

### Common Issues

1. **Import Error for mailjet_rest**
   ```bash
   pip install mailjet-rest
   ```

2. **LangGraph Import Error**
   ```bash
   pip install langgraph langchain-google-genai
   ```

3. **Excel File Not Reading**
   - Ensure file has .xlsx or .xls extension
   - Check that required 'email' column exists
   - Verify file size is under 16MB

4. **Email Sending Fails**
   - Verify Mailjet API keys are correct
   - Check email addresses are valid
   - Ensure Mailjet account is active

### Debug Mode

To run in debug mode with detailed error messages:

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## Development

### Adding New Features

1. **Custom Email Templates**: Extend the `draft_content` method
2. **Additional File Formats**: Add support for CSV, JSON imports
3. **Email Scheduling**: Implement delayed email sending
4. **Analytics Dashboard**: Add email open/click tracking

### Testing

Run the original notebook files for testing individual components:

```bash
jupyter notebook agent.ipynb
```

## License

This project is part of the Hushh Hackathon submission.

## Support

For issues or questions, please refer to the project documentation or create an issue in the repository.
