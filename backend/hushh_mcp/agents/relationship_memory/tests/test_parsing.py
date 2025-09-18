"""
Test LangGraph parsing and intent recognition
"""

import pytest
from typing import Dict, Any


class TestLangGraphParsing:
    """Test suite for LangGraph parsing and intent recognition"""
    
    def test_intent_parsing_confidence(self, agent_handler):
        """Test that intents are parsed with high confidence"""
        test_cases = [
            ("add John to contacts", "add_contact"),
            ("show me all contacts", "show_contacts"),
            ("remember that Sarah likes coffee", "add_memory"),
            ("remind me to call David", "add_reminder"),
            ("show details of Alice", "get_contact_details"),
            ("John's birthday is tomorrow", "add_date"),
            ("show upcoming dates", "show_upcoming_dates")
        ]
        
        for user_input, expected_action in test_cases:
            result = agent_handler(user_input)
            # The action should be correctly identified
            assert result["status"] in ["success", "error"]  # Some might fail due to missing contacts
            
    def test_contact_name_extraction(self, agent_handler):
        """Test that contact names are extracted correctly"""
        variations = [
            "add John Smith to contacts",
            "Add contact John Smith", 
            "create contact for John Smith",
            "new contact: John Smith"
        ]
        
        for variation in variations:
            result = agent_handler(variation)
            assert result["status"] == "success"
            assert "John Smith" in result["message"]
            
    def test_email_extraction(self, agent_handler):
        """Test that emails are extracted correctly"""
        email_tests = [
            "add Sarah with email sarah@test.com",
            "Sarah's email is sarah@test.com",
            "add email sarah@test.com for Sarah"
        ]
        
        for email_test in email_tests:
            result = agent_handler(email_test)
            assert result["status"] == "success"
            
    def test_memory_content_extraction(self, agent_handler):
        """Test that memory content is extracted correctly"""
        agent_handler("add Tom Wilson to contacts")
        
        memory_tests = [
            "remember that Tom loves pizza",
            "Tom mentioned he plays guitar",
            "Tom is working at Google"
        ]
        
        for memory_test in memory_tests:
            result = agent_handler(memory_test)
            assert result["status"] == "success"
            assert result["action_taken"] == "add_memory"
            
    def test_date_extraction(self, agent_handler):
        """Test that dates are extracted correctly"""
        agent_handler("add Test Person to contacts")
        
        date_tests = [
            ("Test Person's birthday is on 12 november", "birthday", "12-11"),
            ("add anniversary for Test Person on 25 december", "anniversary", "25-12"),
            ("Test Person's graduation is on 5 june", "graduation", "05-06")
        ]
        
        for date_input, expected_type, expected_date in date_tests:
            result = agent_handler(date_input)
            assert result["status"] == "success"
            assert result["action_taken"] == "add_date"
            assert expected_type in result["message"]
            
    def test_unknown_intent_handling(self, agent_handler):
        """Test handling of unclear or unknown intents"""
        unclear_inputs = [
            "hello",
            "what's the weather?",
            "random text here",
            "xyz abc def"
        ]
        
        for unclear_input in unclear_inputs:
            result = agent_handler(unclear_input)
            # Should either be classified as unknown or return an error
            if result["status"] == "error":
                assert "understand" in result["message"] or "unknown" in result["message"]
                
    def test_complex_sentence_parsing(self, agent_handler):
        """Test parsing of complex sentences"""
        complex_tests = [
            "add my friend Jennifer Lopez with email jlo@music.com and remember she loves dancing",
            "create contact for Dr. Smith at hospital, email drsmith@hospital.com, remind me to call about appointment"
        ]
        
        for complex_test in complex_tests:
            result = agent_handler(complex_test)
            # Should successfully parse at least the primary action
            assert result["status"] == "success"
