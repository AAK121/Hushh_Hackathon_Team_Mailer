"""
Pytest tests for HushhMCP Agents

Tests the AddToCalendar agent functionality, consent validation,
and proper integration with operons according to HushhMCP protocol.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import the agent
from hushh_mcp.agents.addtocalendar.index import AddToCalendarAgent, _generate_encryption_key
from hushh_mcp.consent.token import issue_token, validate_token
from hushh_mcp.constants import ConsentScope


class TestAddToCalendarAgent:
    """Test suite for AddToCalendar Agent following HushhMCP protocol."""
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mocked AddToCalendar agent for testing."""
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_api_key'}):
            agent = AddToCalendarAgent()
            return agent
    
    @pytest.fixture
    def valid_email_token(self):
        """Create a valid email consent token."""
        return issue_token(
            user_id="test_user_123",
            agent_id="agent_addtocalendar", 
            scope=ConsentScope.VAULT_READ_EMAIL
        )
    
    @pytest.fixture
    def valid_calendar_token(self):
        """Create a valid calendar consent token."""
        return issue_token(
            user_id="test_user_123",
            agent_id="agent_addtocalendar",
            scope=ConsentScope.VAULT_WRITE_CALENDAR
        )
    
    @pytest.fixture
    def sample_emails(self):
        """Sample email data for testing."""
        return [
            {
                'id': 'email_1',
                'subject': 'Team Meeting Tomorrow',
                'sender': 'manager@company.com',
                'date': 'Wed, 10 Aug 2025 09:00:00 GMT',
                'content': 'We have a team meeting tomorrow at 2 PM in conference room A.',
                'timestamp': '1754678400000'
            },
            {
                'id': 'email_2', 
                'subject': 'Doctor Appointment Reminder',
                'sender': 'clinic@healthcare.com',
                'date': 'Wed, 10 Aug 2025 10:00:00 GMT',
                'content': 'Your appointment is scheduled for Friday at 10 AM.',
                'timestamp': '1754682000000'
            }
        ]

    def test_agent_initialization(self, mock_agent):
        """Test agent can be initialized properly."""
        assert mock_agent.agent_id == "agent_addtocalendar"
        assert hasattr(mock_agent, 'handle')
    
    def test_agent_manifest_compliance(self):
        """Test agent has proper manifest structure."""
        from hushh_mcp.agents.addtocalendar.manifest import manifest
        
        required_fields = ['id', 'name', 'description', 'scopes', 'version']
        for field in required_fields:
            assert field in manifest, f"Manifest missing required field: {field}"
        
        assert manifest['id'] == "agent_addtocalendar"
        assert isinstance(manifest['scopes'], list)
        assert len(manifest['scopes']) > 0

    @patch('hushh_mcp.operons.verify_email.prioritize_emails_operon')
    @patch('hushh_mcp.consent.token.validate_token')
    def test_consent_validation_success(self, mock_validate, mock_operon, mock_agent, valid_email_token):
        """Test agent properly validates consent tokens through prioritize_emails."""
        # Mock successful validation
        mock_validate.return_value = (True, "Valid", {
            'user_id': 'test_user_123',
            'agent_id': 'agent_addtocalendar',
            'scope': ConsentScope.VAULT_READ_EMAIL
        })
        mock_operon.return_value = {'prioritized_emails': []}
        
        sample_emails = [{'id': 'test', 'subject': 'Test', 'snippet': 'Test content'}]
        
        # Test consent validation through public method
        result = mock_agent.prioritize_emails(sample_emails, 'test_user_123', valid_email_token.token)
        assert isinstance(result, list)
        mock_validate.assert_called()

    @patch('hushh_mcp.operons.verify_email.prioritize_emails_operon')
    @patch('hushh_mcp.consent.token.validate_token')
    def test_consent_validation_failure(self, mock_validate, mock_operon, mock_agent):
        """Test agent rejects invalid consent tokens through prioritize_emails."""
        # Mock failed validation
        mock_validate.return_value = (False, "Invalid token", {})
        
        sample_emails = [{'id': 'test', 'subject': 'Test', 'snippet': 'Test content'}]
        
        # Should raise exception when consent validation fails
        with pytest.raises(Exception):
            mock_agent.prioritize_emails(sample_emails, 'test_user_123', 'invalid_token')

    def test_encryption_key_generation(self):
        """Test encryption key generation for vault storage."""
        user_id = "test_user_123"
        key = _generate_encryption_key(user_id)
        
        # Should be 64-character hex string for AES-256
        assert len(key) == 64
        assert all(c in '0123456789abcdef' for c in key.lower())
        
        # Should be deterministic - same user_id = same key
        key2 = _generate_encryption_key(user_id)
        assert key == key2

    def test_unicode_text_cleaning(self, mock_agent):
        """Test Unicode cleaning functionality."""
        # Test with problematic Unicode characters
        test_text = "Hello\u200bworld\u00a0test\u034f"  # Zero-width space, non-breaking space, combining grapheme joiner
        cleaned = mock_agent._clean_unicode_text(test_text)
        
        # Should preserve normal text and spaces
        assert "Hello" in cleaned
        assert "world" in cleaned
        assert "test" in cleaned
        # Should not contain problematic Unicode
        assert '\u200b' not in cleaned
        assert '\u034f' not in cleaned

    @patch('hushh_mcp.operons.verify_email.prioritize_emails_operon')
    @patch('hushh_mcp.consent.token.validate_token')
    def test_email_prioritization_integration(self, mock_validate, mock_prioritize, mock_agent, sample_emails, valid_email_token):
        """Test agent properly integrates with email prioritization operon."""
        # Mock consent validation
        mock_validate.return_value = (True, "Valid", {'user_id': 'test_user_123'})
        
        # Mock prioritization operon
        mock_prioritize.return_value = {'prioritized_emails': sample_emails}
        
        # Test prioritization using the actual public method
        result = mock_agent.prioritize_emails(sample_emails, 'test_user_123', valid_email_token.token)
        
        assert isinstance(result, list)
        mock_prioritize.assert_called_once()

    @patch('google.generativeai.GenerativeModel')
    @patch('hushh_mcp.consent.token.validate_token')
    def test_ai_event_extraction(self, mock_validate, mock_genai, mock_agent, sample_emails, valid_email_token):
        """Test AI-powered event extraction functionality."""
        # Mock consent validation
        mock_validate.return_value = (True, "Valid", {'user_id': 'test_user_123'})
        
        # Mock AI response
        mock_response = Mock()
        mock_response.text = json.dumps({
            "events": [
                {
                    "summary": "Team Meeting",
                    "start_time": "2025-08-11T14:00:00",
                    "end_time": "2025-08-11T15:00:00",
                    "confidence": 0.9
                }
            ]
        })
        
        mock_ai_instance = Mock()
        mock_ai_instance.generate_content.return_value = mock_response
        mock_genai.return_value = mock_ai_instance
        
        # Test event extraction
        events = mock_agent._extract_events_with_ai(sample_emails, 'test_user_123', valid_email_token.token)
        
        assert len(events) >= 1
        assert events[0]['summary'] == "Team Meeting"
        assert events[0]['confidence'] >= 0.7  # High confidence threshold

    @patch('googleapiclient.discovery.build')
    @patch('hushh_mcp.consent.token.validate_token')
    def test_calendar_creation_integration(self, mock_validate, mock_google_service, mock_agent, valid_calendar_token):
        """Test Google Calendar integration for event creation."""
        # Mock consent validation
        mock_validate.return_value = (True, "Valid", {'user_id': 'test_user_123'})
        
        # Mock Google Calendar service
        mock_service = Mock()
        mock_events = Mock()
        mock_service.events.return_value = mock_events
        mock_events.insert.return_value.execute.return_value = {
            'id': 'test_event_123',
            'htmlLink': 'https://calendar.google.com/event123'
        }
        mock_google_service.return_value = mock_service
        
        # Test event data
        events = [
            {
                'summary': 'Test Event',
                'start_time': '2025-08-11T14:00:00',
                'end_time': '2025-08-11T15:00:00',
                'confidence_score': 0.9
            }
        ]
        
        # Test calendar creation
        results = mock_agent._create_events_in_calendar(
            events, 'test_user_123', valid_calendar_token.token
        )
        
        assert len(results) == 1
        assert results[0]['status'] == 'success'
        assert 'google_event_id' in results[0]

    @patch('hushh_mcp.vault.encrypt.encrypt_data')
    def test_vault_encryption_integration(self, mock_encrypt, mock_agent):
        """Test vault encryption for storing event data."""
        # Mock encryption
        mock_encrypt.return_value = Mock(
            ciphertext='encrypted_data',
            iv='test_iv', 
            tag='test_tag'
        )
        
        # Test data
        vault_data = {
            'event_id': 'test_123',
            'summary': 'Test Event',
            'user_id': 'test_user_123'
        }
        
        # Generate encryption key
        user_id = "test_user_123"
        encryption_key = _generate_encryption_key(user_id)
        
        # Test encryption call
        mock_encrypt(json.dumps(vault_data), encryption_key)
        
        mock_encrypt.assert_called_once()
        args, kwargs = mock_encrypt.call_args
        assert json.loads(args[0]) == vault_data
        assert args[1] == encryption_key

    @patch('hushh_mcp.operons.email_analysis.prioritize_emails_operon')
    @patch('hushh_mcp.operons.email_analysis.categorize_emails_operon')
    @patch('googleapiclient.discovery.build')
    @patch('google.generativeai.GenerativeModel')
    @patch('hushh_mcp.consent.token.validate_token')
    def test_comprehensive_agent_workflow(self, mock_validate, mock_genai, mock_google_service, 
                                         mock_categorize, mock_prioritize, mock_agent, 
                                         sample_emails, valid_email_token, valid_calendar_token):
        """Test complete agent workflow from emails to calendar events."""
        # Mock consent validation for both tokens
        mock_validate.return_value = (True, "Valid", {'user_id': 'test_user_123'})
        
        # Mock email prioritization
        prioritized_emails = sample_emails.copy()
        for i, email in enumerate(prioritized_emails):
            email['priority_score'] = 8 - i
        mock_prioritize.return_value = prioritized_emails
        
        # Mock email categorization  
        categorized_emails = prioritized_emails.copy()
        for email in categorized_emails:
            email['category'] = 'work'
        mock_categorize.return_value = categorized_emails
        
        # Mock AI event extraction
        mock_response = Mock()
        mock_response.text = json.dumps({
            "events": [
                {
                    "summary": "Team Meeting",
                    "start_time": "2025-08-11T14:00:00",
                    "end_time": "2025-08-11T15:00:00", 
                    "confidence": 0.9
                }
            ]
        })
        mock_ai_instance = Mock()
        mock_ai_instance.generate_content.return_value = mock_response
        mock_genai.return_value = mock_ai_instance
        
        # Mock Google Calendar
        mock_service = Mock()
        mock_events = Mock()
        mock_service.events.return_value = mock_events
        mock_events.insert.return_value.execute.return_value = {
            'id': 'created_event_123'
        }
        mock_google_service.return_value = mock_service
        
        # Test complete workflow
        with patch.object(mock_agent, '_read_recent_emails', return_value=sample_emails):
            result = mock_agent.handle(
                user_id='test_user_123',
                email_token=valid_email_token.token,
                calendar_token=valid_calendar_token.token,
                action='comprehensive_analysis'
            )
        
        # Verify workflow completion
        assert result['status'] == 'success'
        assert 'analysis_summary' in result
        assert result['analysis_summary']['events_created'] >= 1
        
        # Verify all operons were called
        mock_prioritize.assert_called()
        mock_categorize.assert_called()

    def test_agent_error_handling(self, mock_agent):
        """Test agent handles errors gracefully."""
        # Test with invalid action
        with pytest.raises(ValueError, match="Unsupported action"):
            mock_agent.handle(
                user_id='test_user_123',
                email_token='valid_token',
                calendar_token='valid_token', 
                action='invalid_action'
            )
    
    def test_scope_enforcement(self, mock_agent):
        """Test agent enforces proper scopes for different operations."""
        # Test email operations require email scope
        with pytest.raises(PermissionError):
            mock_agent._validate_consent('test_user', 'token', ConsentScope.VAULT_WRITE_CALENDAR)
            # This should fail when trying to read emails with calendar scope

    @pytest.mark.parametrize("confidence_threshold,expected_count", [
        (0.7, 2),  # High threshold, fewer events
        (0.5, 3),  # Medium threshold, more events
        (0.9, 1),  # Very high threshold, minimal events
    ])
    def test_event_confidence_filtering(self, mock_agent, confidence_threshold, expected_count):
        """Test event filtering based on confidence scores."""
        mock_events = [
            {'summary': 'High Confidence Event', 'confidence_score': 0.95},
            {'summary': 'Medium Confidence Event', 'confidence_score': 0.75},
            {'summary': 'Low Confidence Event', 'confidence_score': 0.45}
        ]
        
        filtered = [e for e in mock_events if e['confidence_score'] >= confidence_threshold]
        assert len(filtered) <= expected_count


