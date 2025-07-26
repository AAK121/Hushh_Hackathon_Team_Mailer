# Hushh Mailer Agent - Web Interface

A ChatGPT-style web interface for the Hushh Mailer Agent that helps you create and send professional emails with AI assistance.

## Features

- 🤖 **AI-Powered Email Generation**: Create professional emails by simply describing what you want to write
- 📝 **Interactive Editing**: Request revisions and improvements to your email drafts
- 📊 **Excel Integration**: Upload Excel files with recipient data for bulk email sending
- 📧 **Email Sending**: Send emails directly through the Mailjet API
- 💬 **Chat Interface**: ChatGPT-like conversational interface for easy interaction
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file in this directory with your Mailjet credentials:
   ```
   MJ_APIKEY_PUBLIC=your_mailjet_public_key
   MJ_APIKEY_PRIVATE=your_mailjet_private_key
   ```

3. **Run the Application**:
   ```bash
   python app.py
   ```

4. **Open in Browser**:
   Navigate to `http://localhost:5000`

## Usage

### Creating Emails

1. **Start a New Conversation**: Click "New Email Draft" or use the example prompts
2. **Describe Your Email**: Tell the AI what kind of email you want to create
3. **Review the Draft**: The AI will generate a professional email template
4. **Request Changes**: If needed, ask for revisions to improve the email
5. **Approve**: Once satisfied, approve the email for sending

### Sending Emails

#### Option 1: Upload Excel File
1. Click "Upload Contact List" after approving an email
2. Upload an Excel file (.xlsx or .xls) with recipient data
3. Required column: `email`
4. Optional columns: `name`, `company_name`, etc. (matching template placeholders)
5. Confirm sending to all recipients

#### Option 2: Manual Sending
1. Copy the template and customize manually
2. Use your preferred email client

## Email Template Placeholders

Your email templates can include placeholders that will be automatically filled from your Excel data:

- `{name}` - Recipient's name
- `{email}` - Recipient's email
- `{company_name}` - Company name
- `{position}` - Job position
- `{start_date}` - Start date
- `{department}` - Department
- `{sender_name}` - Your name
- `{title}` - Your title

## Excel File Format

Your Excel file should have columns matching the placeholders in your email template:

| name | email | company_name | position |
|------|--------|--------------|----------|
| John Doe | john@example.com | Tech Corp | Developer |
| Jane Smith | jane@example.com | Design Inc | Designer |

## API Endpoints

- `POST /api/generate-email` - Generate email template
- `POST /api/send-emails` - Send emails to recipients
- `POST /api/process-excel` - Process uploaded Excel file
- `GET /api/health` - Health check

## File Structure

```
Mailer/
├── index.html          # Main web interface
├── styles.css          # CSS styling
├── script.js           # JavaScript functionality
├── app.py              # Flask backend
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Features in Detail

### Conversation History
- Previous email drafts are saved in the sidebar
- Click on any conversation to resume working on that email

### Example Prompts
- Welcome emails for new employees
- Follow-up emails for interviews
- Meeting invitations
- Thank you emails

### Error Handling
- Graceful fallback if backend is unavailable
- Clear error messages for upload issues
- Retry mechanisms for failed email sends

## Troubleshooting

1. **Emails not sending**: Check your Mailjet credentials in the `.env` file
2. **Excel upload fails**: Ensure your file has an `email` column
3. **Template placeholders not working**: Make sure your Excel columns match the placeholders exactly
4. **Port conflicts**: Change the port in `app.py` if 5000 is already in use

## Integration with Jupyter Notebooks

This web interface can work alongside the existing Jupyter notebook implementation in the same folder:
- `excel.ipynb` - Original notebook implementation
- `send_emails.ipynb` - Email sending notebook

Both interfaces use the same underlying email generation and sending logic.
