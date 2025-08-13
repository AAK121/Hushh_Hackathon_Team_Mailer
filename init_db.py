"""
Database initialization script
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Import models
from hushh_mcp.agents.relationship_memory.models import Base, Contact, RelationshipMemory, Reminder

# Load environment variables
load_dotenv()

def init_database():
    """Initialize the database with required tables"""
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/relationship_memory')
    
    # Create engine
    engine = create_engine(database_url)
    
    try:
        # Create all tables
        Base.metadata.create_all(engine)
        print("✅ Database tables created successfully")
        
        # Create session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Test connection
        session.execute(text("SELECT 1"))
        print("✅ Database connection test successful")
        
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_database()
