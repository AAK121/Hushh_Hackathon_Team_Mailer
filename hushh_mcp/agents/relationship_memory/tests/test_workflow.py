"""
Test the complete agent workflow end-to-end
"""

import pytest
from typing import Dict, Any


class TestAgentWorkflow:
    """Test complete agent workflow scenarios"""
    
    def test_complete_contact_lifecycle(self, agent_handler):
        """Test complete contact management lifecycle"""
        # 1. Add new contact
        result = agent_handler("add contact Sarah Johnson with email sarah@email.com")
        assert result["status"] == "success"
        assert result["action_taken"] == "add_contact"
        
        # 2. Add memory
        result = agent_handler("remember that Sarah loves coffee and works at tech company")
        assert result["status"] == "success"
        assert result["action_taken"] == "add_memory"
        
        # 3. Add date
        result = agent_handler("Sarah's birthday is on 15 march")
        assert result["status"] == "success"
        assert result["action_taken"] == "add_date"
        
        # 4. Add reminder
        result = agent_handler("remind me to send birthday wishes to Sarah")
        assert result["status"] == "success"
        assert result["action_taken"] == "add_reminder"
        
        # 5. Show contact details
        result = agent_handler("show details for Sarah Johnson")
        assert result["status"] == "success"
        assert "coffee" in result["message"]
        assert "15-03" in result["message"]
        
        # 6. Update contact
        result = agent_handler("update Sarah Johnson's email to sarah.new@email.com")
        assert result["status"] == "success"
        assert result["action_taken"] == "add_contact"
        
    def test_memory_accumulation(self, agent_handler):
        """Test that multiple memories accumulate for a contact"""
        # Add contact
        agent_handler("add contact David Kim to contacts")
        
        # Add multiple memories
        memories = [
            "David is a software engineer",
            "David loves hiking on weekends",
            "David has a dog named Max",
            "David graduated from MIT"
        ]
        
        for memory in memories:
            result = agent_handler(f"remember that {memory}")
            assert result["status"] == "success"
            
        # Check all memories are stored
        result = agent_handler("show memories for David Kim")
        assert result["status"] == "success"
        for memory_key in ["engineer", "hiking", "dog", "MIT"]:
            assert memory_key in result["message"]
            
    def test_date_management_workflow(self, agent_handler):
        """Test complete date management workflow"""
        # Add contact
        agent_handler("add contact Emma Watson to contacts")
        
        # Add multiple dates
        dates = [
            ("Emma's birthday is on 20 april", "birthday", "20-04"),
            ("Emma's anniversary is on 10 june", "anniversary", "10-06"),
            ("Emma's graduation is on 5 september", "graduation", "05-09")
        ]
        
        for date_input, date_type, expected_date in dates:
            result = agent_handler(date_input)
            assert result["status"] == "success"
            assert result["action_taken"] == "add_date"
            
        # Show contact details
        result = agent_handler("show details for Emma Watson")
        assert result["status"] == "success"
        assert "20-04" in result["message"]
        assert "10-06" in result["message"]
        assert "05-09" in result["message"]
        
        # Show upcoming dates
        result = agent_handler("show upcoming dates")
        assert result["status"] == "success"
        
    def test_reminder_workflow(self, agent_handler):
        """Test reminder management workflow"""
        # Add contact
        agent_handler("add contact Michael Brown to contacts")
        
        # Add multiple reminders
        reminders = [
            "remind me to call Michael about project",
            "remind me to send Michael the document",
            "remind me to invite Michael to dinner"
        ]
        
        for reminder in reminders:
            result = agent_handler(reminder)
            assert result["status"] == "success"
            assert result["action_taken"] == "add_reminder"
            
        # Show all reminders
        result = agent_handler("show all my reminders")
        assert result["status"] == "success"
        assert "call Michael" in result["message"]
        assert "document" in result["message"]
        assert "dinner" in result["message"]
        
    def test_cross_feature_interactions(self, agent_handler):
        """Test interactions between different features"""
        # Create a complex scenario
        agent_handler("add contact Lisa Chen with email lisa@company.com")
        agent_handler("remember that Lisa is project manager at startup")
        agent_handler("Lisa's work anniversary is on 1 january")
        agent_handler("remind me to congratulate Lisa on work anniversary")
        
        # Show contact should include all information
        result = agent_handler("show details for Lisa Chen")
        assert result["status"] == "success"
        message = result["message"]
        assert "Lisa Chen" in message
        assert "lisa@company.com" in message
        assert "project manager" in message
        assert "01-01" in message
        
        # Show upcoming dates should include Lisa's anniversary
        result = agent_handler("show upcoming dates")
        assert result["status"] == "success"
        
        # Show reminders should include Lisa's reminder
        result = agent_handler("show all reminders")
        assert result["status"] == "success"
        assert "Lisa" in result["message"]
        
    def test_error_handling_workflow(self, agent_handler):
        """Test error handling in various scenarios"""
        # Try to add memory for non-existent contact
        result = agent_handler("remember that NonExistent loves pizza")
        assert result["status"] == "error"
        assert "not found" in result["message"]
        
        # Try to add date for non-existent contact
        result = agent_handler("NonExistent's birthday is on 25 december")
        assert result["status"] == "error"
        assert "not found" in result["message"]
        
        # Try to show details for non-existent contact
        result = agent_handler("show details for NonExistent")
        assert result["status"] == "error"
        assert "not found" in result["message"]
        
    def test_data_persistence(self, agent_handler):
        """Test that data persists between operations"""
        # Add contact with full information
        agent_handler("add contact Alex Rodriguez with email alex@email.com")
        agent_handler("remember that Alex is a chef and loves cooking Italian food")
        agent_handler("Alex's birthday is on 8 july")
        agent_handler("remind me to book restaurant with Alex")
        
        # Perform other operations
        agent_handler("add contact Another Person to contacts")
        agent_handler("show all contacts")
        
        # Verify original contact data still exists
        result = agent_handler("show details for Alex Rodriguez")
        assert result["status"] == "success"
        assert "alex@email.com" in result["message"]
        assert "chef" in result["message"]
        assert "08-07" in result["message"]
        
        result = agent_handler("show all reminders")
        assert result["status"] == "success"
        assert "Alex" in result["message"]
        
    def test_edge_cases(self, agent_handler):
        """Test edge cases and boundary conditions"""
        # Very long names
        result = agent_handler("add contact Very Long Name With Multiple Words Here to contacts")
        assert result["status"] == "success"
        
        # Special characters in memory
        agent_handler("add contact Test Person to contacts")
        result = agent_handler("remember that Test Person said 'Hello, world!' and uses email@domain.co.uk")
        assert result["status"] == "success"
        
        # Multiple contacts with similar names
        agent_handler("add contact John Smith to contacts")
        agent_handler("add contact John Johnson to contacts")
        
        result = agent_handler("show all contacts")
        assert result["status"] == "success"
        assert "John Smith" in result["message"]
        assert "John Johnson" in result["message"]