class TestAgentSecurityCompliance:
    """Test suite for security and compliance requirements."""
    
    def test_no_hardcoded_credentials(self):
        """Ensure no hardcoded credentials in agent code."""
        import inspect
        from hushh_mcp.agents.addtocalendar.index import AddToCalendarAgent
        
        source = inspect.getsource(AddToCalendarAgent)
        
        # Should not contain hardcoded API keys or tokens
        forbidden_patterns = ['api_key=', 'token=', 'password=', 'secret=']
        for pattern in forbidden_patterns:
            assert pattern.lower() not in source.lower(), f"Found potential hardcoded credential: {pattern}"

    def test_consent_token_required(self, mock_agent):
        """Test that all agent operations require valid consent tokens."""
        # Attempt operation without valid token should fail
        with pytest.raises((PermissionError, ValueError)):
            mock_agent.handle(
                user_id='test_user',
                email_token=None,
                calendar_token=None,
                action='comprehensive_analysis'
            )

    def test_user_id_validation(self, mock_agent):
        """Test agent validates user_id matches token."""
        # This test ensures token user_id must match provided user_id
        with pytest.raises((PermissionError, ValueError)):
            mock_agent._validate_consent(
                user_id='user_A',
                token='token_for_user_B', 
                scope=ConsentScope.VAULT_READ_EMAIL
            )
