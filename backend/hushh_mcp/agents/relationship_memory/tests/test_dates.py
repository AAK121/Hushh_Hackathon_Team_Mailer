"""
Test date management functionality
"""

import pytest
from typing import Dict, Any


class TestDateManagement:
    """Test suite for date management features"""
    
    def test_add_birthday(self, agent_handler):
        """Test adding a birthday to a contact"""
        # Add contact first
        agent_handler("add Taylor Swift to contacts")
        
        result = agent_handler("Taylor's birthday is on 13 december")
        
        assert result["status"] == "success"
        assert result["action_taken"] == "add_date"
        assert "birthday" in result["message"]
        assert "Taylor" in result["message"]
        
    def test_add_anniversary(self, agent_handler):
        """Test adding an anniversary"""
        agent_handler("add John Smith to contacts")
        
        result = agent_handler("add anniversary for John on 25 june 2018")
        
        assert result["status"] == "success"
        assert result["action_taken"] == "add_date"
        assert "anniversary" in result["message"]
        
    def test_add_multiple_dates_per_contact(self, agent_handler):
        """Test adding multiple dates to the same contact"""
        agent_handler("add Emma Stone to contacts")
        
        # Add birthday
        result1 = agent_handler("Emma's birthday is on 6 november")
        assert result1["status"] == "success"
        
        # Add graduation
        result2 = agent_handler("add graduation for Emma on 15 may")
        assert result2["status"] == "success"
        
    def test_show_upcoming_dates(self, agent_handler):
        """Test showing upcoming important dates"""
        # Add contacts with dates
        agent_handler("add Brad Pitt to contacts")
        agent_handler("Brad's birthday is on 18 december")
        
        result = agent_handler("show upcoming important dates")
        
        assert result["status"] == "success"
        assert result["action_taken"] == "show_upcoming_dates"
        
    def test_dates_in_contact_details(self, agent_handler):
        """Test that dates appear in contact details"""
        agent_handler("add Angelina Jolie to contacts")
        agent_handler("Angelina's birthday is on 4 june")
        
        result = agent_handler("show me the details of Angelina Jolie")
        
        assert result["status"] == "success"
        assert result["action_taken"] == "get_contact_details"
        assert "Angelina Jolie" in result["message"]
        
    def test_date_format_parsing(self, agent_handler):
        """Test various date format parsing"""
        agent_handler("add Test Person to contacts")
        
        # Test different date formats
        formats = [
            "Test Person's birthday is on 12 nov",
            "add anniversary for Test Person on 25 december",
            "Test Person's graduation is on 15 aug"
        ]
        
        for date_input in formats:
            result = agent_handler(date_input)
            assert result["status"] == "success"
            assert result["action_taken"] == "add_date"
            
    def test_upcoming_dates_query_variations(self, agent_handler):
        """Test different ways to query upcoming dates"""
        agent_handler("add Future Person to contacts")
        agent_handler("Future Person's birthday is on 20 august")
        
        queries = [
            "show upcoming important dates",
            "any birthdays coming up?",
            "what important dates are coming"
        ]
        
        for query in queries:
            result = agent_handler(query)
            assert result["status"] == "success"
            assert result["action_taken"] == "show_upcoming_dates"
            
    def test_date_requires_existing_contact(self, agent_handler):
        """Test that adding dates requires an existing contact"""
        result = agent_handler("NonExistent Person's birthday is on 1 january")
        
        assert result["status"] == "error"
        assert "not found" in result["message"] or "add the contact first" in result["message"]
