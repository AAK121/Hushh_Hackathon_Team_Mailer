# hushh_mcp/agents/relationship_memory/index.py

"""
Relationship Memory Agent - Main Entry Point
AI-powered agent for managing contacts, memories, and reminders with full MCP compliance.
"""

import os
import sys
import uuid
from typing import Dict, Any, Optional, Union
from dotenv import load_dotenv

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from hushh_mcp.consent.token import validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.agents.relationship_memory.manifest import manifest

# Import the LangGraph agent
try:
    from hushh_mcp.agents.relationship_memory.langgraph_agent import RelationshipMemoryAgent
except ImportError as e:
    print(f"Warning: Could not import LangGraph agent: {e}")
    RelationshipMemoryAgent = None

class RelationshipMemoryAgentHandler:
    """
    Main handler for the Relationship Memory Agent.
    Validates tokens and delegates to the LangGraph implementation.
    """
    
    def __init__(self):
        self.agent_id = manifest["id"]
        self.required_scopes = manifest["scopes"]
        self.langgraph_agent = None
        self._current_user_id = None
        self._current_vault_key = None
        
        # Load environment variables from main project folder
        main_env_path = os.path.join(project_root, '.env')
        load_dotenv(main_env_path)
        
    def _validate_permissions(self, user_id: str, token: str, required_scope: ConsentScope) -> tuple[bool, str]:
        """Validate token and permissions for the given scope"""
        try:
            valid, reason, parsed = validate_token(token, expected_scope=required_scope)
            
            if not valid:
                return False, f"❌ Invalid token: {reason}"
                
            if parsed.user_id != user_id:
                return False, "❌ Token user mismatch"
                
            return True, "✅ Token validated successfully"
            
        except Exception as e:
            return False, f"❌ Token validation error: {str(e)}"
    
    def _initialize_agent(self, user_id: str, vault_key: str) -> bool:
        """Initialize the LangGraph agent if not already initialized with the same parameters"""
        try:
            if RelationshipMemoryAgent is None:
                return False
            
            # Only initialize if not already initialized with the same parameters
            if (self.langgraph_agent is None or 
                self._current_user_id != user_id or 
                self._current_vault_key != vault_key):
                
                self.langgraph_agent = RelationshipMemoryAgent(
                    user_id=user_id,
                    vault_key=vault_key
                )
                self._current_user_id = user_id
                self._current_vault_key = vault_key
                
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize LangGraph agent: {e}")
            return False
    
    def handle(self, user_id: str, tokens: Dict[str, str], user_input: str, vault_key: Optional[Union[str, bytes]] = None) -> Dict[str, Any]:
        """
        Main handler method for processing user requests.
        
        Args:
            user_id: User identifier
            tokens: Dictionary of consent tokens by scope
            user_input: Natural language input from user
            vault_key: Optional vault encryption key (bytes or string)
            
        Returns:
            Dictionary with agent response
        """
        
        # Generate vault key if not provided
        if not vault_key:
            vault_key = os.urandom(32)
        elif isinstance(vault_key, str):
            vault_key = vault_key.encode() if len(vault_key) < 64 else bytes.fromhex(vault_key)
        # If it's already bytes, use as-is
        
        # Validate at least one token
        if not tokens:
            return {
                "status": "error",
                "message": "❌ No consent tokens provided",
                "agent_id": self.agent_id
            }
        
        # Validate required permissions
        validated_scopes = []
        for scope_str, token in tokens.items():
            try:
                # Convert string to ConsentScope enum
                scope = ConsentScope(scope_str) if isinstance(scope_str, str) else scope_str
                valid, reason = self._validate_permissions(user_id, token, scope)
                
                if valid:
                    validated_scopes.append(scope)
                else:
                    print(f"⚠️ Scope {scope.value} validation failed: {reason}")
                    
            except Exception as e:
                print(f"⚠️ Error validating scope {scope_str}: {e}")
        
        if not validated_scopes:
            return {
                "status": "error", 
                "message": "❌ No valid tokens found",
                "agent_id": self.agent_id
            }
        
        # Initialize and run the LangGraph agent
        if not self._initialize_agent(user_id, vault_key):
            return {
                "status": "error",
                "message": "❌ Failed to initialize agent. Please check dependencies.",
                "agent_id": self.agent_id,
                "fallback": "Basic agent functionality not available"
            }
        
        try:
            # Process the user input using LangGraph agent
            result = self.langgraph_agent.process_input(user_input)
            
            # Add metadata
            result.update({
                "agent_id": self.agent_id,
                "user_id": user_id,
                "validated_scopes": [scope.value for scope in validated_scopes]
            })
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Agent execution failed: {str(e)}",
                "agent_id": self.agent_id,
                "user_id": user_id
            }

def run_agent(user_id: str = None, vault_key: str = None, demo_mode: bool = True) -> Dict[str, Any]:
    """
    Standalone function to run the agent (for testing/demo purposes)
    
    Args:
        user_id: Optional user ID (generates random if not provided)
        vault_key: Optional vault key (generates random if not provided)  
        demo_mode: Whether to run in demo mode with mock tokens
        
    Returns:
        Agent execution result
    """
    
    if not user_id:
        user_id = f"demo_user_{str(uuid.uuid4())[:8]}"
    
    if not vault_key:
        vault_key = os.urandom(32).hex()
    
    print(f"🚀 Running Relationship Memory Agent for user: {user_id}")
    
    # Initialize handler
    handler = RelationshipMemoryAgentHandler()
    
    if demo_mode:
        # In demo mode, create mock tokens (bypass actual token validation)
        print("📝 Running in demo mode - using mock tokens")
        
        # Mock tokens for demo
        mock_tokens = {
            ConsentScope.VAULT_READ_CONTACTS.value: "mock_token_read_contacts",
            ConsentScope.VAULT_WRITE_CONTACTS.value: "mock_token_write_contacts",
            ConsentScope.VAULT_READ_MEMORY.value: "mock_token_read_memory",
            ConsentScope.VAULT_WRITE_MEMORY.value: "mock_token_write_memory"
        }
        
        # Override validation for demo
        handler._validate_permissions = lambda uid, token, scope: (True, "Demo mode")
        
        # Test inputs
        test_inputs = [
            "add alok as a contact with email 23b2223@iitb.ac.in",
            "show my contacts",
            "remember that I met sarah at the conference"
        ]
        
        results = []
        for user_input in test_inputs:
            print(f"\n🔍 Processing: {user_input}")
            result = handler.handle(user_id, mock_tokens, user_input, vault_key)
            print(f"📋 Result: {result}")
            results.append(result)
        
        return {"demo_results": results}
    
    else:
        return {
            "status": "ready",
            "message": "Agent initialized and ready for use",
            "agent_id": handler.agent_id,
            "required_scopes": [scope.value for scope in handler.required_scopes]
        }

if __name__ == "__main__":
    # Run the agent in demo mode
    result = run_agent(demo_mode=True)
    print(f"\n🎉 Final result: {result}")
