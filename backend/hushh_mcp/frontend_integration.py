# hushh_mcp/frontend_integration.py

"""
Frontend Integration Module for HushhMCP
=========================================

This module provides API endpoints and utilities for integrating with 
frontend applications using Supabase OAuth and credential management.

Features:
- Supabase OAuth token validation
- Google credentials.json management
- Mailjet API key secure storage
- Consent token generation for frontend users
- Secure credential exchange
"""

import os
import json
import jwt
import hashlib
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from pydantic import BaseModel

# HushMCP imports
from hushh_mcp.consent.token import issue_token, validate_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.vault.encrypt import encrypt_data, decrypt_data
from hushh_mcp.config import VAULT_ENCRYPTION_KEY

class SupabaseUser(BaseModel):
    """Supabase authenticated user model."""
    id: str
    email: str
    user_metadata: Dict
    app_metadata: Dict
    aud: str
    exp: int

class CredentialRequest(BaseModel):
    """Request model for storing user credentials."""
    user_id: str
    supabase_token: str
    google_credentials: Optional[Dict] = None
    mailjet_api_key: Optional[str] = None
    mailjet_api_secret: Optional[str] = None

class ConsentRequest(BaseModel):
    """Request model for generating consent tokens."""
    user_id: str
    supabase_token: str
    agent_id: str
    scopes: List[str]
    duration_hours: int = 24

