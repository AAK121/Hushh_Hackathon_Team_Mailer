# tests/test_hushh_mcp_compliance.py

"""
HushhMCP Compliance Test Suite
==============================

This test suite verifies that both agents (MailerPanda and AddToCalendar)
are properly implementing the HushhMCP protocol according to the specification.

Test Categories:
1. Consent Token Validation
2. Vault Encryption Usage  
3. Trust Link Implementation
4. Operon Integration
5. Frontend API Integration
6. Manifest Compliance
"""

import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Test setup
import sys
sys.path.insert(0, '.')

from hushh_mcp.consent.token import issue_token, validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.frontend_integration import frontend_integration, CredentialRequest, ConsentRequest
from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
from hushh_mcp.agents.addtocalendar.index import AddToCalendarAgent


class TestHushhMCPCompliance:
    """Test suite for HushhMCP protocol compliance."""
    
    @pytest.fixture
    def valid_user_id(self):
        return "user_test_12345"
    
    @pytest.fixture
    def valid_consent_tokens(self, valid_user_id):
        """Generate valid consent tokens for testing."""
        tokens = {}
        
        # Email read token
        email_token, _ = issue_token(
            user_id=valid_user_id,
            scopes=[ConsentScope.VAULT_READ_EMAIL],
            duration_hours=1
        )
        tokens[ConsentScope.VAULT_READ_EMAIL.value] = email_token
        
        # Email write token  
        email_write_token, _ = issue_token(
            user_id=valid_user_id,
            scopes=[ConsentScope.VAULT_WRITE_EMAIL],
            duration_hours=1
        )
        tokens[ConsentScope.VAULT_WRITE_EMAIL.value] = email_write_token
        
        # Calendar write token
        calendar_token, _ = issue_token(
            user_id=valid_user_id,
            scopes=[ConsentScope.VAULT_WRITE_CALENDAR],
            duration_hours=1
        )
        tokens[ConsentScope.VAULT_WRITE_CALENDAR.value] = calendar_token
        
        # Temporary scope token
        temp_token, _ = issue_token(
            user_id=valid_user_id,
            scopes=[ConsentScope.CUSTOM_TEMPORARY],
            duration_hours=1
        )
        tokens[ConsentScope.CUSTOM_TEMPORARY.value] = temp_token
        
        return tokens
    
    @pytest.fixture
    def mock_supabase_token(self):
        """Mock Supabase JWT token for testing."""
        import jwt
        payload = {
            "sub": "user_test_12345",
            "email": "test@example.com",
            "aud": "authenticated", 
            "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
            "user_metadata": {},
            "app_metadata": {}
        }
        # Use a test secret
        return jwt.encode(payload, "test_secret", algorithm="HS256")


class TestMailerPandaCompliance(TestHushhMCPCompliance):
    """Test MailerPanda agent HushhMCP compliance."""
    
    def test_mailerpanda_consent_validation(self, valid_user_id, valid_consent_tokens):
        """Test that MailerPanda properly validates consent tokens."""
        
        # Mock environment variables
        with patch.dict(os.environ, {
            'MAILJET_API_KEY': 'test_key',
            'MAILJET_API_SECRET': 'test_secret',
            'GOOGLE_API_KEY': 'test_google_key'
        }):
            agent = MassMailerAgent()
            
            # Test consent validation for content generation
            result = agent._validate_consent_for_operation(
                consent_tokens=valid_consent_tokens,
                operation="content_generation", 
                user_id=valid_user_id
            )
            assert result is True
            
            # Test with invalid user ID should fail
            with pytest.raises(PermissionError):
                agent._validate_consent_for_operation(
                    consent_tokens=valid_consent_tokens,
                    operation="content_generation",
                    user_id="different_user"
                )
    
    def test_mailerpanda_vault_usage(self, valid_user_id, valid_consent_tokens):
        """Test that MailerPanda properly uses vault encryption."""
        
        with patch.dict(os.environ, {
            'MAILJET_API_KEY': 'test_key',
            'MAILJET_API_SECRET': 'test_secret', 
            'GOOGLE_API_KEY': 'test_google_key'
        }):
            agent = MassMailerAgent()
            
            # Test vault storage
            test_data = {"campaign_id": "test123", "content": "test email"}
            vault_key = agent._store_in_vault(
                data=test_data,
                vault_key="test_campaign_123",
                user_id=valid_user_id,
                consent_tokens=valid_consent_tokens
            )
            
            assert vault_key == "test_campaign_123"
    
    def test_mailerpanda_operon_usage(self, valid_user_id, valid_consent_tokens):
        """Test that MailerPanda uses operons correctly."""
        
        with patch.dict(os.environ, {
            'MAILJET_API_KEY': 'test_key',
            'MAILJET_API_SECRET': 'test_secret',
            'GOOGLE_API_KEY': 'test_google_key'
        }):
            
            # Mock the operon
            with patch('hushh_mcp.operons.verify_email.verify_email_operon') as mock_operon:
                mock_operon.return_value = True
                
                agent = MassMailerAgent()
                
                # Test contact reading with operon usage
                with patch('pandas.read_excel') as mock_excel:
                    mock_excel.return_value = Mock()
                    mock_excel.return_value.iterrows.return_value = [
                        (0, {'email': 'test@example.com', 'name': 'Test User'})
                    ]
                    
                    with patch('os.path.exists', return_value=True):
                        contacts = agent._read_contacts_with_consent(
                            user_id=valid_user_id,
                            consent_tokens=valid_consent_tokens
                        )
                        
                        # Verify operon was called
                        mock_operon.assert_called_with('test@example.com')


