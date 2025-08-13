"""
Complete startup script for the Relationship Memory Agent
"""
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_environment():
    """Check and load environment variables"""
    env_file = Path(".env")
    if not env_file.exists():
        print("Creating .env file...")
        with open(env_file, "w") as f:
            f.write("""# Database configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/relationship_memory

# AI configuration
GEMINI_API_KEY=your_gemini_api_key

# Vector DB configuration
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_env

# Security
SECRET_KEY=your_32_char_secret_key_here
VAULT_ENCRYPTION_KEY=your_64_char_encryption_key_here

# Agent configuration
AGENT_ID=agent_relationship_memory
ENVIRONMENT=development
""")
        print("Please update the .env file with your credentials")
        sys.exit(1)
    
    load_dotenv()
    required_vars = [
        "DATABASE_URL",
        "GEMINI_API_KEY",
        "PINECONE_API_KEY",
        "PINECONE_ENVIRONMENT"
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"Missing required environment variables: {missing}")
        print("Please update your .env file")
        sys.exit(1)
    
    print("✅ Environment variables loaded")

def init_database():
    """Initialize the database"""
    try:
        import psycopg2
        from sqlalchemy import create_engine
        from hushh_mcp.agents.relationship_memory.models import Base
        
        # Create database if it doesn't exist
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="postgres",
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='relationship_memory'")
        if not cursor.fetchone():
            cursor.execute("CREATE DATABASE relationship_memory")
        
        conn.close()
        
        # Create tables
        engine = create_engine(os.getenv("DATABASE_URL"))
        Base.metadata.create_all(engine)
        print("✅ Database initialized")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        sys.exit(1)

def init_vector_store():
    """Initialize vector store connection"""
    try:
        import pinecone
        
        pinecone.init(
            api_key=os.getenv("PINECONE_API_KEY"),
            environment=os.getenv("PINECONE_ENVIRONMENT")
        )
        
        # Create index if it doesn't exist
        index_name = "relationship-memories"
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=index_name,
                dimension=768,  # Gemini embedding dimension
                metric="cosine"
            )
        
        print("✅ Vector store initialized")
        
    except Exception as e:
        print(f"❌ Vector store initialization failed: {str(e)}")
        sys.exit(1)

def start_api():
    """Start the FastAPI server"""
    import uvicorn
    from fastapi import FastAPI
    from hushh_mcp.agents.relationship_memory.api import router
    
    app = FastAPI(title="Relationship Memory Agent")
    app.include_router(router)
    
    print("\n🚀 Starting API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

def main():
    """Main startup function"""
    print("Starting Relationship Memory Agent...\n")
    
    # Check environment
    check_environment()
    
    # Initialize database
    init_database()
    
    # Initialize vector store
    init_vector_store()
    
    # Start API server
    start_api()

if __name__ == "__main__":
    main()
