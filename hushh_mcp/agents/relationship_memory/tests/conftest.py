"""
Pytest configuration and fixtures for relationship memory agent tests
"""

import pytest
import tempfile
import os
from typing import Dict, Any
from hushh_mcp.agents.relationship_memory.index import RelationshipMemoryAgent
from hushh_mcp.consent.token import issue_token
from hushh_mcp.types import ConsentScope


@pytest.fixture
def temp_vault_key():
    """Provide a test vault key"""
    return "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"


@pytest.fixture
def test_user_id():
    """Provide a test user ID"""
    return "test_user_pytest"


@pytest.fixture
def agent():
    """Create a relationship memory agent instance"""
    return RelationshipMemoryAgent()


@pytest.fixture
def tokens(agent, test_user_id):
    """Issue all required tokens for testing"""
    tokens = {}
    for scope in agent.required_scopes:
        token = issue_token(
            user_id=test_user_id,
            agent_id=agent.agent_id,
            scope=scope,
            expires_in_ms=3600000  # 1 hour
        )
        tokens[scope.value] = token.token
    return tokens


@pytest.fixture
def agent_handler(agent, test_user_id, tokens, temp_vault_key):
    """Helper function to handle agent requests"""
    def _handle(user_input: str) -> Dict[str, Any]:
        return agent.handle(
            user_id=test_user_id,
            tokens=tokens,
            user_input=user_input,
            vault_key=temp_vault_key
        )
    return _handle


@pytest.fixture(autouse=True)
def clean_test_data():
    """Clean up test data before and after each test"""
    # This runs before each test
    yield
    # This runs after each test - cleanup if needed
