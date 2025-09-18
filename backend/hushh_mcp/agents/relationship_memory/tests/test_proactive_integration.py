"""
Integration test for the complete Proactive Relationship Manager Agent.
Tests end-to-end functionality including proactive checks, batch operations, and advice generation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from hushh_mcp.agents.relationship_memory.index import (
    RelationshipMemoryAgent, run, run_proactive_check
)
from hushh_mcp.constants import ConsentScope


class TestProactiveIntegration:
    """Integration tests for the complete proactive system"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_tokens = {
            ConsentScope.VAULT_READ_CONTACTS.value: "test_read_token",
            ConsentScope.VAULT_WRITE_CONTACTS.value: "test_write_token"
        }
        self.test_user_id = "test_user_123"
        self.test_vault_key = "test_vault_key"
    
    @patch('hushh_mcp.agents.relationship_memory.index.validate_token')
    @patch('hushh_mcp.agents.relationship_memory.index.VaultManager')
    @patch('hushh_mcp.agents.relationship_memory.index.ChatGoogleGenerativeAI')
    def test_proactive_startup_flow(self, mock_llm_class, mock_vault_manager_class, mock_validate_token):
        """Test complete proactive startup flow"""
        # Mock token validation
        mock_validate_token.return_value = (True, "Valid", Mock(user_id=self.test_user_id))
        
        # Mock LLM
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "🌅 Good morning! Jane's birthday is in 3 days! 🎂 Also, it's been 45 days since you talked to John. Want some suggestions?"
        mock_llm.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm
        
        # Mock vault manager with contacts
        mock_vault_manager = Mock()
        mock_vault_manager_class.return_value = mock_vault_manager
        
        # Create test contacts with upcoming events and reconnection needs
        current_date = datetime.now()
        birthday_date = (current_date + timedelta(days=3)).strftime('%d-%m')
        old_contact_date = (current_date - timedelta(days=45)).strftime('%Y-%m-%d')
        
        mock_contacts = [
            {
                'name': 'Jane Doe',
                'email': 'jane@example.com',
                'dates': {'birthday': birthday_date},
                'priority': 'high',
                'last_talked_date': (current_date - timedelta(days=2)).strftime('%Y-%m-%d')
            },
            {
                'name': 'John Smith',
                'email': 'john@example.com',
                'priority': 'medium',
                'last_talked_date': old_contact_date
            }
        ]
        
        mock_vault_manager.get_all_contacts.return_value = mock_contacts
        
        # Test proactive startup check
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            result = run_proactive_check(self.test_user_id, self.test_tokens, self.test_vault_key)
        
        # Verify proactive response
        assert result["status"] == "success"
        assert "Jane's birthday" in result["message"] or "proactive" in result.get("action_taken", "")
        assert mock_llm.invoke.called
    
    @patch('hushh_mcp.agents.relationship_memory.index.validate_token')
    @patch('hushh_mcp.agents.relationship_memory.index.VaultManager')
    @patch('hushh_mcp.agents.relationship_memory.index.ChatGoogleGenerativeAI')
    def test_batch_contact_import_flow(self, mock_llm_class, mock_vault_manager_class, mock_validate_token):
        """Test complete batch contact import flow"""
        # Mock token validation
        mock_validate_token.return_value = (True, "Valid", Mock(user_id=self.test_user_id))
        
        # Mock LLM for intent parsing
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        
        # Mock structured output for batch contact parsing
        from hushh_mcp.agents.relationship_memory.index import UserIntent, ContactInfo
        
        batch_intent = UserIntent(
            action="add_contact",
            confidence=0.95,
            contact_info=[
                ContactInfo(name="Alice Johnson", email="alice@example.com", priority="high"),
                ContactInfo(name="Bob Wilson", phone="+1234567890", priority="medium"),
                ContactInfo(name="Carol Davis", company="Tech Corp", priority="low")
            ]
        )
        
        mock_structured_llm = Mock()
        mock_structured_llm.invoke.return_value = batch_intent
        mock_llm.with_structured_output.return_value = mock_structured_llm
        
        # Mock vault manager
        mock_vault_manager = Mock()
        mock_vault_manager_class.return_value = mock_vault_manager
        mock_vault_manager.get_all_contacts.return_value = []  # No existing contacts
        mock_vault_manager.store_contact.side_effect = ["contact_1", "contact_2", "contact_3"]
        
        # Test batch contact import
        batch_input = "add these contacts: Alice Johnson with email alice@example.com, Bob Wilson at +1234567890, and Carol Davis from Tech Corp"
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            result = run(self.test_user_id, self.test_tokens, batch_input, self.test_vault_key)
        
        # Verify batch processing
        assert result["status"] == "success"
        assert "3 contacts" in result["message"] or "Alice" in result["message"]
        assert len(result.get("data", [])) == 3
        assert mock_vault_manager.store_contact.call_count == 3
    
    @patch('hushh_mcp.agents.relationship_memory.index.validate_token')
    @patch('hushh_mcp.agents.relationship_memory.index.VaultManager')
    @patch('hushh_mcp.agents.relationship_memory.index.ChatGoogleGenerativeAI')
    def test_advice_generation_flow(self, mock_llm_class, mock_vault_manager_class, mock_validate_token):
        """Test complete advice generation flow"""
        # Mock token validation
        mock_validate_token.return_value = (True, "Valid", Mock(user_id=self.test_user_id))
        
        # Mock LLM
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        
        # Mock intent parsing for advice request
        from hushh_mcp.agents.relationship_memory.index import UserIntent
        
        advice_intent = UserIntent(
            action="get_advice",
            confidence=0.9,
            contact_name="Sarah Johnson"
        )
        
        mock_structured_llm = Mock()
        mock_structured_llm.invoke.return_value = advice_intent
        mock_llm.with_structured_output.return_value = mock_structured_llm
        
        # Mock advice response
        advice_response = Mock()
        advice_response.content = "Based on your memories, Sarah loves hiking and outdoor activities. For her birthday, consider getting her a high-quality water bottle, hiking socks, or a trail map of local hiking spots!"
        
        # Set up LLM to return advice response for advice generation
        mock_llm.invoke.return_value = advice_response
        
        # Mock vault manager with contact and memories
        mock_vault_manager = Mock()
        mock_vault_manager_class.return_value = mock_vault_manager
        
        mock_contact = {
            'name': 'Sarah Johnson',
            'email': 'sarah@example.com',
            'notes': 'Loves outdoor activities',
            'dates': {'birthday': '15-03'},
            'priority': 'high'
        }
        
        mock_memories = [
            {
                'contact_name': 'Sarah Johnson',
                'summary': 'Sarah mentioned wanting new hiking gear',
                'location': 'Coffee shop',
                'tags': ['outdoor', 'hiking', 'gear']
            },
            {
                'contact_name': 'Sarah Johnson',
                'summary': 'Talked about favorite hiking trails',
                'tags': ['hiking', 'trails']
            }
        ]
        
        mock_vault_manager.get_all_contacts.return_value = [mock_contact]
        mock_vault_manager.get_all_memories.return_value = mock_memories
        
        # Test advice generation
        advice_input = "what should I get Sarah Johnson for her birthday?"
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            # Create agent and mock find_contact_by_name
            agent = RelationshipMemoryAgent()
            agent._find_contact_by_name = Mock(return_value=mock_contact)
            
            result = agent.handle(self.test_user_id, self.test_tokens, advice_input, self.test_vault_key)
        
        # Verify advice generation
        assert result["status"] == "success"
        assert "hiking" in result["message"].lower() or "outdoor" in result["message"].lower()
        assert result.get("action_taken") == "advice_generated"
    
    @patch('hushh_mcp.agents.relationship_memory.index.validate_token')
    @patch('hushh_mcp.agents.relationship_memory.index.VaultManager')
    @patch('hushh_mcp.agents.relationship_memory.index.ChatGoogleGenerativeAI')
    def test_memory_with_interaction_tracking(self, mock_llm_class, mock_vault_manager_class, mock_validate_token):
        """Test memory addition with automatic interaction tracking"""
        # Mock token validation
        mock_validate_token.return_value = (True, "Valid", Mock(user_id=self.test_user_id))
        
        # Mock LLM
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        
        # Mock intent parsing for memory addition
        from hushh_mcp.agents.relationship_memory.index import UserIntent, MemoryInfo
        
        memory_intent = UserIntent(
            action="add_memory",
            confidence=0.9,
            memory_info=MemoryInfo(
                contact_name="John Doe",
                summary="John got promoted to Senior Developer at his company"
            )
        )
        
        mock_structured_llm = Mock()
        mock_structured_llm.invoke.return_value = memory_intent
        mock_llm.with_structured_output.return_value = mock_structured_llm
        
        # Mock vault manager
        mock_vault_manager = Mock()
        mock_vault_manager_class.return_value = mock_vault_manager
        mock_vault_manager.store_memory.return_value = "memory_123"
        
        # Mock contact for interaction tracking
        mock_contact = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'last_talked_date': '2024-01-01'
        }
        
        # Test memory addition
        memory_input = "remember that John Doe got promoted to Senior Developer"
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            # Create agent and mock methods
            agent = RelationshipMemoryAgent()
            agent._find_contact_by_name = Mock(return_value=mock_contact)
            agent._update_existing_contact = Mock(return_value=mock_contact)
            
            result = agent.handle(self.test_user_id, self.test_tokens, memory_input, self.test_vault_key)
        
        # Verify memory storage and interaction tracking
        assert result["status"] == "success"
        assert "Successfully recorded memory about John Doe" in result["message"]
        assert result.get("action_taken") == "add_memory"
        assert mock_vault_manager.store_memory.called
        
        # Verify interaction timestamp was updated
        today = datetime.now().strftime('%Y-%m-%d')
        assert mock_contact['last_talked_date'] == today
    
    @patch('hushh_mcp.agents.relationship_memory.index.validate_token')
    def test_error_handling_invalid_tokens(self, mock_validate_token):
        """Test error handling with invalid tokens"""
        # Mock invalid token validation
        mock_validate_token.return_value = (False, "Invalid token", None)
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            result = run(self.test_user_id, {"invalid": "token"}, "add contact John", self.test_vault_key)
        
        # Verify error handling
        assert result["status"] == "error"
        assert "No valid tokens found" in result["message"]
    
    @patch('hushh_mcp.agents.relationship_memory.index.validate_token')
    @patch('hushh_mcp.agents.relationship_memory.index.VaultManager')
    def test_error_handling_vault_unavailable(self, mock_vault_manager_class, mock_validate_token):
        """Test error handling when VaultManager is unavailable"""
        # Mock token validation
        mock_validate_token.return_value = (True, "Valid", Mock(user_id=self.test_user_id))
        
        # Mock VaultManager to be None (unavailable)
        with patch('hushh_mcp.agents.relationship_memory.index.VaultManager', None):
            with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
                result = run(self.test_user_id, self.test_tokens, "add contact John", self.test_vault_key)
        
        # Verify error handling
        assert result["status"] == "error"
        assert "VaultManager not available" in result["message"]


