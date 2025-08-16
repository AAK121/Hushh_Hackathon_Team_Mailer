"""
Unit tests for enhanced Pydantic models in the Proactive Relationship Manager Agent.
Tests the new fields and batch operation capabilities.
"""

import pytest
from typing import List, Dict
from pydantic import ValidationError

# Import the enhanced models
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from hushh_mcp.agents.relationship_memory.index import (
    ContactInfo, UserIntent, RelationshipMemoryState
)


class TestEnhancedContactInfo:
    """Test the enhanced ContactInfo model with priority and last_talked_date fields"""
    
    def test_contact_info_basic_creation(self):
        """Test basic contact creation with required fields only"""
        contact = ContactInfo(name="John Doe")
        
        assert contact.name == "John Doe"
        assert contact.email is None
        assert contact.phone is None
        assert contact.priority == "medium"  # Default value
        assert contact.last_talked_date is None
    
    def test_contact_info_with_all_fields(self):
        """Test contact creation with all fields including new ones"""
        contact = ContactInfo(
            name="Jane Smith",
            email="jane@example.com",
            phone="+1234567890",
            company="Tech Corp",
            location="San Francisco",
            notes="Met at conference",
            dates={"birthday": "15-03", "anniversary": "22-06"},
            priority="high",
            last_talked_date="2024-01-15"
        )
        
        assert contact.name == "Jane Smith"
        assert contact.email == "jane@example.com"
        assert contact.phone == "+1234567890"
        assert contact.company == "Tech Corp"
        assert contact.location == "San Francisco"
        assert contact.notes == "Met at conference"
        assert contact.dates == {"birthday": "15-03", "anniversary": "22-06"}
        assert contact.priority == "high"
        assert contact.last_talked_date == "2024-01-15"
    
    def test_contact_info_priority_validation(self):
        """Test that priority field only accepts valid values"""
        # Valid priorities
        for priority in ["high", "medium", "low"]:
            contact = ContactInfo(name="Test", priority=priority)
            assert contact.priority == priority
        
        # Invalid priority should raise validation error
        with pytest.raises(ValidationError):
            ContactInfo(name="Test", priority="invalid")
    
    def test_contact_info_date_format_validation(self):
        """Test last_talked_date accepts proper date format"""
        # Valid date format
        contact = ContactInfo(name="Test", last_talked_date="2024-01-15")
        assert contact.last_talked_date == "2024-01-15"
        
        # Note: We're not enforcing strict date validation in the model
        # but this test documents the expected format


class TestEnhancedUserIntent:
    """Test the enhanced UserIntent model with batch operations and advice requests"""
    
    def test_user_intent_get_advice_action(self):
        """Test that get_advice action is supported"""
        intent = UserIntent(
            action="get_advice",
            confidence=0.9,
            contact_name="John Doe"
        )
        
        assert intent.action == "get_advice"
        assert intent.confidence == 0.9
        assert intent.contact_name == "John Doe"
    
    def test_user_intent_batch_contact_info(self):
        """Test that contact_info accepts a list of ContactInfo objects"""
        contacts = [
            ContactInfo(name="John Doe", email="john@example.com"),
            ContactInfo(name="Jane Smith", phone="+1234567890", priority="high")
        ]
        
        intent = UserIntent(
            action="add_contact",
            confidence=0.95,
            contact_info=contacts
        )
        
        assert intent.action == "add_contact"
        assert intent.confidence == 0.95
        assert len(intent.contact_info) == 2
        assert intent.contact_info[0].name == "John Doe"
        assert intent.contact_info[1].name == "Jane Smith"
        assert intent.contact_info[1].priority == "high"
    
    def test_user_intent_single_contact_as_list(self):
        """Test that single contact can be provided as a list"""
        contact = ContactInfo(name="Single Contact")
        
        intent = UserIntent(
            action="add_contact",
            confidence=0.8,
            contact_info=[contact]
        )
        
        assert len(intent.contact_info) == 1
        assert intent.contact_info[0].name == "Single Contact"
    
    def test_user_intent_empty_contact_list(self):
        """Test that empty contact list is handled properly"""
        intent = UserIntent(
            action="add_contact",
            confidence=0.5,
            contact_info=[]
        )
        
        assert intent.contact_info == []
    
    def test_user_intent_all_actions_supported(self):
        """Test that all expected actions are supported"""
        expected_actions = [
            "add_contact", "add_memory", "add_reminder", 
            "show_contacts", "show_memories", "show_reminders", 
            "search_contacts", "get_contact_details", "add_date", 
            "show_upcoming_dates", "get_advice", "unknown"
        ]
        
        for action in expected_actions:
            intent = UserIntent(action=action, confidence=0.8)
            assert intent.action == action
    
    def test_user_intent_invalid_action(self):
        """Test that invalid actions raise validation error"""
        with pytest.raises(ValidationError):
            UserIntent(action="invalid_action", confidence=0.8)