class TestAddToCalendarCompliance(TestHushhMCPCompliance):
    """Test AddToCalendar agent HushhMCP compliance."""
    
    def test_addtocalendar_consent_validation(self, valid_user_id, valid_consent_tokens):
        """Test that AddToCalendar properly validates consent tokens."""
        
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'}):
            agent = AddToCalendarAgent()
            
            # Test consent validation in prioritize_emails
            with patch('hushh_mcp.operons.email_analysis.prioritize_emails_operon') as mock_operon:
                mock_operon.return_value = []
                
                emails = [{"subject": "Test", "content": "Test email"}]
                result = agent.prioritize_emails(
                    emails=emails,
                    user_id=valid_user_id,
                    consent_token=valid_consent_tokens[ConsentScope.VAULT_READ_EMAIL.value]
                )
                
                # Verify operon was called (indicating consent validation passed)
                mock_operon.assert_called_once()
    
    def test_addtocalendar_vault_encryption(self, valid_user_id, valid_consent_tokens):
        """Test that AddToCalendar properly uses vault encryption."""
        
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'}):
            agent = AddToCalendarAgent()
            
            # Test event creation with vault storage
            with patch('hushh_mcp.vault.encrypt.encrypt_data') as mock_encrypt:
                mock_encrypt.return_value = "encrypted_data"
                
                # Mock Google Calendar service
                with patch.object(agent, '_get_google_service') as mock_service:
                    mock_calendar = Mock()
                    mock_calendar.events().insert().execute.return_value = {
                        'id': 'test_event_123',
                        'htmlLink': 'https://calendar.google.com/event/test'
                    }
                    mock_service.return_value = mock_calendar
                    
                    events = [{
                        'summary': 'Test Event',
                        'start_time': '2025-08-10T14:00:00',
                        'end_time': '2025-08-10T15:00:00',
                        'confidence_score': 0.9
                    }]
                    
                    result = agent.create_events_in_calendar(
                        events=events,
                        user_id=valid_user_id,
                        consent_token=valid_consent_tokens[ConsentScope.VAULT_WRITE_CALENDAR.value]
                    )
                    
                    # Verify encryption was used
                    mock_encrypt.assert_called()
                    assert result['status'] in ['success', 'partial']
    
    def test_addtocalendar_handle_method_compliance(self, valid_user_id, valid_consent_tokens):
        """Test AddToCalendar handle method HushhMCP compliance."""
        
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'}):
            agent = AddToCalendarAgent()
            
            # Test comprehensive analysis action
            with patch.object(agent, 'run_comprehensive_email_analysis') as mock_analysis:
                mock_analysis.return_value = {
                    'status': 'success',
                    'analysis_summary': {'total_emails_processed': 10}
                }
                
                result = agent.handle(
                    user_id=valid_user_id,
                    email_token_str=valid_consent_tokens[ConsentScope.VAULT_READ_EMAIL.value],
                    calendar_token_str=valid_consent_tokens[ConsentScope.VAULT_WRITE_CALENDAR.value],
                    action="comprehensive_analysis"
                )
                
                assert result['status'] == 'success'
                mock_analysis.assert_called_once()


