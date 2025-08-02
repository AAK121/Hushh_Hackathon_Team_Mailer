"""
Flask Web Frontend for Email Agent
A modern web interface for the email automation system
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
import os
import pandas as pd
from werkzeug.utils import secure_filename
import tempfile
from email_agent import EmailAgent
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global agent instance
email_agent = None

def init_agent():
    """Initialize the email agent with API keys"""
    global email_agent
    
    # Try to get API keys from environment variables first
    google_api_key = os.getenv('GOOGLE_API_KEY', 'AIzaSyAYIuaAQJxmuspF5tyDEpJ3iYm6gVVQZOo')
    mailjet_api_key = os.getenv('MAILJET_API_KEY', 'cca56ed08f5272f813370d7fc5a34a24')
    mailjet_secret_key = os.getenv('MAILJET_SECRET_KEY', '60fb43675233e2ac775f1c6cb8fe455c')
    
    try:
        email_agent = EmailAgent(
            google_api_key=google_api_key,
            mailjet_api_key=mailjet_api_key,
            mailjet_secret_key=mailjet_secret_key
        )
        return True
    except Exception as e:
        print(f"Failed to initialize email agent: {e}")
        return False

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """API configuration page"""
    if request.method == 'POST':
        google_api_key = request.form.get('google_api_key')
        mailjet_api_key = request.form.get('mailjet_api_key')
        mailjet_secret_key = request.form.get('mailjet_secret_key')
        
        if not all([google_api_key, mailjet_api_key, mailjet_secret_key]):
            flash('All API keys are required!', 'error')
            return render_template('setup.html')
        
        # Save to environment or config file
        os.environ['GOOGLE_API_KEY'] = google_api_key
        os.environ['MAILJET_API_KEY'] = mailjet_api_key
        os.environ['MAILJET_SECRET_KEY'] = mailjet_secret_key
        
        if init_agent():
            flash('API keys configured successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Failed to initialize with provided API keys!', 'error')
    
    return render_template('setup.html')

@app.route('/upload_excel', methods=['POST'])
def upload_excel():
    """Handle Excel file upload"""
    if 'excel_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['excel_file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename.endswith(('.xlsx', '.xls')):
        filename = secure_filename(file.filename)
        
        # Save to temporary directory
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)
        file.save(filepath)
        
        try:
            # Read Excel file to validate and get column info
            df = pd.read_excel(filepath)
            columns = df.columns.tolist()
            row_count = len(df)
            
            # Check for required columns
            required_cols = ['email']
            missing_cols = [col for col in required_cols if col not in columns]
            
            if missing_cols:
                return jsonify({
                    'error': f'Missing required columns: {", ".join(missing_cols)}'
                }), 400
            
            return jsonify({
                'success': True,
                'filepath': filepath,
                'columns': columns,
                'row_count': row_count,
                'preview': df.head(5).to_dict('records')
            })
            
        except Exception as e:
            return jsonify({'error': f'Error reading Excel file: {str(e)}'}), 400
    
    return jsonify({'error': 'Invalid file format. Please upload .xlsx or .xls file'}), 400

@app.route('/draft_email', methods=['POST'])
def draft_email():
    """Draft email based on user input"""
    if not email_agent:
        return jsonify({'error': 'Email agent not initialized. Please configure API keys first.'}), 400
    
    data = request.json
    user_input = data.get('user_input', '')
    excel_file_path = data.get('excel_file_path', '')
    
    if not user_input:
        return jsonify({'error': 'User input is required'}), 400
    
    try:
        result = email_agent.draft_email_only(user_input, excel_file_path)
        
        if result:
            return jsonify({
                'success': True,
                'subject': result.get('subject', ''),
                'email_template': result.get('email_template', ''),
                'mass': result.get('mass', False)
            })
        else:
            return jsonify({'error': 'Failed to draft email'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Error drafting email: {str(e)}'}), 500

@app.route('/send_emails', methods=['POST'])
def send_emails():
    """Send emails to all recipients"""
    if not email_agent:
        return jsonify({'error': 'Email agent not initialized. Please configure API keys first.'}), 400
    
    data = request.json
    subject = data.get('subject', '')
    email_template = data.get('email_template', '')
    excel_file_path = data.get('excel_file_path', '')
    
    if not all([subject, email_template, excel_file_path]):
        return jsonify({'error': 'Subject, email template, and Excel file are required'}), 400
    
    # Create state for sending emails
    state = {
        'subject': subject,
        'email_template': email_template,
        'excel_file_path': excel_file_path,
        'approved': True
    }
    
    try:
        result = email_agent.send_emails(state)
        
        if result:
            return jsonify({
                'success': True,
                'emails_sent': result.get('emails_sent', 0),
                'total_emails': result.get('total_emails', 0),
                'message': f"Successfully sent {result.get('emails_sent', 0)} out of {result.get('total_emails', 0)} emails"
            })
        else:
            return jsonify({'error': 'Failed to send emails'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Error sending emails: {str(e)}'}), 500

@app.route('/preview_excel/<path:filepath>')
def preview_excel(filepath):
    """Preview Excel file data"""
    try:
        df = pd.read_excel(filepath)
        return jsonify({
            'columns': df.columns.tolist(),
            'data': df.head(10).to_dict('records'),
            'total_rows': len(df)
        })
    except Exception as e:
        return jsonify({'error': f'Error reading file: {str(e)}'}), 400

@app.route('/download_status/<path:filepath>')
def download_status(filepath):
    """Download email status file"""
    status_file = filepath.replace('.xlsx', '_status.xlsx')
    if os.path.exists(status_file):
        return send_file(status_file, as_attachment=True)
    else:
        flash('Status file not found', 'error')
        return redirect(url_for('index'))

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

if __name__ == '__main__':
    # Initialize agent on startup
    if not init_agent():
        print("Warning: Email agent could not be initialized. Please configure API keys.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
