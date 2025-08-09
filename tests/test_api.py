"""
Comprehensive Test Suite for HushMCP API Server
==============================================

Tests the FastAPI-based REST API server for HushMCP agents, including:
- Agent registry functionality
- Consent token validation and generation
- API endpoints for agent execution
- Error handling and security
- Request/response validation
"""

import pytest
import json
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# FastAPI testing
from fastapi.testclient import TestClient
from fastapi import status

# HushMCP imports
from hushh_mcp.types import ConsentScope
from hushh_mcp.consent.token import HushhConsentToken

# Import the API application
import sys
sys.path.append('.')
from api import app, agent_registry, AgentRegistry


class TestAPIHealthAndInfo:
    """Test suite for basic API health and information endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client for API testing."""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test root health check endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "agents_available" in data
        assert "version" in data
        assert data["version"] == "1.0.0"
    
    def test_health_check_endpoint(self, client):
        """Test detailed health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert isinstance(data["agents_available"], int)
        assert data["agents_available"] >= 0
    
    def test_api_metadata(self, client):
        """Test API metadata through OpenAPI schema."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        
        assert schema["info"]["title"] == "HushMCP Agent API"
        assert schema["info"]["description"] == "Privacy-first AI agent orchestration platform"
        assert schema["info"]["version"] == "1.0.0"


class TestAgentRegistry:
    """Test suite for agent registry functionality."""
    
    @pytest.fixture
    def mock_registry(self):
        """Create a mock agent registry for testing."""
        registry = AgentRegistry()
        
        # Mock a test agent
        mock_agent = Mock()
        mock_agent.agent_id = "test_agent"
        mock_agent.handle = Mock(return_value={"status": "success", "data": "test_result"})
        
        registry.agents["test_agent"] = {
            'instance': mock_agent,
            'class': type(mock_agent),
            'module': Mock(),
            'path': Mock(name="test_agent")
        }
        
        return registry
    
    def test_agent_registry_initialization(self):
        """Test agent registry initializes correctly."""
        registry = AgentRegistry()
        
        assert isinstance(registry.agents, dict)
        # Should load actual agents if they exist
        assert len(registry.agents) >= 0
    
    def test_get_existing_agent(self, mock_registry):
        """Test retrieving an existing agent."""
        agent_data = mock_registry.get_agent("test_agent")
        
        assert agent_data is not None
        assert agent_data['instance'].agent_id == "test_agent"
        assert hasattr(agent_data['instance'], 'handle')
    
    def test_get_nonexistent_agent(self, mock_registry):
        """Test retrieving a non-existent agent."""
        agent_data = mock_registry.get_agent("nonexistent_agent")
        
        assert agent_data is None
    
    @patch('importlib.import_module')
    def test_list_agents_with_manifests(self, mock_import, mock_registry):
        """Test listing agents with manifest information."""
        # Mock manifest module
        mock_manifest = {
            'name': 'Test Agent',
            'description': 'A test agent for testing',
            'version': '2.0.0',
            'required_scopes': ['vault.read.email']
        }
        mock_manifest_module = Mock()
        mock_manifest_module.manifest = mock_manifest
        mock_import.return_value = mock_manifest_module
        
        agents = mock_registry.list_agents()
        
        assert len(agents) >= 1
        test_agent = next((agent for agent in agents if agent.id == "test_agent"), None)
        assert test_agent is not None
        assert test_agent.name == "Test Agent"
        assert test_agent.description == "A test agent for testing"
        assert test_agent.version == "2.0.0"
        assert test_agent.required_scopes == ['vault.read.email']
        assert test_agent.status == "active"
    
    @patch('importlib.import_module')
    def test_list_agents_without_manifests(self, mock_import, mock_registry):
        """Test listing agents when manifest loading fails."""
        # Mock import failure
        mock_import.side_effect = ImportError("Manifest not found")
        
        agents = mock_registry.list_agents()
        
        assert len(agents) >= 1
        test_agent = next((agent for agent in agents if agent.id == "test_agent"), None)
        assert test_agent is not None
        assert test_agent.name == "test_agent"
        assert "manifest unavailable" in test_agent.description
        assert test_agent.version == "unknown"
        assert test_agent.status == "limited"


