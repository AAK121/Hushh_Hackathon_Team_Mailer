#!/usr/bin/env python3
"""
Quick start script for Hushh Email Agent
Run this script to start the web application
"""

import sys
import subprocess
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask',
        'pandas',
        'mailjet_rest',
        'langchain_google_genai',
        'langgraph'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('_', '-'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Installing missing packages...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies. Please run manually:")
            print("   pip install -r requirements.txt")
            return False
    
    return True

def main():
    """Main function to start the application"""
    print("🚀 Starting Hushh Email Agent...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ app.py not found. Please run this script from the Mailer directory.")
        return
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Set environment variables if not already set
    env_vars = {
        'FLASK_ENV': 'development',
        'FLASK_DEBUG': '1'
    }
    
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
    
    print("🌟 Email Agent Features:")
    print("   ✨ AI-powered email generation")
    print("   📊 Excel file integration")
    print("   📧 Mass email sending")
    print("   🎨 Modern web interface")
    print("   📈 Real-time progress tracking")
    print()
    print("🌐 Web Interface: http://localhost:5000")
    print("🔧 API Setup: http://localhost:5000/setup")
    print()
    print("📝 Note: Configure your API keys at /setup before using")
    print("=" * 50)
    
    try:
        # Import and run the Flask app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n👋 Email Agent stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        print("💡 Try running: python app.py")

if __name__ == "__main__":
    main()
