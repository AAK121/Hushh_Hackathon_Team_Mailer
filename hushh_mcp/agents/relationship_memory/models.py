"""
Database models for the Relationship Memory Agent
Using SQLAlchemy for PostgreSQL integration
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, JSON, Float, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY
import sqlalchemy.orm as orm

class Base(DeclarativeBase):
    pass

class Contact(Base):
    """Contact model representing a person in the relationship memory system"""
    __tablename__ = 'contacts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    relationship: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    birthday: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    memories: Mapped[List["RelationshipMemory"]] = orm.relationship("RelationshipMemory", back_populates="contact")
    reminders: Mapped[List["Reminder"]] = orm.relationship("Reminder", back_populates="contact")

class RelationshipMemory(Base):
    """Memory model representing interactions and events with contacts"""
    __tablename__ = 'relationship_memories'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    contact_id: Mapped[int] = mapped_column(ForeignKey('contacts.id'), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    detailed_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    embedding_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    vector_embedding: Mapped[Optional[List[float]]] = mapped_column(ARRAY(Float), nullable=True)
    sentiment: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tags: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relationships
    contact: Mapped["Contact"] = orm.relationship("Contact", back_populates="memories")

class Reminder(Base):
    """Reminder model for scheduling follow-ups and important dates"""
    __tablename__ = 'reminders'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    contact_id: Mapped[int] = mapped_column(ForeignKey('contacts.id'), nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)  # birthday, follow-up, check-in, etc.
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    recurrence: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # daily, weekly, monthly, yearly
    status: Mapped[str] = mapped_column(String, server_default='pending')
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relationships
    contact: Mapped["Contact"] = orm.relationship("Contact", back_populates="reminders")
