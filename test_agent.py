"""
Test script for the Relationship Memory Agent
Demonstrates key functionalities and interactions
"""
import os
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import numpy as np

# Import our models
from hushh_mcp.agents.relationship_memory.models import Base, Contact, RelationshipMemory, Reminder

# Load environment variables
load_dotenv()

class RelationshipMemoryAgent:
    def __init__(self):
        """Initialize the agent with database connection"""
        database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/relationship_memory')
        self.engine = create_engine(database_url)
        self.user_id = "test_user_1"  # Simulating a logged-in user

    def create_contact(self, name: str, email: Optional[str] = None, 
                      phone: Optional[str] = None, relationship: Optional[str] = None,
                      birthday: Optional[datetime] = None, notes: Optional[str] = None) -> Contact:
        """Create a new contact"""
        with Session(self.engine) as session:
            contact = Contact(
                user_id=self.user_id,
                name=name,
                email=email,
                phone=phone,
                relationship=relationship,
                birthday=birthday,
                notes=notes
            )
            session.add(contact)
            session.commit()
            # Refresh the instance to get generated values
            session.refresh(contact)
            # Make a copy of important attributes
            result = {
                'id': contact.id,
                'name': contact.name,
                'email': contact.email
            }
        return result

    def add_memory(self, contact_id: int, summary: str, detailed_notes: Optional[str] = None,
                   sentiment: Optional[str] = None, tags: Optional[dict] = None) -> dict:
        """Add a new memory for a contact"""
        with Session(self.engine) as session:
            # Create a simple vector embedding (in real app, this would use an AI model)
            vector = np.random.rand(1536).tolist()  # Simulating a vector embedding
            
            memory = RelationshipMemory(
                user_id=self.user_id,
                contact_id=contact_id,
                summary=summary,
                detailed_notes=detailed_notes,
                vector_embedding=vector,
                sentiment=sentiment,
                tags=tags
            )
            session.add(memory)
            session.commit()
            session.refresh(memory)
            return {
                'id': memory.id,
                'summary': memory.summary,
                'sentiment': memory.sentiment
            }

    def set_reminder(self, contact_id: int, title: str, scheduled_at: datetime,
                    reminder_type: str = "follow-up", description: Optional[str] = None,
                    recurrence: Optional[str] = None) -> dict:
        """Set a new reminder for a contact"""
        with Session(self.engine) as session:
            reminder = Reminder(
                user_id=self.user_id,
                contact_id=contact_id,
                type=reminder_type,
                title=title,
                description=description,
                scheduled_at=scheduled_at,
                recurrence=recurrence,
                status="pending"
            )
            session.add(reminder)
            session.commit()
            session.refresh(reminder)
            return {
                'id': reminder.id,
                'title': reminder.title,
                'scheduled_at': reminder.scheduled_at
            }

    def get_contact_memories(self, contact_id: int) -> List[dict]:
        """Get all memories for a contact"""
        with Session(self.engine) as session:
            stmt = select(RelationshipMemory).where(
                RelationshipMemory.contact_id == contact_id,
                RelationshipMemory.user_id == self.user_id
            )
            memories = session.execute(stmt).scalars().all()
            return [
                {
                    'id': mem.id,
                    'summary': mem.summary,
                    'sentiment': mem.sentiment,
                    'detailed_notes': mem.detailed_notes
                }
                for mem in memories
            ]

    def get_upcoming_reminders(self, days: int = 7) -> List[dict]:
        """Get upcoming reminders for the next N days"""
        with Session(self.engine) as session:
            # Use a join to get contact information
            stmt = select(Reminder, Contact).join(Contact).where(
                Reminder.user_id == self.user_id,
                Reminder.scheduled_at <= datetime.now() + timedelta(days=days),
                Reminder.scheduled_at >= datetime.now(),
                Reminder.status == "pending"
            )
            results = session.execute(stmt).all()
            return [
                {
                    'id': rem[0].id,
                    'title': rem[0].title,
                    'scheduled_at': rem[0].scheduled_at,
                    'contact_name': rem[1].name
                }
                for rem in results
            ]

    def search_memories_by_sentiment(self, sentiment: str) -> List[dict]:
        """Search memories by sentiment"""
        with Session(self.engine) as session:
            stmt = select(RelationshipMemory, Contact).join(Contact).where(
                RelationshipMemory.user_id == self.user_id,
                RelationshipMemory.sentiment == sentiment
            )
            results = session.execute(stmt).all()
            return [
                {
                    'id': mem[0].id,
                    'summary': mem[0].summary,
                    'sentiment': mem[0].sentiment,
                    'contact_name': mem[1].name
                }
                for mem in results
            ]

    def get_all_contacts(self) -> List[dict]:
        """Get all contacts for the current user"""
        with Session(self.engine) as session:
            stmt = select(Contact).where(Contact.user_id == self.user_id)
            contacts = session.execute(stmt).scalars().all()
            return [
                {
                    'id': contact.id,
                    'name': contact.name,
                    'email': contact.email,
                    'relationship': contact.relationship,
                    'birthday': contact.birthday.strftime('%Y-%m-%d') if contact.birthday else None
                }
                for contact in contacts
            ]

