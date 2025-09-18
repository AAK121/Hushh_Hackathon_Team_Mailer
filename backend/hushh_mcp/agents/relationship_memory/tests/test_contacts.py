"""
Test contact management functionality
"""

import pytest
from typing import Dict, Any


class TestContactManagement:
    """Test suite for contact management features"""
    
    def test_add_new_contact(self, agent_handler):
        """Test adding a new contact"""
        result = agent_handler("add John Doe to contacts")
        
        assert result["status"] == "success"
        assert result["action_taken"] == "add_contact"
        assert "John Doe" in result["message"]
        
    def test_add_contact_with_email(self, agent_handler):
        """Test adding a contact with email"""
        result = agent_handler("add Jane Smith with email jane@example.com")
        
        assert result["status"] == "success"
        assert result["action_taken"] == "add_contact"
        assert "Jane Smith" in result["message"]
        
    def test_update_existing_contact_email(self, agent_handler):
        """Test updating an existing contact's email"""
        # First add a contact
        agent_handler("add Bob Wilson to contacts")
        
        # Then update the email
        result = agent_handler("add email for Bob Wilson as bob@test.com")
        
        assert result["status"] == "success"
        assert result["action_taken"] == "update_contact"
        assert "email" in result["message"]
        
    def test_show_contacts(self, agent_handler):
        """Test showing all contacts"""
        # Add some contacts first
        agent_handler("add Alice Cooper to contacts")
        agent_handler("add David Bowie to contacts")
        
        result = agent_handler("show contacts")
        
        assert result["status"] == "success"
        assert result["action_taken"] == "show_contacts"
        assert "Found" in result["message"]
        
    def test_get_contact_details(self, agent_handler):
        """Test getting detailed contact information"""
        # Add a contact first
        agent_handler("add Sarah Connor with email sarah@resistance.com")
        
        result = agent_handler("show me the details of Sarah Connor")
        
        assert result["status"] == "success"
        assert result["action_taken"] == "get_contact_details"
        assert "Sarah Connor" in result["message"]
        
    def test_contact_uniqueness(self, agent_handler):
        """Test that duplicate contacts are handled properly"""
        # Add a contact
        agent_handler("add Tom Hanks to contacts")
        
        # Try to add the same contact again
        result = agent_handler("add Tom Hanks to contacts")
        
        assert result["status"] == "success"
        # Should either update or indicate contact exists
        assert result["action_taken"] in ["update_contact", "contact_unchanged"]
        
    def test_add_contact_with_multiple_details(self, agent_handler):
        """Test adding a contact with multiple details"""
        result = agent_handler("add Michael Jordan with email mj@bulls.com and phone 555-1234")
        
        assert result["status"] == "success"
        assert result["action_taken"] == "add_contact"
        assert "Michael Jordan" in result["message"]
