#!/usr/bin/env python3
"""
GmailCat PDA Web Application Startup Script
Powered by HushMCP Framework
"""

import os
import sys
import subprocess
import django
from pathlib import Path

def main():
    """Main startup function for GmailCat PDA webapp."""
    print("🐱 Starting GmailCat PDA Web Application...")
    print("=" * 50)
    
    # Get the webapp directory
    webapp_dir = Path(__file__).parent
    os.chdir(webapp_dir)
    
    # Check if Django is installed
    try:
        import django
        print(f"✅ Django {django.get_version()} found")
    except ImportError:
        print("❌ Django not found. Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        import django
        print(f"✅ Django {django.get_version()} installed")
    
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_settings.settings')
    
    # Check if database exists, create if not
    db_path = webapp_dir / 'db.sqlite3'
    if not db_path.exists():
        print("🔧 Setting up database...")
        subprocess.run([sys.executable, "manage.py", "migrate", "--run-syncdb"])
        print("✅ Database created")
    
    # Check environment variables
    env_path = webapp_dir.parent / '.env'
    if env_path.exists():
        print("✅ Environment file found")
    else:
        print("⚠️  No .env file found. Make sure OPENAI_API_KEY is set")
    
    print("\n🚀 Starting development server...")
    print("📱 Open your browser and go to: http://127.0.0.1:8000")
    print("🔧 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the Django development server
    try:
        subprocess.run([sys.executable, "manage.py", "runserver", "127.0.0.1:8000"])
    except KeyboardInterrupt:
        print("\n👋 GmailCat PDA shutting down. Goodbye!")

if __name__ == "__main__":
    main()