class TestEndToEndScenarios:
    """End-to-end scenario tests"""
    
    @patch('hushh_mcp.agents.relationship_memory.index.validate_token')
    @patch('hushh_mcp.agents.relationship_memory.index.VaultManager')
    @patch('hushh_mcp.agents.relationship_memory.index.ChatGoogleGenerativeAI')
    def test_complete_relationship_management_scenario(self, mock_llm_class, mock_vault_manager_class, mock_validate_token):
        """Test a complete relationship management scenario"""
        # Mock token validation
        mock_validate_token.return_value = (True, "Valid", Mock(user_id="user123"))
        
        # Mock LLM
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        
        # Mock vault manager
        mock_vault_manager = Mock()
        mock_vault_manager_class.return_value = mock_vault_manager
        mock_vault_manager.get_all_contacts.return_value = []
        mock_vault_manager.store_contact.return_value = "contact_123"
        mock_vault_manager.store_memory.return_value = "memory_123"
        
        tokens = {
            ConsentScope.VAULT_READ_CONTACTS.value: "read_token",
            ConsentScope.VAULT_WRITE_CONTACTS.value: "write_token"
        }
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            # Step 1: Add a contact
            from hushh_mcp.agents.relationship_memory.index import UserIntent, ContactInfo
            
            add_intent = UserIntent(
                action="add_contact",
                confidence=0.9,
                contact_info=[ContactInfo(name="Alice Smith", email="alice@example.com", priority="high")]
            )
            
            mock_structured_llm = Mock()
            mock_structured_llm.invoke.return_value = add_intent
            mock_llm.with_structured_output.return_value = mock_structured_llm
            
            result1 = run("user123", tokens, "add contact Alice Smith with email alice@example.com", "vault_key")
            
            assert result1["status"] == "success"
            assert "Alice Smith" in result1["message"]
            
            # Step 2: Add a memory about the contact
            from hushh_mcp.agents.relationship_memory.index import MemoryInfo
            
            memory_intent = UserIntent(
                action="add_memory",
                confidence=0.9,
                memory_info=MemoryInfo(contact_name="Alice Smith", summary="Alice loves photography")
            )
            
            mock_structured_llm.invoke.return_value = memory_intent
            
            # Mock contact for memory addition
            mock_contact = {
                'name': 'Alice Smith',
                'email': 'alice@example.com',
                'priority': 'high',
                'last_talked_date': '2024-01-01'
            }
            
            # Create agent and mock methods
            agent = RelationshipMemoryAgent()
            agent._find_contact_by_name = Mock(return_value=mock_contact)
            agent._update_existing_contact = Mock(return_value=mock_contact)
            
            result2 = agent.handle("user123", tokens, "remember that Alice loves photography", "vault_key")
            
            assert result2["status"] == "success"
            assert "Alice Smith" in result2["message"]
            
            # Step 3: Get advice about the contact
            advice_intent = UserIntent(
                action="get_advice",
                confidence=0.9,
                contact_name="Alice Smith"
            )
            
            mock_structured_llm.invoke.return_value = advice_intent
            
            # Mock advice response
            advice_response = Mock()
            advice_response.content = "Since Alice loves photography, consider getting her a camera accessory or photography book!"
            mock_llm.invoke.return_value = advice_response
            
            # Mock memories for advice
            mock_memories = [
                {
                    'contact_name': 'Alice Smith',
                    'summary': 'Alice loves photography',
                    'tags': ['photography', 'hobby']
                }
            ]
            mock_vault_manager.get_all_memories.return_value = mock_memories
            
            result3 = agent.handle("user123", tokens, "what should I get Alice for her birthday?", "vault_key")
            
            assert result3["status"] == "success"
            assert "photography" in result3["message"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])