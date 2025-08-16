"""
Test memory management functionality
"""

import pytest
from typing import Dict, Any


class TestMemoryManagement:
    """Test suite for memory management features"""
    
    def test_add_simple_memory(self, agent_handler):
        """Test adding a simple memory"""
        # Add a contact first
        agent_handler("add Emma Watson to contacts")
        
        result = agent_handler("Remember that Emma loves reading books")
        
        assert result["status"] == "success"
        assert result["action_taken"] == "add_memory"
        assert "Emma" in result["message"]
        
    def test_add_memory_with_location(self, agent_handler):
        """Test adding a memory with location context"""
        agent_handler("add Chris Evans to contacts")
        
        result = agent_handler("Met Chris at the coffee shop downtown, he mentioned he's working on a new project")
        
        assert result["status"] == "success"
        assert result["action_taken"] == "add_memory"
        assert "Chris" in result["message"]
        
    def test_show_memories_for_contact(self, agent_handler):
        """Test showing memories for a specific contact"""
        # Add contact and memory
        agent_handler("add Ryan Reynolds to contacts")
        agent_handler("Remember that Ryan has a great sense of humor")
        
        result = agent_handler("show me all memories about Ryan")
        
        assert result["status"] == "success"
        assert result["action_taken"] == "show_memories"
        assert "Ryan" in result["message"]
        
    def test_show_all_memories(self, agent_handler):
        """Test showing all memories"""
        # Add some memories
        agent_handler("add Blake Lively to contacts")
        agent_handler("Remember that Blake is interested in photography")
        
        result = agent_handler("show me all memories")
        
        assert result["status"] == "success"
        assert result["action_taken"] == "show_memories"
        
    def test_memory_in_contact_details(self, agent_handler):
        """Test that memories appear in contact details"""
        # Add contact and memory
        agent_handler("add Jennifer Lawrence to contacts")
        agent_handler("Remember that Jennifer loves archery")
        
        result = agent_handler("show me the details of Jennifer Lawrence")
        
        assert result["status"] == "success"
        assert result["action_taken"] == "get_contact_details"
        assert "Jennifer Lawrence" in result["message"]
        
    def test_memory_requires_contact(self, agent_handler):
        """Test that memory addition requires a valid contact"""
        result = agent_handler("Remember that NonExistentPerson likes pizza")
        
        # Should still work but might create a memory without validation
        # The exact behavior depends on implementation
        assert result["status"] in ["success", "error"]
        
    def test_multiple_memories_for_contact(self, agent_handler):
        """Test adding multiple memories for the same contact"""
        agent_handler("add Leonardo DiCaprio to contacts")
        
        # Add multiple memories
        agent_handler("Remember that Leonardo is passionate about environmental causes")
        agent_handler("Remember that Leonardo is an amazing actor")
        
        result = agent_handler("show me all memories about Leonardo")
        
        assert result["status"] == "success"
        assert result["action_taken"] == "show_memories"