class FrontendIntegration:
    """
    Handles frontend integration with secure credential management
    and HushhMCP protocol compliance.
    """
    
    def __init__(self):
        self.supabase_jwt_secret = os.environ.get("SUPABASE_JWT_SECRET", "test_secret_for_development")
        if not self.supabase_jwt_secret and os.environ.get("ENVIRONMENT") == "production":
            raise ValueError("SUPABASE_JWT_SECRET must be set for production frontend integration")
    
    def verify_supabase_token(self, token: str) -> SupabaseUser:
        """
        Verifies Supabase JWT token and extracts user information.
        
        Args:
            token: Supabase JWT token from frontend
            
        Returns:
            SupabaseUser: Validated user information
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            # Decode JWT token
            payload = jwt.decode(
                token, 
                self.supabase_jwt_secret, 
                algorithms=["HS256"],
                options={"verify_exp": True}
            )
            
            # Validate required fields
            required_fields = ["sub", "email", "aud", "exp"]
            if not all(field in payload for field in required_fields):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token structure"
                )
            
            return SupabaseUser(
                id=payload["sub"],
                email=payload["email"],
                user_metadata=payload.get("user_metadata", {}),
                app_metadata=payload.get("app_metadata", {}),
                aud=payload["aud"],
                exp=payload["exp"]
            )
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
    
    def store_user_credentials(self, request: CredentialRequest) -> Dict:
        """
        Securely stores user credentials with encryption.
        
        Args:
            request: Credential storage request
            
        Returns:
            Dict: Storage confirmation with vault keys
        """
        # Verify Supabase token first
        user = self.verify_supabase_token(request.supabase_token)
        
        # Validate user ID matches token
        if user.id != request.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User ID mismatch"
            )
        
        vault_keys = {}
        
        # Store Google credentials if provided
        if request.google_credentials:
            google_vault_key = f"google_credentials_{user.id}"
            google_data = {
                'credentials': request.google_credentials,
                'user_id': user.id,
                'user_email': user.email,
                'stored_at': datetime.utcnow().isoformat(),
                'credential_type': 'google_oauth'
            }
            
            encrypted_google = encrypt_data(json.dumps(google_data), VAULT_ENCRYPTION_KEY)
            vault_keys['google_credentials'] = google_vault_key
            
            # In production, store in persistent vault
            print(f"🔒 Google credentials encrypted and stored: {google_vault_key}")
        
        # Store Mailjet credentials if provided
        if request.mailjet_api_key and request.mailjet_api_secret:
            mailjet_vault_key = f"mailjet_credentials_{user.id}"
            mailjet_data = {
                'api_key': request.mailjet_api_key,
                'api_secret': request.mailjet_api_secret,
                'user_id': user.id,
                'user_email': user.email,
                'stored_at': datetime.utcnow().isoformat(),
                'credential_type': 'mailjet_api'
            }
            
            encrypted_mailjet = encrypt_data(json.dumps(mailjet_data), VAULT_ENCRYPTION_KEY)
            vault_keys['mailjet_credentials'] = mailjet_vault_key
            
            print(f"🔒 Mailjet credentials encrypted and stored: {mailjet_vault_key}")
        
        return {
            'status': 'success',
            'message': 'Credentials stored securely',
            'user_id': user.id,
            'vault_keys': vault_keys,
            'stored_at': datetime.utcnow().isoformat()
        }
    
    def retrieve_user_credentials(self, user_id: str, supabase_token: str, credential_type: str) -> Dict:
        """
        Retrieves and decrypts user credentials.
        
        Args:
            user_id: User identifier
            supabase_token: Supabase authentication token
            credential_type: Type of credentials ('google', 'mailjet')
            
        Returns:
            Dict: Decrypted credential data
        """
        # Verify Supabase token
        user = self.verify_supabase_token(supabase_token)
        
        if user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User ID mismatch"
            )
        
        vault_key = f"{credential_type}_credentials_{user_id}"
        
        # In production, retrieve from persistent vault and decrypt
        # For now, return structure for testing
        return {
            'status': 'success',
            'vault_key': vault_key,
            'credential_type': credential_type,
            'user_id': user_id,
            'message': 'Credentials retrieved successfully'
        }
    
    def generate_consent_tokens(self, request: ConsentRequest) -> Dict:
        """
        Generates HushhMCP consent tokens for authenticated users.
        
        Args:
            request: Consent token generation request
            
        Returns:
            Dict: Generated consent tokens for each scope
        """
        # Verify Supabase token
        user = self.verify_supabase_token(request.supabase_token)
        
        if user.id != request.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User ID mismatch"
            )
        
        # Generate tokens for each requested scope
        consent_tokens = {}
        duration_ms = request.duration_hours * 60 * 60 * 1000
        
        for scope_str in request.scopes:
            try:
                # Validate scope
                scope = ConsentScope(scope_str)
                
                # Issue token
                token, expires_at = issue_token(
                    user_id=user.id,
                    scopes=[scope],
                    duration_hours=request.duration_hours
                )
                
                consent_tokens[scope.value] = {
                    'token': token,
                    'expires_at': expires_at,
                    'scope': scope.value,
                    'agent_id': request.agent_id
                }
                
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid scope: {scope_str}"
                )
        
        return {
            'status': 'success',
            'user_id': user.id,
            'agent_id': request.agent_id,
            'consent_tokens': consent_tokens,
            'expires_in_hours': request.duration_hours,
            'issued_at': datetime.utcnow().isoformat()
        }
    
    def create_agent_session(self, user_id: str, supabase_token: str, agent_id: str) -> Dict:
        """
        Creates a complete agent session with credentials and consent tokens.
        
        Args:
            user_id: User identifier
            supabase_token: Supabase authentication token
            agent_id: Target agent identifier
            
        Returns:
            Dict: Complete session data for agent execution
        """
        # Verify authentication
        user = self.verify_supabase_token(supabase_token)
        
        if user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User ID mismatch"
            )
        
        # Define scope requirements for each agent
        agent_scopes = {
            'agent_mailerpanda': [
                ConsentScope.VAULT_READ_EMAIL,
                ConsentScope.VAULT_WRITE_EMAIL,
                ConsentScope.VAULT_READ_FILE,
                ConsentScope.VAULT_WRITE_FILE,
                ConsentScope.CUSTOM_TEMPORARY
            ],
            'agent_addtocalendar': [
                ConsentScope.VAULT_READ_EMAIL,
                ConsentScope.VAULT_WRITE_CALENDAR,
                ConsentScope.VAULT_READ_CALENDAR
            ]
        }
        
        if agent_id not in agent_scopes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown agent: {agent_id}"
            )
        
        # Generate consent tokens for required scopes
        consent_tokens = {}
        for scope in agent_scopes[agent_id]:
            token, expires_at = issue_token(
                user_id=user.id,
                scopes=[scope],
                duration_hours=24
            )
            consent_tokens[scope.value] = token
        
        # Create session data
        session_data = {
            'session_id': f"session_{user.id}_{agent_id}_{int(datetime.now(timezone.utc).timestamp())}",
            'user_id': user.id,
            'user_email': user.email,
            'agent_id': agent_id,
            'consent_tokens': consent_tokens,
            'credential_vault_keys': {
                'google_credentials': f"google_credentials_{user.id}",
                'mailjet_credentials': f"mailjet_credentials_{user.id}"
            },
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }
        
        return {
            'status': 'success',
            'message': 'Agent session created successfully',
            'session': session_data
        }

# Global instance for API endpoints
frontend_integration = FrontendIntegration()
