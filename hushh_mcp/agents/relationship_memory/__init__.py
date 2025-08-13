"""
Initialization script for the Relationship Memory Agent
"""

import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_agent():
    """Initialize the Relationship Memory Agent"""
    try:
        # Initialize database
        from .db import init_db
        init_db()
        logger.info("Database initialized successfully")
        
        # Initialize vector store namespace
        import pinecone
        pinecone.init(
            api_key="YOUR_PINECONE_API_KEY",
            environment="YOUR_PINECONE_ENV"
        )
        
        # Create index if it doesn't exist
        if "relationship-memories" not in pinecone.list_indexes():
            pinecone.create_index(
                "relationship-memories",
                dimension=1536,  # OpenAI embedding dimension
                metric="cosine"
            )
        logger.info("Vector store initialized successfully")
        
        # Initialize Celery beat schedule
        from .reminder_engine import celery_app
        celery_app.conf.beat_schedule = {
            'check-upcoming-reminders': {
                'task': 'check_upcoming_reminders',
                'schedule': 300.0,  # Every 5 minutes
            }
        }
        logger.info("Reminder scheduler initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing agent: {str(e)}")
        raise

if __name__ == "__main__":
    init_agent()
