"""
Test script to populate the database with sample data
"""
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Import models
from hushh_mcp.agents.relationship_memory.models import Base, Contact, RelationshipMemory, Reminder

# Load environment variables
load_dotenv()

def create_test_data():
    """Create sample data for testing"""
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/relationship_memory')
    
    # Create engine and session
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Create a test contact
        contact = Contact(
            user_id="test_user_1",
            name="John Doe",
            email="john.doe@example.com",
            phone="+1-555-0123",
            relationship="Friend",
            birthday=datetime(1990, 5, 15),
            notes="Met at the tech conference in San Francisco"
        )
        session.add(contact)
        session.flush()  # Get the ID without committing
        
        # Create a memory for the contact
        memory = RelationshipMemory(
            user_id="test_user_1",
            contact_id=contact.id,
            summary="First meeting at TechConf 2025",
            detailed_notes="Had a great conversation about AI and machine learning. John works as a senior developer at TechCorp.",
            sentiment="positive",
            tags={"topics": ["AI", "ML", "career"], "location": "San Francisco"}
        )
        session.add(memory)
        
        # Create a reminder for the contact
        reminder = Reminder(
            user_id="test_user_1",
            contact_id=contact.id,
            type="follow-up",
            title="Schedule coffee meetup",
            description="Follow up on ML collaboration discussion",
            scheduled_at=datetime.now() + timedelta(days=7),
            recurrence="none",
            status="pending"
        )
        session.add(reminder)
        
        # Commit the changes
        session.commit()
        print("✅ Test data created successfully")
        
        # Verify the relationships
        # Reload the contact to get fresh data
        contact = session.query(Contact).filter_by(id=contact.id).first()
        print("\nVerifying relationships:")
        print(f"Contact: {contact.name}")
        print(f"Memories count: {len(contact.memories)}")
        print(f"First memory summary: {contact.memories[0].summary}")
        print(f"Reminders count: {len(contact.reminders)}")
        print(f"First reminder title: {contact.reminders[0].title}")
        
    except Exception as e:
        print(f"❌ Error creating test data: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    create_test_data()
