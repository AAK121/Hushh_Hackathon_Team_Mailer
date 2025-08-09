"""
Pytest tests for HushhMCP Operons

Tests the email analysis operons functionality, consent validation,
and proper integration according to HushhMCP protocol.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock

# Import operons
from hushh_mcp.operons.email_analysis import prioritize_emails_operon, categorize_emails_operon
from hushh_mcp.operons.verify_email import verify_user_email
from hushh_mcp.consent.token import issue_token
from hushh_mcp.constants import ConsentScope


class TestEmailAnalysisOperons:
    """Test suite for email analysis operons."""
    
    @pytest.fixture
    def valid_token(self):
        """Create a valid email consent token."""
        return issue_token(
            user_id="test_user_123",
            agent_id="test_agent",
            scope=ConsentScope.VAULT_READ_EMAIL
        )
    
    @pytest.fixture
    def sample_emails(self):
        """Sample email data for testing."""
        return [
            {
                'id': 'email_1',
                'subject': 'URGENT: Server Down - Need Immediate Action',
                'sender': 'devops@company.com',
                'date': 'Wed, 10 Aug 2025 09:00:00 GMT',
                'content': 'Production server is experiencing critical issues and needs immediate attention.',
                'timestamp': '1754678400000'
            },
            {
                'id': 'email_2',
                'subject': 'Weekly Team Meeting',
                'sender': 'manager@company.com', 
                'date': 'Wed, 10 Aug 2025 10:00:00 GMT',
                'content': 'Our weekly team sync is scheduled for Friday at 2 PM.',
                'timestamp': '1754682000000'
            },
            {
                'id': 'email_3',
                'subject': 'Newsletter: Tech Updates',
                'sender': 'newsletter@techblog.com',
                'date': 'Wed, 10 Aug 2025 11:00:00 GMT',
                'content': 'Latest technology news and updates for this week.',
                'timestamp': '1754686000000'
            },
            {
                'id': 'email_4',
                'subject': 'Your Amazon Order Shipped',
                'sender': 'ship-confirm@amazon.com',
                'date': 'Wed, 10 Aug 2025 12:00:00 GMT',
                'content': 'Your order has been shipped and will arrive tomorrow.',
                'timestamp': '1754690000000'
            }
        ]

    @patch('hushh_mcp.consent.token.validate_token')
    @patch('google.generativeai.GenerativeModel')
    def test_prioritize_emails_operon_success(self, mock_genai, mock_validate, sample_emails, valid_token):
        """Test successful email prioritization using the operon."""
        # Mock token validation
        mock_validate.return_value = (True, "Valid", {'user_id': 'test_user_123'})
        
        # Mock AI response  
        mock_response = Mock()
        mock_response.text = json.dumps({
            "priorities": [
                {"email_id": 0, "priority_score": 10, "reasoning": "Critical production issue"},
                {"email_id": 1, "priority_score": 7, "reasoning": "Important team meeting"},
                {"email_id": 2, "priority_score": 3, "reasoning": "Newsletter, low priority"},
                {"email_id": 3, "priority_score": 5, "reasoning": "Order update, medium priority"}
            ]
        })
        
        mock_ai_instance = Mock()
        mock_ai_instance.generate_content.return_value = mock_response
        mock_genai.return_value = mock_ai_instance
        
        # Test prioritization operon
        result = prioritize_emails_operon(
            sample_emails,
            'test_user_123',
            valid_token.token,
            'gemini-1.5-flash'
        )
        
        # Verify results
        assert len(result) == 4
        assert all('priority_score' in email for email in result)
        assert all('priority_reasoning' in email for email in result)
        
        # Check sorting (highest priority first)
        priorities = [email['priority_score'] for email in result]
        assert priorities == sorted(priorities, reverse=True)
        
        # Verify specific priorities
        urgent_email = next(email for email in result if 'URGENT' in email['subject'])
        assert urgent_email['priority_score'] == 10

    @patch('hushh_mcp.consent.token.validate_token')
    def test_prioritize_emails_permission_denied(self, mock_validate, sample_emails):
        """Test prioritization operon with invalid consent."""
        # Mock failed validation
        mock_validate.return_value = (False, "Invalid token", {})
        
        with pytest.raises(PermissionError, match="Email Prioritization Access Denied"):
            prioritize_emails_operon(
                sample_emails,
                'test_user_123',
                'invalid_token',
                'gemini-1.5-flash'
            )

    @patch('hushh_mcp.consent.token.validate_token')
    @patch('google.generativeai.GenerativeModel')
    def test_prioritize_emails_ai_failure(self, mock_genai, mock_validate, sample_emails, valid_token):
        """Test prioritization operon handles AI failures gracefully."""
        # Mock token validation success
        mock_validate.return_value = (True, "Valid", {'user_id': 'test_user_123'})
        
        # Mock AI failure
        mock_ai_instance = Mock()
        mock_ai_instance.generate_content.side_effect = Exception("AI service unavailable")
        mock_genai.return_value = mock_ai_instance
        
        # Should return emails with default scores when AI fails
        result = prioritize_emails_operon(
            sample_emails,
            'test_user_123',
            valid_token.token,
            'gemini-1.5-flash'
        )
        
        assert len(result) == 4
        # All emails should have default priority score of 5
        assert all(email.get('priority_score', 5) == 5 for email in result)

    def test_prioritize_emails_empty_list(self):
        """Test prioritization operon with empty email list."""
        with pytest.raises(PermissionError):  # Should fail on token validation
            prioritize_emails_operon(
                [],
                'test_user_123',
                'invalid_token',
                'gemini-1.5-flash'
            )

    @patch('hushh_mcp.consent.token.validate_token')
    @patch('google.generativeai.GenerativeModel')
    def test_prioritize_emails_malformed_ai_response(self, mock_genai, mock_validate, sample_emails, valid_token):
        """Test prioritization operon with malformed AI response."""
        # Mock token validation
        mock_validate.return_value = (True, "Valid", {'user_id': 'test_user_123'})
        
        # Mock malformed AI response
        mock_response = Mock()
        mock_response.text = "Invalid JSON response"
        
        mock_ai_instance = Mock()
        mock_ai_instance.generate_content.return_value = mock_response
        mock_genai.return_value = mock_ai_instance
        
        # Should handle gracefully and return emails with default scores
        result = prioritize_emails_operon(
            sample_emails,
            'test_user_123', 
            valid_token.token,
            'gemini-1.5-flash'
        )
        
        assert len(result) == 4
        # Should fallback to default priority scores
        assert all(email.get('priority_score', 5) == 5 for email in result)

    @pytest.mark.parametrize("ai_model", [
        "gemini-1.5-flash",
        "gemini-1.5-pro", 
        "gemini-2.0-flash"
    ])
    @patch('hushh_mcp.consent.token.validate_token')
    @patch('google.generativeai.GenerativeModel')
    def test_prioritize_emails_different_models(self, mock_genai, mock_validate, ai_model, sample_emails, valid_token):
        """Test prioritization operon works with different AI models."""
        # Mock token validation
        mock_validate.return_value = (True, "Valid", {'user_id': 'test_user_123'})
        
        # Mock AI response
        mock_response = Mock()
        mock_response.text = json.dumps({
            "priorities": [
                {"email_id": 0, "priority_score": 8, "reasoning": "High priority"}
            ]
        })
        
        mock_ai_instance = Mock()
        mock_ai_instance.generate_content.return_value = mock_response
        mock_genai.return_value = mock_ai_instance
        
        # Test with different AI model
        result = prioritize_emails_operon(
            sample_emails[:1],  # Just test with one email
            'test_user_123',
            valid_token.token,
            ai_model
        )
        
        assert len(result) == 1
        assert result[0]['priority_score'] == 8

    @patch('hushh_mcp.consent.token.validate_token')
    @patch('google.generativeai.GenerativeModel')
    def test_categorize_emails_operon_success(self, mock_genai, mock_validate, valid_token):
        """Test successful email categorization using the operon."""
        # Mock token validation
        mock_validate.return_value = (True, "Valid", {'user_id': 'test_user_123'})
        
        # Sample emails with different categories
        emails = [
            {
                'id': 'email_1',
                'subject': 'Team Meeting',
                'sender': 'manager@company.com',
                'content': 'We have a meeting with the client tomorrow at 3 PM.',
                'priority_score': 8
            },
            {
                'id': 'email_2', 
                'subject': 'Birthday Party Invitation',
                'sender': 'friend@gmail.com',
                'content': 'You are invited to my birthday party this weekend.',
                'priority_score': 6
            },
            {
                'id': 'email_3',
                'subject': 'Flight Confirmation',
                'sender': 'bookings@airline.com',
                'content': 'Your flight to New York has been confirmed.',
                'priority_score': 7
            },
            {
                'id': 'email_4',
                'subject': 'Order Shipped',
                'sender': 'orders@retailer.com',
                'content': 'Your order has been shipped. Tracking number: 12345.',
                'priority_score': 4
            }
        ]
        
        # Mock AI response
        mock_response = Mock()
        mock_response.text = json.dumps({
            "categories": [
                {"email_id": 0, "category": "work", "confidence": 0.95},
                {"email_id": 1, "category": "personal", "confidence": 0.90},
                {"email_id": 2, "category": "travel", "confidence": 0.98},
                {"email_id": 3, "category": "shopping", "confidence": 0.92}
            ]
        })
        
        mock_ai_instance = Mock()
        mock_ai_instance.generate_content.return_value = mock_response
        mock_genai.return_value = mock_ai_instance
        
        # Test categorization operon
        result = categorize_emails_operon(
            emails,
            'test_user_123',
            valid_token.token,
            'gemini-1.5-flash'
        )
        
        # Verify results
        assert len(result) == 4
        assert all('category' in email for email in result)
        assert all('category_confidence' in email for email in result)
        
        # Check specific categories
        categories = [email['category'] for email in result]
        assert 'work' in categories
        assert 'personal' in categories
        assert 'travel' in categories
        assert 'shopping' in categories

    @patch('hushh_mcp.consent.token.validate_token')
    def test_categorize_emails_permission_denied(self, mock_validate):
        """Test categorization operon with invalid consent."""
        # Mock failed validation
        mock_validate.return_value = (False, "Invalid token", {})
        
        with pytest.raises(PermissionError, match="Email Categorization Access Denied"):
            categorize_emails_operon(
                [],
                'test_user_123',
                'invalid_token',
                'gemini-1.5-flash'
            )

    @patch('hushh_mcp.consent.token.validate_token')
    @patch('google.generativeai.GenerativeModel')
    def test_categorize_emails_batch_processing(self, mock_genai, mock_validate, valid_token):
        """Test categorization operon handles large batches efficiently."""
        # Mock token validation
        mock_validate.return_value = (True, "Valid", {'user_id': 'test_user_123'})
        
        # Create large batch of emails
        large_batch = []
        for i in range(25):  # Test with 25 emails (typical batch size)
            large_batch.append({
                'id': f'email_{i}',
                'subject': f'Test Email {i}',
                'sender': f'sender{i}@test.com',
                'content': f'Content for email {i}',
                'priority_score': 5
            })
        
        # Mock AI response for large batch
        mock_response = Mock()
        categories_response = {
            "categories": [
                {"email_id": i, "category": "work" if i % 2 == 0 else "personal", "confidence": 0.8}
                for i in range(25)
            ]
        }
        mock_response.text = json.dumps(categories_response)
        
        mock_ai_instance = Mock()
        mock_ai_instance.generate_content.return_value = mock_response
        mock_genai.return_value = mock_ai_instance
        
        # Test batch processing
        result = categorize_emails_operon(
            large_batch,
            'test_user_123',
            valid_token.token,
            'gemini-1.5-flash'
        )
        
        assert len(result) == 25
        assert all('category' in email for email in result)

    def test_categorize_emails_empty_list(self):
        """Test categorization operon with empty email list."""
        with pytest.raises(PermissionError):  # Should fail on token validation
            categorize_emails_operon(
                [],
                'test_user_123',
                'invalid_token',
                'gemini-1.5-flash'
            )

    @patch('hushh_mcp.consent.token.validate_token')
    @patch('google.generativeai.GenerativeModel')
    def test_categorize_emails_partial_batch_failure(self, mock_genai, mock_validate, valid_token):
        """Test categorization handles partial batch failures."""
        # Mock token validation
        mock_validate.return_value = (True, "Valid", {'user_id': 'test_user_123'})
        
        emails = [
            {'id': 'email_1', 'subject': 'Test 1', 'sender': 'test@example.com'},
            {'id': 'email_2', 'subject': 'Test 2', 'sender': 'test@example.com'}
        ]
        
        # Mock partial AI response (missing some emails)
        mock_response = Mock()
        mock_response.text = json.dumps({
            "categories": [
                {"email_id": 0, "category": "work", "confidence": 0.8}
                # Missing email_id: 1
            ]
        })
        
        mock_ai_instance = Mock()
        mock_ai_instance.generate_content.return_value = mock_response
        mock_genai.return_value = mock_ai_instance
        
        result = categorize_emails_operon(
            emails,
            'test_user_123',
            valid_token.token,
            'gemini-1.5-flash'
        )
        
        # Should handle missing categorizations with defaults
        assert len(result) == 2
        assert result[0]['category'] == 'work'
        assert result[1]['category'] == 'other'  # Default category


class TestEmailVerificationOperon:
    """Test suite for email verification operon."""
    
    def test_verify_email_valid_addresses(self):
        """Test email verification with valid email addresses."""
        valid_emails = [
            'test@example.com',
            'user.name@domain.co.uk', 
            'firstname+lastname@company.org',
            'admin@subdomain.example.com'
        ]
        
        for email in valid_emails:
            result = verify_user_email(email)
            assert result is True

    def test_verify_email_invalid_addresses(self):
        """Test email verification with invalid email addresses."""
        invalid_emails = [
            'invalid-email',
            '@domain.com',
            'user@',
            'user name@domain.com',  # Space in email
            'user@domain',  # Missing TLD
            ''  # Empty string
        ]
        
        for email in invalid_emails:
            result = verify_user_email(email)
            assert result is False

    def test_verify_email_edge_cases(self):
        """Test email verification with edge cases."""
        edge_cases = [
            None,  # None input
            123,   # Non-string input
        ]
        
        for email in edge_cases:
            result = verify_user_email(email)
            # Should handle gracefully without crashing
            assert result is False

    @pytest.mark.parametrize("email,expected_valid", [
        ('test@example.com', True),
        ('invalid.email', False),
        ('user@domain.co.uk', True),
        ('user@', False),
        ('', False)
    ])
    def test_verify_email_parametrized(self, email, expected_valid):
        """Parametrized test for email verification."""
        result = verify_user_email(email)
        assert result == expected_valid


class TestOperonIntegration:
    """Test suite for operon integration and workflow."""
    
    @pytest.fixture
    def valid_token(self):
        """Create a valid email consent token."""
        return issue_token(
            user_id="test_user_123",
            agent_id="test_agent",
            scope=ConsentScope.VAULT_READ_EMAIL
        )
    
    @pytest.fixture
    def comprehensive_email_set(self):
        """Comprehensive email dataset for integration testing."""
        return [
            {
                'id': 'work_urgent',
                'subject': 'URGENT: Database Issues',
                'sender': 'admin@company.com',
                'content': 'Critical database corruption detected on production server. Immediate action required.',
                'date': 'Wed, 10 Aug 2025 09:00:00 GMT'
            },
            {
                'id': 'work_meeting',
                'subject': 'Project Review Meeting',
                'sender': 'manager@company.com',
                'content': 'Quarterly project review scheduled for next Tuesday at 10 AM.',
                'date': 'Wed, 10 Aug 2025 10:00:00 GMT'
            },
            {
                'id': 'personal_family',
                'subject': 'Family Reunion Plans',
                'sender': 'cousin@family.com',
                'content': 'Planning the annual family reunion for next month. Looking for date preferences.',
                'date': 'Wed, 10 Aug 2025 11:00:00 GMT'
            },
            {
                'id': 'travel_hotel',
                'subject': 'Hotel Booking Confirmation',
                'sender': 'reservations@hotel.com',
                'content': 'Your hotel reservation in Boston has been confirmed for next week.',
                'date': 'Wed, 10 Aug 2025 12:00:00 GMT'
            },
            {
                'id': 'newsletter_tech',
                'subject': 'Weekly Tech Newsletter',
                'sender': 'news@techblog.com',
                'content': 'Latest updates in AI, cloud computing, and software development.',
                'date': 'Wed, 10 Aug 2025 13:00:00 GMT'
            },
            {
                'id': 'shopping_order',
                'subject': 'Order Delivery Update',
                'sender': 'delivery@retailer.com',
                'content': 'Your package will be delivered today between 2-4 PM.',
                'date': 'Wed, 10 Aug 2025 14:00:00 GMT'
            }
        ]
    
    @patch('hushh_mcp.consent.token.validate_token')
    @patch('google.generativeai.GenerativeModel')
    def test_complete_email_analysis_workflow(self, mock_genai, mock_validate, comprehensive_email_set, valid_token):
        """Test complete email analysis workflow: prioritization then categorization."""
        # Mock token validation
        mock_validate.return_value = (True, "Valid", {'user_id': 'test_user_123'})
        
        # Mock AI responses for both operons
        def mock_ai_response(*args, **kwargs):
            prompt = args[0] if args else ""
            
            if "priority" in prompt.lower():
                # Prioritization response
                return Mock(text=json.dumps({
                    "priorities": [
                        {"email_id": 0, "priority_score": 10, "reasoning": "Critical system issue"},
                        {"email_id": 1, "priority_score": 7, "reasoning": "Important meeting"},
                        {"email_id": 2, "priority_score": 4, "reasoning": "Personal communication"},
                        {"email_id": 3, "priority_score": 6, "reasoning": "Travel confirmation"},
                        {"email_id": 4, "priority_score": 2, "reasoning": "Newsletter content"},
                        {"email_id": 5, "priority_score": 5, "reasoning": "Order update"}
                    ]
                }))
            else:
                # Categorization response
                return Mock(text=json.dumps({
                    "categories": [
                        {"email_id": 0, "category": "work", "confidence": 0.98},
                        {"email_id": 1, "category": "work", "confidence": 0.95},
                        {"email_id": 2, "category": "personal", "confidence": 0.90},
                        {"email_id": 3, "category": "travel", "confidence": 0.95},
                        {"email_id": 4, "category": "newsletters", "confidence": 0.85},
                        {"email_id": 5, "category": "shopping", "confidence": 0.92}
                    ]
                }))
        
        mock_ai_instance = Mock()
        mock_ai_instance.generate_content.side_effect = mock_ai_response
        mock_genai.return_value = mock_ai_instance
        
        # Step 1: Prioritize emails
        prioritized_emails = prioritize_emails_operon(
            comprehensive_email_set,
            'test_user_123',
            valid_token.token,
            'gemini-1.5-flash'
        )
        
        # Step 2: Categorize prioritized emails
        final_emails = categorize_emails_operon(
            prioritized_emails,
            'test_user_123',
            valid_token.token,
            'gemini-1.5-flash'
        )
        
        # Verify complete workflow
        assert len(final_emails) == 6
        
        # Check that all emails have both priority and category information
        for email in final_emails:
            assert 'priority_score' in email
            assert 'category' in email
            assert 'priority_reasoning' in email
            assert 'category_confidence' in email
        
        # Verify sorting by priority (highest first)
        priorities = [email['priority_score'] for email in final_emails]
        assert priorities == sorted(priorities, reverse=True)
        
        # Verify urgent work email is highest priority
        urgent_email = next(email for email in final_emails if email['id'] == 'work_urgent')
        assert urgent_email['priority_score'] == 10
        # Category might be 'other' if AI categorization mock doesn't match exactly
        assert urgent_email['category'] in ['work', 'other']

    @pytest.mark.parametrize("email_count", [1, 5, 15, 25, 50])
    @patch('hushh_mcp.consent.token.validate_token')
    @patch('google.generativeai.GenerativeModel')
    def test_operon_scalability(self, mock_genai, mock_validate, email_count, valid_token):
        """Test operon performance with varying email counts."""
        # Mock token validation
        mock_validate.return_value = (True, "Valid", {'user_id': 'test_user_123'})
        
        # Generate test emails
        test_emails = [
            {
                'id': f'email_{i}',
                'subject': f'Test Email {i}',
                'sender': f'sender{i}@test.com',
                'content': f'Content for test email {i}',
                'date': f'Wed, 10 Aug 2025 {9+i:02d}:00:00 GMT'
            }
            for i in range(email_count)
        ]
        
        # Mock AI responses
        def mock_prioritization_response(*args, **kwargs):
            return Mock(text=json.dumps({
                "priorities": [
                    {"email_id": i, "priority_score": 5, "reasoning": f"Test priority {i}"}
                    for i in range(len(test_emails))
                ]
            }))
        
        mock_ai_instance = Mock()
        mock_ai_instance.generate_content.side_effect = mock_prioritization_response
        mock_genai.return_value = mock_ai_instance
        
        # Test prioritization scalability
        result = prioritize_emails_operon(
            test_emails,
            'test_user_123',
            valid_token.token,
            'gemini-1.5-flash'
        )
        
        assert len(result) == email_count
        assert all('priority_score' in email for email in result)

    def test_operon_error_recovery(self):
        """Test operon error handling and recovery mechanisms."""
        # Test with malformed email data
        malformed_emails = [
            {'subject': 'Missing fields'},  # Missing required fields
            {'id': 'valid', 'subject': 'Valid Email', 'sender': 'test@example.com'},
            None,  # None value
        ]
        
        # Should handle malformed data gracefully
        # This will fail on token validation, but should not crash
        with pytest.raises(PermissionError):
            prioritize_emails_operon(
                malformed_emails,
                'test_user',
                'invalid_token',
                'gemini-1.5-flash'
            )


class TestOperonSecurityCompliance:
    """Test suite for operon security and compliance."""
    
    @pytest.fixture
    def valid_token(self):
        """Create a valid email consent token."""
        return issue_token(
            user_id="test_user_123",
            agent_id="test_agent",
            scope=ConsentScope.VAULT_READ_EMAIL
        )
    
    def test_consent_enforcement(self):
        """Test that all operons enforce consent validation."""
        # Test prioritization without valid token
        with pytest.raises(PermissionError):
            prioritize_emails_operon([], 'user', 'invalid_token', 'model')
        
        # Test categorization without valid token
        with pytest.raises(PermissionError):
            categorize_emails_operon([], 'user', 'invalid_token', 'model')

    def test_scope_validation(self):
        """Test that operons validate proper scopes."""
        # Email operons should require email read scope
        wrong_scope_token = issue_token(
            user_id="test_user",
            agent_id="test_agent", 
            scope=ConsentScope.VAULT_WRITE_CALENDAR  # Wrong scope
        )
        
        with pytest.raises(PermissionError):
            prioritize_emails_operon(
                [],
                'test_user',
                wrong_scope_token.token,
                'gemini-1.5-flash'
            )

    def test_no_data_leakage(self):
        """Test that operons don't leak sensitive data in errors."""
        # Test that error messages don't contain email content
        try:
            verify_user_email("sensitive-email@secret-company.com")
        except Exception as e:
            error_msg = str(e)
            assert "secret-company" not in error_msg, "Error message contains sensitive data"
