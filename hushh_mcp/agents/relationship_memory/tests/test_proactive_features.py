"""
Comprehensive test suite for proactive relationship manager features.
Tests proactive triggers, batch operations, advice generation, and workflow integration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from hushh_mcp.agents.relationship_memory.index import (
    RelationshipMemoryAgent, RelationshipMemoryState, ContactInfo, UserIntent
)


class TestProactiveTriggerDetection:
    """Test proactive trigger detection system"""
    
    def setup_method(self):
        """Setup test environment"""
        self.agent = RelationshipMemoryAgent()
        
    @patch('hushh_mcp.agents.relationship_memory.index.VaultManager')
    def test_check_proactive_triggers_upcoming_events(self, mock_vault_manager_class):
        """Test detection of upcoming birthdays and anniversaries"""
        # Mock vault manager
        mock_vault_manager = Mock()
        mock_vault_manager_class.return_value = mock_vault_manager
        
        # Mock contacts with upcoming events
        current_date = datetime.now()
        future_date = current_date + timedelta(days=5)
        
        mock_contacts = [
            {
                'name': 'Jane Doe',
                'dates': {
                    'birthday': '15-03',  # Assuming this is 5 days away
                    'anniversary': '20-12'  # Far in future
                },
                'priority': 'high',
                'last_talked_date': '2024-01-01'
            },
            {
                'name': 'John Smith',
                'dates': {
                    'birthday': '10-01'  # Far in past/future
                },
                'priority': 'medium',
                'last_talked_date': '2024-01-15'
            }
        ]
        
        mock_vault_manager.get_all_contacts.return_value = mock_contacts
        
        # Create test state
        state = RelationshipMemoryState(
            user_input="",
            user_id="test_user",
            vault_key="test_key",
            parsed_intent=None,
            result_data=[],
            response_message="",
            error=None,
            action_taken="",
            is_startup=True,
            proactive_triggers=[],
            conversation_history=[]
        )
        
        # Test proactive trigger detection
        result_state = self.agent._check_for_proactive_triggers(state)
        
        # Verify triggers were detected
        assert "proactive_triggers" in result_state
        triggers = result_state["proactive_triggers"]
        
        # Should have some triggers (exact count depends on current date)
        assert isinstance(triggers, list)
        
        # Check trigger structure
        for trigger in triggers:
            assert "type" in trigger
            assert trigger["type"] in ["upcoming_event", "reconnection"]
            assert "contact_name" in trigger
    
    @patch('hushh_mcp.agents.relationship_memory.index.VaultManager')
    def test_check_proactive_triggers_reconnection_suggestions(self, mock_vault_manager_class):
        """Test detection of reconnection opportunities"""
        # Mock vault manager
        mock_vault_manager = Mock()
        mock_vault_manager_class.return_value = mock_vault_manager
        
        # Mock contacts needing reconnection
        old_date = (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d')
        very_old_date = (datetime.now() - timedelta(days=100)).strftime('%Y-%m-%d')
        
        mock_contacts = [
            {
                'name': 'High Priority Contact',
                'priority': 'high',
                'last_talked_date': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
            },
            {
                'name': 'Medium Priority Contact',
                'priority': 'medium',
                'last_talked_date': old_date
            },
            {
                'name': 'Low Priority Contact',
                'priority': 'low',
                'last_talked_date': very_old_date
            }
        ]
        
        mock_vault_manager.get_all_contacts.return_value = mock_contacts
        
        # Create test state
        state = RelationshipMemoryState(
            user_input="",
            user_id="test_user",
            vault_key="test_key",
            parsed_intent=None,
            result_data=[],
            response_message="",
            error=None,
            action_taken="",
            is_startup=True,
            proactive_triggers=[],
            conversation_history=[]
        )
        
        # Test proactive trigger detection
        result_state = self.agent._check_for_proactive_triggers(state)
        
        # Verify reconnection triggers
        triggers = result_state["proactive_triggers"]
        reconnection_triggers = [t for t in triggers if t["type"] == "reconnection"]
        
        # Should have reconnection suggestions
        assert len(reconnection_triggers) >= 2  # Medium and Low priority contacts
        
        # Check trigger details
        for trigger in reconnection_triggers:
            assert "days_since_contact" in trigger
            assert "priority" in trigger
            assert trigger["days_since_contact"] > 0
    
    def test_calculate_days_until_event(self):
        """Test date calculation for upcoming events"""
        current_date = datetime(2024, 3, 1)  # March 1st
        
        # Test birthday in same month
        days_until = self.agent._calculate_days_until_event("15-03", current_date)
        assert days_until == 14  # March 15th is 14 days away
        
        # Test birthday in next month
        days_until = self.agent._calculate_days_until_event("10-04", current_date)
        assert days_until == 40  # April 10th
        
        # Test invalid date format
        days_until = self.agent._calculate_days_until_event("invalid", current_date)
        assert days_until == 999  # Error case
    
    def test_calculate_days_since_contact(self):
        """Test calculation of days since last contact"""
        # Test with valid last_talked_date
        contact_recent = {
            'last_talked_date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        }
        days_since = self.agent._calculate_days_since_contact(contact_recent)
        assert days_since == 5
        
        # Test with no last_talked_date but created_at
        contact_old = {
            'created_at': (datetime.now() - timedelta(days=20)).isoformat()
        }
        days_since = self.agent._calculate_days_since_contact(contact_old)
        assert days_since == 20
        
        # Test with no date information
        contact_no_date = {'name': 'Test Contact'}
        days_since = self.agent._calculate_days_since_contact(contact_no_date)
        assert days_since == 30  # Default fallback


class TestProactiveResponseGeneration:
    """Test proactive response generation"""
    
    def setup_method(self):
        """Setup test environment"""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            self.agent = RelationshipMemoryAgent()
    
    @patch('hushh_mcp.agents.relationship_memory.index.ChatGoogleGenerativeAI')
    def test_generate_proactive_response_with_triggers(self, mock_llm_class):
        """Test proactive response generation with triggers"""
        # Mock LLM response
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Hey! Jane's birthday is in 5 days! 🎂 Also, it's been a while since you talked to John. Want some suggestions?"
        mock_llm.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm
        
        # Create state with triggers
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
                'days_since_contact': 30,
                'priority': 'medium'
            }
        ]
        
        state = RelationshipMemoryState(
            user_input="",
            user_id="test_user",
            vault_key="test_key",
            parsed_intent=None,
            result_data=[],
            response_message="",
            error=None,
            action_taken="",
            is_startup=True,
            proactive_triggers=triggers,
            conversation_history=[]
        )
        
        # Test response generation
        result_state = self.agent._generate_proactive_response(state)
        
        # Verify response was generated
        assert result_state["response_message"] == mock_response.content
        assert result_state["action_taken"] == "proactive_notification"
        assert mock_llm.invoke.called
    
    def test_generate_proactive_response_no_triggers(self):
        """Test proactive response with no triggers"""
        state = RelationshipMemoryState(
            user_input="",
            user_id="test_user",
            vault_key="test_key",
            parsed_intent=None,
            result_data=[],
            response_message="",
            error=None,
            action_taken="",
            is_startup=True,
            proactive_triggers=[],
            conversation_history=[]
        )
        
        # Test response generation
        result_state = self.agent._generate_proactive_response(state)
        
        # Verify no response for empty triggers
        assert result_state["response_message"] == ""
        assert result_state["action_taken"] == "no_proactive_triggers"
    
    def test_format_triggers_for_llm(self):
        """Test trigger formatting for LLM context"""
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
                'days_since_contact': 30,
                'priority': 'medium'
            }
        ]
        
        formatted = self.agent._format_triggers_for_llm(triggers)
        
        # Verify formatting
        assert "UPCOMING EVENTS:" in formatted
        assert "Jane Doe's birthday is in 5 days" in formatted
        assert "RECONNECTION SUGGESTIONS:" in formatted
        assert "Haven't talked to John Smith in 30 days" in formatted
        assert "(medium priority)" in formatted


class TestBatchContactProcessing:
    """Test batch contact processing capabilities"""
    
    def setup_method(self):
        """Setup test environment"""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            self.agent = RelationshipMemoryAgent()
    
    @patch('hushh_mcp.agents.relationship_memory.index.VaultManager')
    def test_batch_contact_processing_success(self, mock_vault_manager_class):
        """Test successful batch contact processing"""
        # Mock vault manager
        mock_vault_manager = Mock()
        mock_vault_manager_class.return_value = mock_vault_manager
        mock_vault_manager.get_all_contacts.return_value = []  # No existing contacts
        mock_vault_manager.store_contact.side_effect = ["contact_1", "contact_2"]
        
        # Create batch contact intent
        contacts = [
            ContactInfo(name="Alice Johnson", email="alice@example.com", priority="high"),
            ContactInfo(name="Bob Wilson", phone="+1234567890", priority="medium")
        ]
        
        intent = UserIntent(
            action="add_contact",
            confidence=0.9,
            contact_info=contacts
        )
        
        state = RelationshipMemoryState(
            user_input="add contacts Alice and Bob",
            user_id="test_user",
            vault_key="test_key",
            parsed_intent=intent,
            result_data=[],
            response_message="",
            error=None,
            action_taken="",
            is_startup=False,
            proactive_triggers=[],
            conversation_history=[]
        )
        
        # Test batch processing
        result_state = self.agent._add_contact_tool(state)
        
        # Verify successful processing
        assert result_state["action_taken"] == "batch_add_success"
        assert "Successfully added 2 contacts" in result_state["response_message"]
        assert len(result_state["result_data"]) == 2
        assert mock_vault_manager.store_contact.call_count == 2
    
    @patch('hushh_mcp.agents.relationship_memory.index.VaultManager')
    def test_batch_contact_processing_partial_failure(self, mock_vault_manager_class):
        """Test batch processing with some failures"""
        # Mock vault manager
        mock_vault_manager = Mock()
        mock_vault_manager_class.return_value = mock_vault_manager
        mock_vault_manager.get_all_contacts.return_value = []
        
        # First contact succeeds, second fails
        mock_vault_manager.store_contact.side_effect = ["contact_1", Exception("Storage failed")]
        
        # Create batch contact intent with one invalid contact
        contacts = [
            ContactInfo(name="Alice Johnson", email="alice@example.com"),
            ContactInfo(name="", email="invalid@example.com")  # Invalid: no name
        ]
        
        intent = UserIntent(
            action="add_contact",
            confidence=0.9,
            contact_info=contacts
        )
        
        state = RelationshipMemoryState(
            user_input="add contacts Alice and invalid",
            user_id="test_user",
            vault_key="test_key",
            parsed_intent=intent,
            result_data=[],
            response_message="",
            error=None,
            action_taken="",
            is_startup=False,
            proactive_triggers=[],
            conversation_history=[]
        )
        
        # Test batch processing
        result_state = self.agent._add_contact_tool(state)
        
        # Verify partial success handling
        assert "Successfully added" in result_state["response_message"]
        assert "Failed to process" in result_state["response_message"]
        assert result_state["action_taken"] in ["batch_add_partial", "batch_add_mixed"]


class TestConversationalAdvice:
    """Test conversational advice generation"""
    
    def setup_method(self):
        """Setup test environment"""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            self.agent = RelationshipMemoryAgent()
    
    @patch('hushh_mcp.agents.relationship_memory.index.VaultManager')
    @patch('hushh_mcp.agents.relationship_memory.index.ChatGoogleGenerativeAI')
    def test_conversational_advice_with_memories(self, mock_llm_class, mock_vault_manager_class):
        """Test advice generation with contact memories"""
        # Mock LLM
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Based on your memories, Sarah loves hiking. Consider getting her a high-quality water bottle or hiking gear!"
        mock_llm.invoke.return_value = mock_response
        mock_llm_class.return_value = mock_llm
        
        # Mock vault manager
        mock_vault_manager = Mock()
        mock_vault_manager_class.return_value = mock_vault_manager
        
        # Mock contact and memories
        mock_contact = {
            'name': 'Sarah Johnson',
            'email': 'sarah@example.com',
            'notes': 'Outdoor enthusiast',
            'dates': {'birthday': '15-03'}
        }
        
        mock_memories = [
            {
                'contact_name': 'Sarah Johnson',
                'summary': 'Sarah loves hiking and mentioned wanting new gear',
                'location': 'Coffee shop',
                'tags': ['outdoor', 'hiking']
            }
        ]
        
        mock_vault_manager.get_all_contacts.return_value = [mock_contact]
        mock_vault_manager.get_all_memories.return_value = mock_memories
        
        # Mock find_contact_by_name
        self.agent._find_contact_by_name = Mock(return_value=mock_contact)
        
        # Create advice intent
        intent = UserIntent(
            action="get_advice",
            confidence=0.9,
            contact_name="Sarah Johnson"
        )
        
        state = RelationshipMemoryState(
            user_input="what should I get Sarah for her birthday?",
            user_id="test_user",
            vault_key="test_key",
            parsed_intent=intent,
            result_data=[],
            response_message="",
            error=None,
            action_taken="",
            is_startup=False,
            proactive_triggers=[],
            conversation_history=[]
        )
        
        # Test advice generation
        result_state = self.agent._conversational_advice_tool(state)
        
        # Verify advice was generated
        assert result_state["response_message"] == mock_response.content
        assert result_state["action_taken"] == "advice_generated"
        assert mock_llm.invoke.called
    
    @patch('hushh_mcp.agents.relationship_memory.index.VaultManager')
    def test_conversational_advice_no_contact(self, mock_vault_manager_class):
        """Test advice generation for non-existent contact"""
        # Mock vault manager
        mock_vault_manager = Mock()
        mock_vault_manager_class.return_value = mock_vault_manager
        
        # Mock find_contact_by_name to return None
        self.agent._find_contact_by_name = Mock(return_value=None)
        
        # Create advice intent
        intent = UserIntent(
            action="get_advice",
            confidence=0.9,
            contact_name="Unknown Person"
        )
        
        state = RelationshipMemoryState(
            user_input="what should I get Unknown Person?",
            user_id="test_user",
            vault_key="test_key",
            parsed_intent=intent,
            result_data=[],
            response_message="",
            error=None,
            action_taken="",
            is_startup=False,
            proactive_triggers=[],
            conversation_history=[]
        )
        
        # Test advice generation
        result_state = self.agent._conversational_advice_tool(state)
        
        # Verify appropriate response for missing contact
        assert "don't have information about Unknown Person" in result_state["response_message"]
        assert result_state["action_taken"] == "advice_no_contact"


class TestWorkflowIntegration:
    """Test enhanced LangGraph workflow integration"""
    
    def setup_method(self):
        """Setup test environment"""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            self.agent = RelationshipMemoryAgent()
    
    def test_route_from_proactive_check_with_triggers(self):
        """Test routing from proactive check when triggers exist"""
        state = RelationshipMemoryState(
            user_input="",
            user_id="test_user",
            vault_key="test_key",
            parsed_intent=None,
            result_data=[],
            response_message="",
            error=None,
            action_taken="",
            is_startup=True,
            proactive_triggers=[{'type': 'upcoming_event'}],
            conversation_history=[]
        )
        
        route = self.agent._route_from_proactive_check(state)
        assert route == "proactive_response"
    
    def test_route_from_proactive_check_no_triggers(self):
        """Test routing from proactive check when no triggers exist"""
        state = RelationshipMemoryState(
            user_input="add contact John",
            user_id="test_user",
            vault_key="test_key",
            parsed_intent=None,
            result_data=[],
            response_message="",
            error=None,
            action_taken="",
            is_startup=False,
            proactive_triggers=[],
            conversation_history=[]
        )
        
        route = self.agent._route_from_proactive_check(state)
        assert route == "parse_intent"
    
    def test_enhanced_route_to_tool(self):
        """Test enhanced routing to tools including new actions"""
        # Test get_advice routing
        intent = UserIntent(action="get_advice", confidence=0.9, contact_name="John")
        state = RelationshipMemoryState(
            user_input="advice about John",
            user_id="test_user",
            vault_key="test_key",
            parsed_intent=intent,
            result_data=[],
            response_message="",
            error=None,
            action_taken="",
            is_startup=False,
            proactive_triggers=[],
            conversation_history=[]
        )
        
        route = self.agent._route_to_tool(state)
        assert route == "get_advice"
        
        # Test invalid action routing
        intent_invalid = UserIntent(action="unknown", confidence=0.9)
        state["parsed_intent"] = intent_invalid
        
        route = self.agent._route_to_tool(state)
        assert route == "error"


class TestInteractionHistoryTracking:
    """Test interaction history tracking functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            self.agent = RelationshipMemoryAgent()
    
    @patch('hushh_mcp.agents.relationship_memory.index.VaultManager')
    def test_update_interaction_tool(self, mock_vault_manager_class):
        """Test updating interaction timestamps"""
        # Mock vault manager
        mock_vault_manager = Mock()
        mock_vault_manager_class.return_value = mock_vault_manager
        
        # Mock contact
        mock_contact = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'last_talked_date': '2024-01-01'
        }
        
        # Mock find_contact_by_name and update methods
        self.agent._find_contact_by_name = Mock(return_value=mock_contact)
        self.agent._update_existing_contact = Mock(return_value=mock_contact)
        
        # Test interaction update
        result = self.agent._update_interaction_tool(mock_vault_manager, "John Doe")
        
        # Verify update was attempted
        assert result is True
        assert self.agent._find_contact_by_name.called
        assert self.agent._update_existing_contact.called
        
        # Verify date was updated to today
        today = datetime.now().strftime('%Y-%m-%d')
        assert mock_contact['last_talked_date'] == today


if __name__ == "__main__":
    pytest.main([__file__, "-v"])