def test_agent():
    """Run a comprehensive test of the agent's functionality"""
    # Clear existing data
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/relationship_memory'))
    with Session(engine) as session:
        session.execute(text("TRUNCATE TABLE reminders, relationship_memories, contacts CASCADE"))
        session.commit()
    
    agent = RelationshipMemoryAgent()
    
    # 1. Create contacts
    print("\n1. Creating contacts...")
    alice = agent.create_contact(
        name="Alice Johnson",
        email="alice@example.com",
        phone="+1-555-0101",
        relationship="Colleague",
        birthday=datetime(1992, 3, 15),
        notes="Met at AI Conference 2025"
    )
    print(f"Created contact: {alice['name']} (ID: {alice['id']})")

    bob = agent.create_contact(
        name="Bob Smith",
        email="bob@example.com",
        phone="+1-555-0102",
        relationship="Client",
        notes="Interested in our ML solutions"
    )
    print(f"Created contact: {bob['name']} (ID: {bob['id']})")

    # 2. Add memories
    print("\n2. Adding memories...")
    memory1 = agent.add_memory(
        contact_id=alice['id'],
        summary="Project collaboration discussion",
        detailed_notes="Discussed ML pipeline optimization project. Alice has great insights on transformer models.",
        sentiment="positive",
        tags={"project": "ML Pipeline", "topics": ["transformers", "optimization"]}
    )
    print(f"Added memory for {alice['name']}: {memory1['summary']}")

    memory2 = agent.add_memory(
        contact_id=bob['id'],
        summary="Initial consultation meeting",
        detailed_notes="Bob expressed interest in implementing our ML solutions. Needs proposal by next week.",
        sentiment="positive",
        tags={"type": "sales", "priority": "high"}
    )
    print(f"Added memory for {bob['name']}: {memory2['summary']}")

    # 3. Set reminders
    print("\n3. Setting reminders...")
    reminder1 = agent.set_reminder(
        contact_id=alice['id'],
        title="Review ML pipeline proposal",
        scheduled_at=datetime.now() + timedelta(days=3),
        reminder_type="follow-up",
        description="Review and discuss the initial pipeline design"
    )
    print(f"Set reminder for {alice['name']}: {reminder1['title']}")

    reminder2 = agent.set_reminder(
        contact_id=bob['id'],
        title="Send project proposal",
        scheduled_at=datetime.now() + timedelta(days=5),
        reminder_type="task",
        description="Prepare and send the ML implementation proposal"
    )
    print(f"Set reminder for {bob['name']}: {reminder2['title']}")

    # 4. Query and display information
    print("\n4. Retrieving information...")
    
    # Get memories for Alice
    print(f"\nMemories for {alice['name']}:")
    memories = agent.get_contact_memories(alice['id'])
    for memory in memories:
        print(f"- {memory['summary']} (Sentiment: {memory['sentiment']})")
    
    # Get upcoming reminders
    print("\nUpcoming reminders (next 7 days):")
    reminders = agent.get_upcoming_reminders()
    for reminder in reminders:
        print(f"- {reminder['title']} for {reminder['contact_name']} on {reminder['scheduled_at'].date()}")
    
    # Search positive memories
    print("\nPositive interactions:")
    positive_memories = agent.search_memories_by_sentiment("positive")
    for memory in positive_memories:
        print(f"- {memory['summary']} with {memory['contact_name']}")

if __name__ == "__main__":
    test_agent()