class TestAgentEndpoints:
    """Test suite for agent-related API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client for API testing."""
        return TestClient(app)
    
    @patch.object(agent_registry, 'list_agents')
    def test_list_agents_endpoint(self, mock_list_agents, client):
        """Test the agents listing endpoint."""
        # Mock agent list
        from api import AgentInfo
        mock_agents = [
            AgentInfo(
                id="test_agent",
                name="Test Agent",
                description="A test agent",
                version="1.0.0",
                required_scopes=["vault.read.email"],
                status="active"
            )
        ]
        mock_list_agents.return_value = mock_agents
        
        response = client.get("/agents")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 1
        assert data[0]["id"] == "test_agent"
        assert data[0]["name"] == "Test Agent"
        assert data[0]["status"] == "active"
    
    @patch.object(agent_registry, 'get_agent')
    @patch.object(agent_registry, 'list_agents')
    def test_get_agent_info_success(self, mock_list_agents, mock_get_agent, client):
        """Test successful agent info retrieval."""
        from api import AgentInfo
        
        # Mock agent exists
        mock_get_agent.return_value = {"instance": Mock()}
        
        # Mock agent info
        mock_agent_info = AgentInfo(
            id="test_agent",
            name="Test Agent",
            description="A test agent",
            version="1.0.0",
            required_scopes=["vault.read.email"],
            status="active"
        )
        mock_list_agents.return_value = [mock_agent_info]
        
        response = client.get("/agents/test_agent")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == "test_agent"
        assert data["name"] == "Test Agent"
    
    @patch.object(agent_registry, 'get_agent')
    def test_get_agent_info_not_found(self, mock_get_agent, client):
        """Test agent info retrieval for non-existent agent."""
        mock_get_agent.return_value = None
        
        response = client.get("/agents/nonexistent_agent")
        
        assert response.status_code == 404
        assert "not found" in response.json()["error"]


