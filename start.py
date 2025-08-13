"""
Startup script for the Relationship Memory Agent
Checks all dependencies and initializes required services
"""
import sys
import subprocess
import os
from pathlib import Path

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "psycopg2-binary",
        "redis",
        "celery",
        "google-generativeai",
        "langchain",
        "pinecone-client",
        "python-dotenv"
    ]
    
    print("Checking dependencies...")
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print("\nInstalling missing packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)

def check_services():
    """Check if required services are running"""
    # Check PostgreSQL
    try:
        import psycopg2
        conn = psycopg2.connect(os.getenv('DATABASE_URL', "postgresql://postgres:postgres@localhost:5432/relationship_memory"))
        conn.close()
        print("✅ PostgreSQL is running")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL error: {str(e)}")
        return False

def init_environment():
    """Initialize environment variables"""
    from dotenv import load_dotenv
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    load_dotenv()
    required_vars = [
        "DATABASE_URL",
        "GEMINI_API_KEY",
        "PINECONE_API_KEY",
        "PINECONE_ENVIRONMENT",
        "SECRET_KEY",
        "VAULT_ENCRYPTION_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:", missing_vars)
        return False
    
    print("✅ Environment variables loaded")
    return True

def init_database():
    """Initialize database tables"""
    try:
        import init_db
        init_db.init_database()
        print("✅ Database initialized")
        return True
    except Exception as e:
        print(f"❌ Database initialization error: {str(e)}")
        return False

def main():
    """Main initialization function"""
    print("Starting Relationship Memory Agent initialization...\n")
    
    # Check and install dependencies
    check_dependencies()
    print("\nChecking services...")
    if not check_services():
        print("\n❌ Required services are not running. Please start PostgreSQL and Redis.")
        return
    
    print("\nInitializing environment...")
    if not init_environment():
        print("\n❌ Environment initialization failed. Please check your .env file.")
        return
    
    print("\nInitializing database...")
    if not init_database():
        print("\n❌ Database initialization failed.")
        return
    
    print("\n✅ All systems initialized successfully!")
    print("\nStarting the agent API server...")
    
    # Start the FastAPI server
    import uvicorn
    uvicorn.run("run_agent:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