class TestEnhancedRelationshipMemoryState:
    """Test the enhanced RelationshipMemoryState with proactive fields"""
    
    def test_relationship_memory_state_basic(self):
        """Test basic state creation with existing fields"""
        state = RelationshipMemoryState(
            user_input="test input",
            user_id="user123",
            vault_key="vault_key_123",
            parsed_intent=None,
            result_data=[],
            response_message="",
            error=None,
            action_taken="",
            is_startup=False,
            proactive_triggers=[],
            conversation_history=[]
        )
        
        assert state["user_input"] == "test input"
        assert state["user_id"] == "user123"
        assert state["vault_key"] == "vault_key_123"
        assert state["is_startup"] is False
        assert state["proactive_triggers"] == []
        assert state["conversation_history"] == []
    
    def test_relationship_memory_state_with_proactive_data(self):
        """Test state with proactive triggers and conversation history"""
        triggers = [
            {
                'type': 'upcoming_event',
                'contact_name': 'Jane Doe',
                'event_type': 'birthday',
                'days_until': 5
            },
            {
                'type': 'reconnection',
                'contact_name': 'John Smith',
                'days_since_contact': 45,
                'priority': 'medium'
            }
        ]
        
        history = ["Previous conversation", "Another message"]
        
        state = RelationshipMemoryState(
            user_input="startup check",
            user_id="user123",
            vault_key="vault_key_123",
            parsed_intent=None,
            result_data=[],
            response_message="",
            error=None,
            action_taken="proactive_check",
            is_startup=True,
            proactive_triggers=triggers,
            conversation_history=history
        )
        
        assert state["is_startup"] is True
        assert state["action_taken"] == "proactive_check"
        assert len(state["proactive_triggers"]) == 2
        assert state["proactive_triggers"][0]["type"] == "upcoming_event"
        assert state["proactive_triggers"][1]["type"] == "reconnection"
        assert len(state["conversation_history"]) == 2


class TestModelIntegration:
    """Test integration between enhanced models"""
    
    def test_user_intent_with_enhanced_contact_info(self):
        """Test UserIntent with enhanced ContactInfo including new fields"""
        contacts = [
            ContactInfo(
                name="Alice Johnson",
                email="alice@example.com",
                priority="high",
                last_talked_date="2024-01-10"
            ),
            ContactInfo(
                name="Bob Wilson",
                phone="+1987654321",
                priority="low",
                last_talked_date="2023-12-15"
            )
        ]
        
        intent = UserIntent(
            action="add_contact",
            confidence=0.92,
            contact_info=contacts
        )
        
        # Verify the integration works properly
        assert len(intent.contact_info) == 2
        assert intent.contact_info[0].priority == "high"
        assert intent.contact_info[0].last_talked_date == "2024-01-10"
        assert intent.contact_info[1].priority == "low"
        assert intent.contact_info[1].last_talked_date == "2023-12-15"
    
    def test_state_with_enhanced_intent(self):
        """Test RelationshipMemoryState with enhanced UserIntent"""
        contacts = [ContactInfo(name="Test Contact", priority="medium")]
        intent = UserIntent(
            action="add_contact",
            confidence=0.85,
            contact_info=contacts
        )
        
        state = RelationshipMemoryState(
            user_input="add contact test",
            user_id="user123",
            vault_key="vault_key_123",
            parsed_intent=intent,
            result_data=[],
            response_message="",
            error=None,
            action_taken="",
            is_startup=False,
            proactive_triggers=[],
            conversation_history=[]
        )
        
        # Verify the integration
        assert state["parsed_intent"].action == "add_contact"
        assert len(state["parsed_intent"].contact_info) == 1
        assert state["parsed_intent"].contact_info[0].priority == "medium"


if __name__ == "__main__":
    pytest.main([__file__])