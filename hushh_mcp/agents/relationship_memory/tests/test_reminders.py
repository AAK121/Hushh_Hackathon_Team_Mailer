"""
Test reminder management functionality
"""

import pytest
from typing import Dict, Any


class TestReminderManagement:
    """Test suite for reminder management features"""
    
    def test_add_simple_reminder(self, agent_handler):
        """Test adding a simple reminder"""
        agent_handler("add Mark Cuban to contacts")
        
        result = agent_handler("remind me to call Mark next week")
        
        assert result["status"] == "success"
        assert result["action_taken"] == "add_reminder"
        assert "Mark" in result["message"]
        
    def test_add_reminder_with_date(self, agent_handler):
        """Test adding a reminder with specific date"""
        agent_handler("add Elon Musk to contacts")
        
        result = agent_handler("remind me to email Elon on 2024-12-25")
        
        assert result["status"] == "success"
        assert result["action_taken"] == "add_reminder"
        
    def test_show_all_reminders(self, agent_handler):
        """Test showing all reminders"""
        # Add some reminders
        agent_handler("add Jeff Bezos to contacts")
        agent_handler("remind me to follow up with Jeff")
        
        result = agent_handler("show me all reminders")
        
        assert result["status"] == "success"
        assert result["action_taken"] == "show_reminders"
        
    def test_reminder_with_priority(self, agent_handler):
        """Test adding reminders with different priorities"""
        agent_handler("add Bill Gates to contacts")
        
        result = agent_handler("urgent reminder to call Bill about the meeting")
        
        assert result["status"] == "success"
        assert result["action_taken"] == "add_reminder"
        
    def test_multiple_reminders_per_contact(self, agent_handler):
        """Test adding multiple reminders for the same contact"""
        agent_handler("add Warren Buffett to contacts")
        
        # Add multiple reminders
        agent_handler("remind me to send Warren the report")
        agent_handler("remind me to schedule meeting with Warren")
        
        result = agent_handler("show me all reminders")
        
        assert result["status"] == "success"
        assert result["action_taken"] == "show_reminders"
        
    def test_reminder_in_contact_details(self, agent_handler):
        """Test that reminders appear in contact details"""
        agent_handler("add Oprah Winfrey to contacts")
        agent_handler("remind me to congratulate Oprah on her success")
        
        result = agent_handler("show me the details of Oprah Winfrey")
        
        assert result["status"] == "success"
        assert result["action_taken"] == "get_contact_details"
        assert "Oprah Winfrey" in result["message"]