class TestFrontendIntegration(TestHushhMCPCompliance):
    """Test frontend integration compliance."""
    
    def test_credential_storage(self, valid_user_id, mock_supabase_token):
        """Test secure credential storage."""
        
        # Mock environment for JWT verification
        with patch.dict(os.environ, {'SUPABASE_JWT_SECRET': 'test_secret'}):
            request = CredentialRequest(
                user_id=valid_user_id,
                supabase_token=mock_supabase_token,
                google_credentials={"type": "service_account"},
                mailjet_api_key="test_key",
                mailjet_api_secret="test_secret"
            )
            
            with patch('hushh_mcp.vault.encrypt.encrypt_data') as mock_encrypt:
                mock_encrypt.return_value = "encrypted_data"
                
                result = frontend_integration.store_user_credentials(request)
                
                assert result['status'] == 'success'
                assert 'vault_keys' in result
                assert len(result['vault_keys']) == 2  # Google + Mailjet
                
                # Verify encryption was called
                assert mock_encrypt.call_count == 2
    
    def test_consent_token_generation(self, valid_user_id, mock_supabase_token):
        """Test frontend consent token generation."""
        
        with patch.dict(os.environ, {'SUPABASE_JWT_SECRET': 'test_secret'}):
            request = ConsentRequest(
                user_id=valid_user_id,
                supabase_token=mock_supabase_token,
                agent_id="agent_mailerpanda",
                scopes=[ConsentScope.VAULT_READ_EMAIL.value, ConsentScope.CUSTOM_TEMPORARY.value],
                duration_hours=24
            )
            
            result = frontend_integration.generate_consent_tokens(request)
            
            assert result['status'] == 'success'
            assert len(result['consent_tokens']) == 2
            assert ConsentScope.VAULT_READ_EMAIL.value in result['consent_tokens']
            assert ConsentScope.CUSTOM_TEMPORARY.value in result['consent_tokens']
    
    def test_agent_session_creation(self, valid_user_id, mock_supabase_token):
        """Test complete agent session creation."""
        
        with patch.dict(os.environ, {'SUPABASE_JWT_SECRET': 'test_secret'}):
            result = frontend_integration.create_agent_session(
                user_id=valid_user_id,
                supabase_token=mock_supabase_token,
                agent_id="agent_mailerpanda"
            )
            
            assert result['status'] == 'success'
            assert 'session' in result
            
            session = result['session']
            assert session['user_id'] == valid_user_id
            assert session['agent_id'] == "agent_mailerpanda"
            assert 'consent_tokens' in session
            assert 'credential_vault_keys' in session


class TestManifestCompliance:
    """Test agent manifest compliance."""
    
    def test_mailerpanda_manifest(self):
        """Test MailerPanda manifest compliance."""
        from hushh_mcp.agents.mailerpanda.manifest import manifest
        
        # Required fields
        assert 'id' in manifest
        assert 'name' in manifest
        assert 'description' in manifest
        assert 'scopes' in manifest
        assert 'required_scopes' in manifest
        assert 'trust_links' in manifest
        
        # Scope validation
        assert ConsentScope.VAULT_READ_EMAIL in manifest['scopes']
        assert ConsentScope.VAULT_WRITE_EMAIL in manifest['scopes']
        assert ConsentScope.CUSTOM_TEMPORARY in manifest['scopes']
        
        # Required scopes structure
        assert 'content_generation' in manifest['required_scopes']
        assert 'email_sending' in manifest['required_scopes']
    
    def test_addtocalendar_manifest(self):
        """Test AddToCalendar manifest compliance."""
        from hushh_mcp.agents.addtocalendar.manifest import manifest
        
        # Required fields
        assert 'id' in manifest
        assert 'name' in manifest
        assert 'description' in manifest
        assert 'scopes' in manifest
        
        # Scope validation
        assert ConsentScope.VAULT_READ_EMAIL in manifest['scopes']
        assert ConsentScope.VAULT_WRITE_CALENDAR in manifest['scopes']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