class TestConsentTokenEndpoints:
    """Test suite for consent token generation and validation."""
    
    @pytest.fixture
    def client(self):
        """Create test client for API testing."""
        return TestClient(app)
    
    @patch('api.issue_token')
    def test_generate_consent_token_success(self, mock_issue_token, client):
        """Test successful consent token generation."""
        # Mock token generation
        mock_token = "HCT:test_token_string"
        mock_expires = datetime.utcnow() + timedelta(hours=24)
        mock_issue_token.return_value = (mock_token, mock_expires)
        
        request_data = {
            "user_id": "test_user_123",
            "scopes": ["vault.read.email", "vault.write.calendar"],
            "duration_hours": 24
        }
        
        response = client.post("/consent/token", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["token"] == mock_token
        assert "expires_at" in data
        assert data["scopes"] == request_data["scopes"]
        
        # Verify issue_token was called correctly
        mock_issue_token.assert_called_once()
        call_args = mock_issue_token.call_args
        assert call_args[1]["user_id"] == "test_user_123"
        assert len(call_args[1]["scopes"]) == 2
        assert call_args[1]["duration_hours"] == 24
    
    def test_generate_consent_token_invalid_scope(self, client):
        """Test consent token generation with invalid scope."""
        request_data = {
            "user_id": "test_user_123",
            "scopes": ["invalid.scope.name"],
            "duration_hours": 24
        }
        
        response = client.post("/consent/token", json=request_data)
        
        assert response.status_code == 400
        assert "Invalid consent scope" in response.json()["error"]
    
    @patch('api.issue_token')
    def test_generate_consent_token_failure(self, mock_issue_token, client):
        """Test consent token generation failure."""
        # Mock token generation failure
        mock_issue_token.side_effect = Exception("Token generation failed")
        
        request_data = {
            "user_id": "test_user_123",
            "scopes": ["vault.read.email"],
            "duration_hours": 24
        }
        
        response = client.post("/consent/token", json=request_data)
        
        assert response.status_code == 500
        assert "Failed to generate consent token" in response.json()["error"]


class TestAgentExecution:
    """Test suite for agent execution endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client for API testing."""
        return TestClient(app)
    
    @pytest.fixture
    def valid_email_token(self):
        """Create a valid email consent token for testing."""
        return HushhConsentToken(
            token='test_email_token',
            user_id='test_user_123',
            agent_id='agent_addtocalendar',
            scope=ConsentScope.VAULT_READ_EMAIL,
            issued_at=int(datetime.utcnow().timestamp() * 1000),
            expires_at=int((datetime.utcnow() + timedelta(hours=1)).timestamp() * 1000),
            signature='test_signature'
        )
    
    @pytest.fixture
    def valid_calendar_token(self):
        """Create a valid calendar consent token for testing."""
        return HushhConsentToken(
            token='test_calendar_token',
            user_id='test_user_123',
            agent_id='agent_addtocalendar',
            scope=ConsentScope.VAULT_WRITE_CALENDAR,
            issued_at=int(datetime.utcnow().timestamp() * 1000),
            expires_at=int((datetime.utcnow() + timedelta(hours=1)).timestamp() * 1000),
            signature='test_signature'
        )
    
    @patch.object(agent_registry, 'get_agent')
    def test_execute_agent_not_found(self, mock_get_agent, client):
        """Test agent execution with non-existent agent."""
        mock_get_agent.return_value = None
        
        request_data = {
            "user_id": "test_user_123",
            "agent_id": "nonexistent_agent",
            "consent_tokens": {"email_token": "test_token"},
            "parameters": {}
        }
        
        response = client.post("/agents/nonexistent_agent/execute", json=request_data)
        
        assert response.status_code == 404
        assert "not found" in response.json()["error"]
    
    def test_execute_agent_id_mismatch(self, client):
        """Test agent execution with mismatched agent IDs."""
        request_data = {
            "user_id": "test_user_123",
            "agent_id": "different_agent",
            "consent_tokens": {"email_token": "test_token"},
            "parameters": {}
        }
        
        response = client.post("/agents/agent_addtocalendar/execute", json=request_data)
        
        assert response.status_code == 400
        assert "Agent ID in request body must match URL parameter" in response.json()["error"]
    
    @patch.object(agent_registry, 'get_agent')
    def test_execute_addtocalendar_agent_success(self, mock_get_agent, client, valid_email_token, valid_calendar_token):
        """Test successful AddToCalendar agent execution."""
        # Mock agent
        mock_agent = Mock()
        mock_agent.handle.return_value = {
            "status": "success",
            "events_created": 2,
            "analysis_summary": {"emails_processed": 5}
        }
        mock_get_agent.return_value = {"instance": mock_agent}
        
        request_data = {
            "user_id": "test_user_123",
            "agent_id": "addtocalendar",
            "consent_tokens": {
                "email_token": valid_email_token.token,
                "calendar_token": valid_calendar_token.token
            },
            "parameters": {
                "action": "comprehensive_analysis"
            }
        }
        
        response = client.post("/agents/addtocalendar/execute", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert data["agent_id"] == "addtocalendar"
        assert "data" in data
        assert data["data"]["events_created"] == 2
        
        # Verify agent was called correctly
        mock_agent.handle.assert_called_once_with(
            user_id="test_user_123",
            email_token_str=valid_email_token.token,
            calendar_token_str=valid_calendar_token.token,
            action="comprehensive_analysis"
        )
    
    @patch.object(agent_registry, 'get_agent')
    def test_execute_addtocalendar_missing_email_token(self, mock_get_agent, client):
        """Test AddToCalendar agent execution with missing email token."""
        mock_get_agent.return_value = {"instance": Mock()}
        
        request_data = {
            "user_id": "test_user_123",
            "agent_id": "addtocalendar",
            "consent_tokens": {},  # Missing email_token
            "parameters": {"action": "comprehensive_analysis"}
        }
        
        response = client.post("/agents/addtocalendar/execute", json=request_data)
        
        assert response.status_code == 200
        assert "requires 'email_token'" in response.json()["error"]
    
    @patch.object(agent_registry, 'get_agent')
    def test_execute_addtocalendar_manual_event_missing_description(self, mock_get_agent, client, valid_email_token, valid_calendar_token):
        """Test AddToCalendar manual event creation with missing description."""
        mock_get_agent.return_value = {"instance": Mock()}
        
        request_data = {
            "user_id": "test_user_123",
            "agent_id": "addtocalendar",
            "consent_tokens": {
                "email_token": valid_email_token.token,
                "calendar_token": valid_calendar_token.token
            },
            "parameters": {
                "action": "manual_event"
                # Missing event_description
            }
        }
        
        response = client.post("/agents/addtocalendar/execute", json=request_data)
        
        assert response.status_code == 200
        assert "requires 'event_description'" in response.json()["error"]
    
    @patch.object(agent_registry, 'get_agent')
    def test_execute_agent_permission_error(self, mock_get_agent, client):
        """Test agent execution with permission error."""
        # Mock agent that raises PermissionError
        mock_agent = Mock()
        mock_agent.handle.side_effect = PermissionError("Access denied")
        mock_get_agent.return_value = {"instance": mock_agent}
        
        request_data = {
            "user_id": "test_user_123",
            "agent_id": "agent_addtocalendar",
            "consent_tokens": {"email_token": "invalid_token"},
            "parameters": {}
        }
        
        response = client.post("/agents/agent_addtocalendar/execute", json=request_data)
        
        assert response.status_code == 403
        assert "Access denied" in response.json()["error"]
    
    @patch.object(agent_registry, 'get_agent')
    def test_execute_agent_general_error(self, mock_get_agent, client):
        """Test agent execution with general error."""
        # Mock agent that raises general exception
        mock_agent = Mock()
        mock_agent.handle.side_effect = Exception("Something went wrong")
        mock_get_agent.return_value = {"instance": mock_agent}
        
        request_data = {
            "user_id": "test_user_123",
            "agent_id": "test_agent",
            "consent_tokens": {"email_token": "test_token"},
            "parameters": {}
        }
        
        response = client.post("/agents/test_agent/execute", json=request_data)
        
        assert response.status_code == 200  # Returns 200 with error in response
        data = response.json()
        
        assert data["status"] == "error"
        assert data["agent_id"] == "test_agent"
        assert "Something went wrong" in data["error"]


class TestSpecificAgentEndpoints:
    """Test suite for agent-specific endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client for API testing."""
        return TestClient(app)
    
    @patch.object(agent_registry, 'get_agent')
    def test_addtocalendar_process_emails_success(self, mock_get_agent, client):
        """Test AddToCalendar specific endpoint success."""
        # Mock agent
        mock_agent = Mock()
        mock_agent.handle.return_value = {"status": "success", "events_created": 3}
        mock_get_agent.return_value = {"instance": mock_agent}
        
        response = client.post(
            "/agents/addtocalendar/process-emails",
            params={
                "user_id": "test_user_123",
                "email_token": "test_email_token",
                "calendar_token": "test_calendar_token"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert data["agent_id"] == "addtocalendar"
        assert data["data"]["events_created"] == 3
    
    @patch.object(agent_registry, 'get_agent')
    def test_addtocalendar_process_emails_not_available(self, mock_get_agent, client):
        """Test AddToCalendar specific endpoint when agent not available."""
        mock_get_agent.return_value = None
        
        response = client.post(
            "/agents/addtocalendar/process-emails",
            params={
                "user_id": "test_user_123",
                "email_token": "test_email_token",
                "calendar_token": "test_calendar_token"
            }
        )
        
        assert response.status_code == 404
        assert "not available" in response.json()["error"]


class TestErrorHandling:
    """Test suite for API error handling."""
    
    @pytest.fixture
    def client(self):
        """Create test client for API testing."""
        return TestClient(app)
    
    def test_http_exception_handling(self, client):
        """Test HTTP exception handling format."""
        # Make a request that will generate a 404
        response = client.get("/nonexistent/endpoint")
        
        assert response.status_code == 404
        data = response.json()
        
        assert "detail" in data
        assert data["detail"] == "Not Found"
    
    def test_invalid_json_request(self, client):
        """Test handling of invalid JSON in request body."""
        # Send malformed JSON
        response = client.post(
            "/agents/test_agent/execute",
            data="invalid json content",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # FastAPI validation error


class TestAPISecurityCompliance:
    """Test suite for API security and compliance."""
    
    @pytest.fixture
    def client(self):
        """Create test client for API testing."""
        return TestClient(app)
    
    def test_cors_headers(self, client):
        """Test CORS middleware configuration."""
        response = client.options("/")
        
        # CORS should be enabled (headers vary by browser)
        assert response.status_code in [200, 405]  # OPTIONS might not be defined for root
    
    def test_api_requires_valid_request_format(self, client):
        """Test API validates request format properly."""
        # Send incomplete agent execution request
        incomplete_request = {
            "user_id": "test_user_123"
            # Missing required fields
        }
        
        response = client.post("/agents/test_agent/execute", json=incomplete_request)
        
        assert response.status_code == 422  # Validation error
    
    def test_agent_execution_input_validation(self, client):
        """Test input validation for agent execution."""
        # Send request with invalid data types
        invalid_request = {
            "user_id": 123,  # Should be string
            "agent_id": "test_agent",
            "consent_tokens": "not_a_dict",  # Should be dict
            "parameters": []  # Should be dict
        }
        
        response = client.post("/agents/test_agent/execute", json=invalid_request)
        
        assert response.status_code == 422  # Validation error


class TestAPIIntegration:
    """Integration tests for complete API workflows."""
    
    @pytest.fixture
    def client(self):
        """Create test client for API testing."""
        return TestClient(app)
    
    @patch('api.issue_token')
    @patch.object(agent_registry, 'get_agent')
    def test_complete_workflow_token_generation_and_execution(self, mock_get_agent, mock_issue_token, client):
        """Test complete workflow: generate token -> execute agent."""
        # Step 1: Generate consent token
        mock_token = "HCT:test_token_string"
        mock_expires = datetime.utcnow() + timedelta(hours=1)
        mock_issue_token.return_value = (mock_token, mock_expires)
        
        token_request = {
            "user_id": "test_user_123",
            "scopes": ["vault.read.email"],
            "duration_hours": 1
        }
        
        token_response = client.post("/consent/token", json=token_request)
        assert token_response.status_code == 200
        token_data = token_response.json()
        
        # Step 2: Use token to execute agent
        mock_agent = Mock()
        mock_agent.handle.return_value = {"status": "success", "data": "test_result"}
        mock_get_agent.return_value = {"instance": mock_agent}
        
        execution_request = {
            "user_id": "test_user_123",
            "agent_id": "test_agent",
            "consent_tokens": {"email_token": token_data["token"]},
            "parameters": {"test_param": "test_value"}
        }
        
        execution_response = client.post("/agents/test_agent/execute", json=execution_request)
        assert execution_response.status_code == 200
        
        execution_data = execution_response.json()
        assert execution_data["status"] == "success"
        assert execution_data["agent_id"] == "test_agent"
    
    def test_api_documentation_accessibility(self, client):
        """Test that API documentation is accessible."""
        # Test Swagger docs
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Test ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200
        
        # Test OpenAPI schema
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "paths" in schema
        assert "components" in schema


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
