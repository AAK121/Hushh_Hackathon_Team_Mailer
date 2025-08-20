# hushh_mcp/agents/chandufinance/index.py

"""
Personal Financial Advisor - HushhMCP Compliant AI-Powered Wealth Management Agent
==================================================================================

A revolutionary personal financial agent that combines traditional financial analysis
with AI-powered personalized advice. Learns your income, budget, goals, and risk 
tolerance to provide tailored investment recommendations using LLM insights.

FEATURES:
- HushhMCP compliant consent token validation
- Encrypted vault storage for all personal financial data
- LLM-powered personalized investment advice
- Comprehensive personal finance profile management
- Goal-based investment planning with timelines
- Risk-appropriate position sizing recommendations
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path

# LLM Integration
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# HushhMCP Core Imports
from hushh_mcp.consent.token import validate_token
from hushh_mcp.vault.encrypt import encrypt_data, decrypt_data
from hushh_mcp.types import ConsentScope, UserID, HushhConsentToken, EncryptedPayload
from hushh_mcp.constants import ConsentScope
from hushh_mcp.config import SECRET_KEY

# Import manifest
from hushh_mcp.agents.chandufinance.manifest import manifest


class PersonalFinancialProfile:
    """User's comprehensive personal financial profile stored in encrypted vault."""
    
    def __init__(self, data: Dict[str, Any] = None):
        self.data = data or {
            'personal_info': {},
            'financial_info': {},
            'goals': [],
            'preferences': {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    
    # Personal Information Properties
    @property
    def full_name(self) -> str:
        return self.data['personal_info'].get('full_name', '')
    
    @property
    def age(self) -> int:
        return self.data['personal_info'].get('age', 30)
    
    @property
    def occupation(self) -> str:
        return self.data['personal_info'].get('occupation', '')
    
    @property
    def family_status(self) -> str:
        return self.data['personal_info'].get('family_status', 'single')
    
    @property
    def dependents(self) -> int:
        return self.data['personal_info'].get('dependents', 0)
    
    # Financial Information Properties  
    @property
    def monthly_income(self) -> float:
        return self.data['financial_info'].get('monthly_income', 0.0)
    
    @property
    def monthly_expenses(self) -> float:
        return self.data['financial_info'].get('monthly_expenses', 0.0)
    
    @property
    def current_savings(self) -> float:
        return self.data['financial_info'].get('current_savings', 0.0)
    
    @property
    def current_debt(self) -> float:
        return self.data['financial_info'].get('current_debt', 0.0)
    
    @property
    def investment_budget(self) -> float:
        return self.data['financial_info'].get('investment_budget', 0.0)
    
    @property
    def detailed_budget(self) -> Dict[str, float]:
        return self.data['financial_info'].get('detailed_budget', {})
    
    # Calculated Properties
    @property
    def savings_rate(self) -> float:
        if self.monthly_income > 0:
            return (self.monthly_income - self.monthly_expenses) / self.monthly_income
        return 0.0
    
    @property
    def debt_to_income_ratio(self) -> float:
        if self.monthly_income > 0:
            return self.current_debt / (self.monthly_income * 12)
        return 0.0
    
    # Preferences Properties
    @property
    def risk_tolerance(self) -> str:
        return self.data['preferences'].get('risk_tolerance', 'moderate')
    
    @property
    def investment_experience(self) -> str:
        return self.data['preferences'].get('investment_experience', 'beginner')
    
    @property
    def time_horizon(self) -> str:
        return self.data['preferences'].get('time_horizon', 'long_term')
    
    @property
    def investment_goals(self) -> List[Dict]:
        return self.data.get('goals', [])
    
    def update_personal_info(self, **kwargs):
        """Update personal information."""
        self.data['personal_info'].update(kwargs)
        self.data['updated_at'] = datetime.now().isoformat()
    
    def update_financial_info(self, **kwargs):
        """Update financial information."""
        self.data['financial_info'].update(kwargs)
        self.data['updated_at'] = datetime.now().isoformat()
    
    def update_preferences(self, **kwargs):
        """Update investment preferences.""" 
        self.data['preferences'].update(kwargs)
        self.data['updated_at'] = datetime.now().isoformat()
    
    def add_goal(self, goal_data: Dict[str, Any]):
        """Add a new financial goal."""
        goal_data['id'] = str(uuid.uuid4())
        goal_data['created_at'] = datetime.now().isoformat()
        self.data['goals'].append(goal_data)
        self.data['updated_at'] = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for storage."""
        return self.data


class PersonalFinancialAgent:
    """
    HushhMCP Compliant Personal Financial Advisor Agent
    
    This agent provides AI-powered personalized financial advice while maintaining
    strict compliance with HushhMCP consent and vault security protocols.
    """
    
    def __init__(self):
        self.agent_id = manifest["id"]
        self.version = manifest["version"] 
        self.required_scopes = manifest["required_scopes"]
        
        # Initialize LLM if available
        self.llm = None
        if LLM_AVAILABLE and os.getenv('GEMINI_API_KEY'):
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    google_api_key=os.getenv('GEMINI_API_KEY'),
                    temperature=0.7
                )
            except Exception as e:
                print(f"⚠️ LLM initialization failed: {e}")
    
    def handle(self, **kwargs) -> Dict[str, Any]:
        """Main entry point for the personal financial agent."""
        try:
            # Extract required parameters
            user_id = kwargs.get('user_id')
            token = kwargs.get('token')
            parameters = kwargs.get('parameters', {})
            
            if not user_id or not token:
                return self._error_response("Missing required parameters: user_id and token")
            
            # Validate consent token with proper HushhMCP validation
            is_valid, reason, parsed_token = validate_token(token)
            if not is_valid:
                return self._error_response(f"Token validation failed: {reason}")
            
            # Verify user ID matches token
            if parsed_token.user_id != user_id:
                return self._error_response("User ID mismatch with token")
            
            # Get command from parameters
            command = parameters.get('command', 'setup_profile')
            
            # Validate scope for the requested command
            required_scope = self._get_required_scope(command)
            if not self._check_scope_permission(parsed_token, required_scope):
                return self._error_response(f"Insufficient permissions for {command}. Required: {required_scope}")
            
            # Route to appropriate handler
            return self._route_command(user_id, command, parameters, parsed_token)
                
        except Exception as e:
            return self._error_response(f"Agent execution failed: {str(e)}")
    
    def _get_required_scope(self, command: str) -> str:
        """Get required consent scope for each command."""
        scope_mapping = {
            # Personal profile management - requires personal data access
            'setup_profile': ConsentScope.VAULT_WRITE_FILE.value,
            'update_personal_info': ConsentScope.VAULT_WRITE_FILE.value,
            'update_income': ConsentScope.VAULT_WRITE_FILE.value,
            'set_budget': ConsentScope.VAULT_WRITE_FILE.value,
            'add_goal': ConsentScope.VAULT_WRITE_FILE.value,
            'view_profile': ConsentScope.VAULT_READ_FILE.value,
            
            # Financial analysis - requires finance data access
            'personal_stock_analysis': ConsentScope.VAULT_READ_FINANCE.value,
            'portfolio_review': ConsentScope.VAULT_READ_FINANCE.value,
            'goal_progress_check': ConsentScope.VAULT_READ_FILE.value,
            
            # Education features - minimal access needed
            'explain_like_im_new': ConsentScope.VAULT_READ_FILE.value,
            'investment_education': ConsentScope.VAULT_READ_FILE.value,
            'behavioral_coaching': ConsentScope.VAULT_READ_FILE.value,
        }
        return scope_mapping.get(command, ConsentScope.VAULT_READ_FILE.value)
    
    def _check_scope_permission(self, token: HushhConsentToken, required_scope: str) -> bool:
        """Check if token has required scope permission."""
        # Handle both single scope and comma-separated scopes
        if isinstance(token.scope, str):
            token_scopes = token.scope.split(',')
        else:
            token_scopes = [str(token.scope)]
        
        # Check if the required scope or a broader write scope is present
        return (required_scope in token_scopes or 
                ConsentScope.VAULT_WRITE_FILE.value in token_scopes or
                ConsentScope.VAULT_READ_FINANCE.value in token_scopes)
    
    def _route_command(self, user_id: str, command: str, parameters: Dict[str, Any], token: HushhConsentToken) -> Dict[str, Any]:
        """Route commands to appropriate handlers."""
        
        # Personal Information Management Commands
        if command == 'setup_profile':
            return self._setup_profile(user_id, parameters, token)
        elif command == 'update_personal_info':
            return self._update_personal_info(user_id, parameters, token)
        elif command == 'update_income':
            return self._update_income(user_id, parameters, token)
        elif command == 'set_budget':
            return self._set_budget(user_id, parameters, token)
        elif command == 'add_goal':
            return self._add_goal(user_id, parameters, token)
        elif command == 'view_profile':
            return self._view_profile(user_id, token)
            
        # Personalized Analysis Commands
        elif command == 'personal_stock_analysis':
            return self._personal_stock_analysis(user_id, parameters, token)
        elif command == 'portfolio_review':
            return self._portfolio_review(user_id, parameters, token)
        elif command == 'goal_progress_check':
            return self._goal_progress_check(user_id, parameters, token)
            
        # Education & Coaching Commands
        elif command == 'explain_like_im_new':
            return self._explain_like_im_new(user_id, parameters, token)
        elif command == 'investment_education':
            return self._investment_education(user_id, parameters, token)
        elif command == 'behavioral_coaching':
            return self._behavioral_coaching(user_id, parameters, token)
        
        else:
            return self._error_response(f"Unknown command: {command}")
    
    def _get_vault_path(self, user_id: str, filename: str) -> str:
        """Get secure vault path for user data."""
        vault_dir = Path(f"vault/{user_id}/finance")
        vault_dir.mkdir(parents=True, exist_ok=True)
        return str(vault_dir / filename)
    
    def _save_to_vault(self, user_id: str, filename: str, data: Dict[str, Any], token: HushhConsentToken) -> bool:
        """Save data to encrypted vault storage."""
        try:
            # Convert data to JSON string
            data_str = json.dumps(data, indent=2)
            
            # Encrypt the data
            encrypted_payload = encrypt_data(data_str, SECRET_KEY)
            
            # Save encrypted data to vault
            vault_path = self._get_vault_path(user_id, filename)
            with open(vault_path, 'w') as f:
                json.dump({
                    'ciphertext': encrypted_payload.ciphertext,
                    'iv': encrypted_payload.iv,
                    'tag': encrypted_payload.tag,
                    'encoding': encrypted_payload.encoding,
                    'algorithm': encrypted_payload.algorithm,
                    'metadata': {
                        'agent_id': self.agent_id,
                        'user_id': user_id,
                        'scope': token.scope,
                        'created_at': datetime.now().isoformat(),
                        'data_type': 'personal_financial_profile'
                    }
                }, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ Vault save failed: {e}")
            return False
    
    def _load_from_vault(self, user_id: str, filename: str) -> Optional[Dict[str, Any]]:
        """Load data from encrypted vault storage."""
        try:
            vault_path = self._get_vault_path(user_id, filename)
            
            if not os.path.exists(vault_path):
                return None
            
            # Load encrypted data
            with open(vault_path, 'r') as f:
                encrypted_data = json.load(f)
            
            # Create EncryptedPayload object
            payload = EncryptedPayload(
                ciphertext=encrypted_data['ciphertext'],
                iv=encrypted_data['iv'], 
                tag=encrypted_data['tag'],
                encoding=encrypted_data['encoding'],
                algorithm=encrypted_data['algorithm']
            )
            
            # Decrypt the data
            decrypted_str = decrypt_data(payload, SECRET_KEY)
            return json.loads(decrypted_str)
            
        except Exception as e:
            print(f"❌ Vault load failed: {e}")
            return None
    
    def _load_user_profile(self, user_id: str) -> Optional[PersonalFinancialProfile]:
        """Load user's financial profile from encrypted vault."""
        profile_data = self._load_from_vault(user_id, 'financial_profile.json')
        if profile_data:
            return PersonalFinancialProfile(profile_data)
        return None
    
    def _save_user_profile(self, user_id: str, profile: PersonalFinancialProfile, token: HushhConsentToken) -> bool:
        """Save user's financial profile to encrypted vault."""
        return self._save_to_vault(user_id, 'financial_profile.json', profile.to_dict(), token)
    
    # ==================== PERSONAL INFORMATION MANAGEMENT ====================
    
    def _setup_profile(self, user_id: str, parameters: Dict[str, Any], token: HushhConsentToken) -> Dict[str, Any]:
        """Set up comprehensive personal financial profile with vault storage."""
        try:
            # Create new profile or load existing
            profile = self._load_user_profile(user_id) or PersonalFinancialProfile()
            
            # Update personal information
            personal_info = {
                'full_name': parameters.get('full_name', ''),
                'age': int(parameters.get('age', 30)),
                'occupation': parameters.get('occupation', ''),
                'family_status': parameters.get('family_status', 'single'),
                'dependents': int(parameters.get('dependents', 0))
            }
            profile.update_personal_info(**personal_info)
            
            # Update financial information
            financial_info = {
                'monthly_income': float(parameters.get('monthly_income', parameters.get('income', 0))),
                'monthly_expenses': float(parameters.get('monthly_expenses', parameters.get('expenses', 0))),
                'current_savings': float(parameters.get('current_savings', 0)),
                'current_debt': float(parameters.get('current_debt', 0)),
                'investment_budget': float(parameters.get('investment_budget', 0))
            }
            profile.update_financial_info(**financial_info)
            
            # Update preferences
            preferences = {
                'risk_tolerance': parameters.get('risk_tolerance', parameters.get('risk', 'moderate')),
                'investment_experience': parameters.get('investment_experience', parameters.get('experience', 'beginner')),
                'time_horizon': parameters.get('time_horizon', 'long_term')
            }
            profile.update_preferences(**preferences)
            
            # Save to encrypted vault
            if not self._save_user_profile(user_id, profile, token):
                return self._error_response("Failed to save profile to vault")
            
            # Generate personalized welcome message using LLM
            welcome_message = self._generate_welcome_message(profile)
            
            return {
                'status': 'success',
                'agent_id': self.agent_id,
                'user_id': user_id,
                'message': 'Personal financial profile created successfully',
                'profile_summary': self._summarize_profile(profile),
                'welcome_message': welcome_message,
                'next_steps': self._suggest_next_steps(profile),
                'vault_stored': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._error_response(f"Profile setup failed: {str(e)}")
    
    def _update_personal_info(self, user_id: str, parameters: Dict[str, Any], token: HushhConsentToken) -> Dict[str, Any]:
        """Update personal information in encrypted vault."""
        try:
            profile = self._load_user_profile(user_id)
            if not profile:
                return self._error_response("No profile found. Please setup profile first.")
            
            # Update personal information fields
            updates = {}
            for field in ['full_name', 'age', 'occupation', 'family_status', 'dependents']:
                if field in parameters:
                    if field in ['age', 'dependents']:
                        updates[field] = int(parameters[field])
                    else:
                        updates[field] = parameters[field]
            
            if updates:
                profile.update_personal_info(**updates)
                
                # Save to vault
                if not self._save_user_profile(user_id, profile, token):
                    return self._error_response("Failed to save updates to vault")
                
                return {
                    'status': 'success',
                    'agent_id': self.agent_id,
                    'user_id': user_id,
                    'message': 'Personal information updated successfully',
                    'updated_fields': list(updates.keys()),
                    'vault_stored': True,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return self._error_response("No valid fields provided for update")
                
        except Exception as e:
            return self._error_response(f"Personal info update failed: {str(e)}")
    
    def _view_profile(self, user_id: str, token: HushhConsentToken) -> Dict[str, Any]:
        """View complete personal financial profile from vault."""
        try:
            profile = self._load_user_profile(user_id)
            if not profile:
                return self._error_response("No profile found. Please setup profile first.")
            
            return {
                'status': 'success',
                'agent_id': self.agent_id,
                'user_id': user_id,
                'personal_info': {
                    'full_name': profile.full_name,
                    'age': profile.age,
                    'occupation': profile.occupation,
                    'family_status': profile.family_status,
                    'dependents': profile.dependents
                },
                'financial_info': {
                    'monthly_income': profile.monthly_income,
                    'monthly_expenses': profile.monthly_expenses,
                    'current_savings': profile.current_savings,
                    'current_debt': profile.current_debt,
                    'investment_budget': profile.investment_budget,
                    'savings_rate': profile.savings_rate,
                    'debt_to_income_ratio': profile.debt_to_income_ratio
                },
                'preferences': {
                    'risk_tolerance': profile.risk_tolerance,
                    'investment_experience': profile.investment_experience,
                    'time_horizon': profile.time_horizon
                },
                'goals': profile.investment_goals,
                'profile_health_score': self._calculate_profile_health_score(profile),
                'vault_source': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._error_response(f"Profile view failed: {str(e)}")
    
    def _update_income(self, user_id: str, parameters: Dict[str, Any], token: HushhConsentToken) -> Dict[str, Any]:
        """Update user's monthly income in vault."""
        try:
            new_income = parameters.get('income')
            if not new_income:
                return self._error_response("Missing required parameter: income")
            
            profile = self._load_user_profile(user_id)
            if not profile:
                return self._error_response("No profile found. Please setup profile first.")
            
            old_income = profile.monthly_income
            
            # Update financial info
            profile.update_financial_info(monthly_income=float(new_income))
            
            # Recalculate investment budget if needed
            new_surplus = profile.monthly_income - profile.monthly_expenses
            if profile.investment_budget > new_surplus * 0.8:  # Keep 20% buffer
                profile.update_financial_info(investment_budget=max(new_surplus * 0.5, 100))
            
            # Save to vault
            if not self._save_user_profile(user_id, profile, token):
                return self._error_response("Failed to save income update to vault")
            
            return {
                'status': 'success',
                'agent_id': self.agent_id,
                'user_id': user_id,
                'message': 'Income updated successfully',
                'old_income': old_income,
                'new_income': profile.monthly_income,
                'new_savings_rate': profile.savings_rate * 100,
                'updated_investment_budget': profile.investment_budget,
                'vault_stored': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._error_response(f"Income update failed: {str(e)}")
    
    def _set_budget(self, user_id: str, parameters: Dict[str, Any], token: HushhConsentToken) -> Dict[str, Any]:
        """Set detailed budget categories in vault."""
        try:
            profile = self._load_user_profile(user_id)
            if not profile:
                return self._error_response("No profile found. Please setup profile first.")
            
            # Extract budget categories
            budget_categories = {
                'housing': float(parameters.get('housing', 0)),
                'food': float(parameters.get('food', 0)),
                'transportation': float(parameters.get('transportation', 0)),
                'utilities': float(parameters.get('utilities', 0)),
                'healthcare': float(parameters.get('healthcare', 0)),
                'entertainment': float(parameters.get('entertainment', 0)),
                'personal_care': float(parameters.get('personal_care', 0)),
                'debt_payments': float(parameters.get('debt_payments', 0)),
                'other': float(parameters.get('other', 0))
            }
            
            # Calculate total expenses
            total_expenses = sum(budget_categories.values())
            
            # Update profile with detailed budget
            profile.update_financial_info(
                detailed_budget=budget_categories,
                monthly_expenses=total_expenses
            )
            
            # Save to vault
            if not self._save_user_profile(user_id, profile, token):
                return self._error_response("Failed to save budget to vault")
            
            # Generate budget analysis
            budget_analysis = self._analyze_budget(profile)
            
            return {
                'status': 'success',
                'agent_id': self.agent_id,
                'user_id': user_id,
                'message': 'Budget updated successfully',
                'detailed_budget': budget_categories,
                'total_expenses': total_expenses,
                'savings_rate': profile.savings_rate * 100,
                'budget_analysis': budget_analysis,
                'vault_stored': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._error_response(f"Budget setup failed: {str(e)}")
    
    def _add_goal(self, user_id: str, parameters: Dict[str, Any], token: HushhConsentToken) -> Dict[str, Any]:
        """Add an investment goal to user's profile in vault."""
        try:
            goal_name = parameters.get('goal_name')
            target_amount = parameters.get('target_amount')
            target_date = parameters.get('target_date')
            priority = parameters.get('priority', 'medium')
            
            if not all([goal_name, target_amount, target_date]):
                return self._error_response("Missing required parameters: goal_name, target_amount, target_date")
            
            profile = self._load_user_profile(user_id)
            if not profile:
                return self._error_response("No profile found. Please setup profile first.")
            
            # Create goal data
            goal_data = {
                'name': goal_name,
                'target_amount': float(target_amount),
                'target_date': target_date,
                'priority': priority,
                'description': parameters.get('description', '')
            }
            
            # Add goal to profile
            profile.add_goal(goal_data)
            
            # Save to vault
            if not self._save_user_profile(user_id, profile, token):
                return self._error_response("Failed to save goal to vault")
            
            # Calculate goal feasibility
            goal_analysis = self._analyze_goal_feasibility(goal_data, profile)
            
            return {
                'status': 'success',
                'agent_id': self.agent_id,
                'user_id': user_id,
                'message': f'Goal "{goal_name}" added successfully',
                'goal_details': goal_data,
                'goal_analysis': goal_analysis,
                'vault_stored': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._error_response(f"Goal addition failed: {str(e)}")
    
    # ==================== PERSONALIZED ANALYSIS ====================
    
    def _personal_stock_analysis(self, user_id: str, parameters: Dict[str, Any], token: HushhConsentToken) -> Dict[str, Any]:
        """Provide personalized stock analysis based on user's financial profile."""
        try:
            ticker = parameters.get('ticker')
            if not ticker:
                return self._error_response("Missing required parameter: ticker")
            
            profile = self._load_user_profile(user_id)
            if not profile:
                return self._error_response("No profile found. Please setup profile first.")
            
            # Fetch financial data for the stock
            financial_data = self._fetch_financial_data(ticker)
            current_price = financial_data.get('current_price', 100.0)
            
            # Calculate position sizing based on user's profile
            position_analysis = self._calculate_position_size(current_price, profile)
            
            # Assess risk alignment with user profile
            risk_assessment = self._assess_stock_risk_for_user(ticker, profile)
            
            # Check goal alignment
            goal_alignment = self._check_goal_alignment(ticker, profile)
            
            # Generate LLM-powered personalized analysis
            personalized_analysis = self._generate_personal_stock_analysis(
                ticker, financial_data, current_price, profile
            )
            
            return {
                'status': 'success',
                'agent_id': self.agent_id,
                'user_id': user_id,
                'ticker': ticker,
                'current_price': current_price,
                'personalized_analysis': personalized_analysis,
                'position_sizing': position_analysis,
                'risk_assessment': risk_assessment,
                'goal_alignment': goal_alignment,
                'financial_data': financial_data,
                'user_context': {
                    'risk_tolerance': profile.risk_tolerance,
                    'experience_level': profile.investment_experience,
                    'investment_budget': profile.investment_budget,
                    'age': profile.age
                },
                'vault_source': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._error_response(f"Personal stock analysis failed: {str(e)}")
    
    def _portfolio_review(self, user_id: str, parameters: Dict[str, Any], token: HushhConsentToken) -> Dict[str, Any]:
        """Review user's portfolio alignment with their profile."""
        try:
            profile = self._load_user_profile(user_id)
            if not profile:
                return self._error_response("No profile found. Please setup profile first.")
            
            # For now, provide general portfolio guidance
            # In a real implementation, this would connect to brokerage APIs
            if self.llm:
                review_prompt = f"""
                Provide a portfolio review for this user:
                
                Profile:
                - Age: {profile.age}
                - Risk Tolerance: {profile.risk_tolerance}
                - Experience: {profile.investment_experience}
                - Monthly Investment Budget: ${profile.investment_budget}
                - Goals: {len(profile.investment_goals)} active goals
                
                Provide:
                1. Recommended asset allocation for their profile
                2. Diversification suggestions
                3. Risk assessment
                4. Rebalancing recommendations
                5. Next steps
                """
                
                response = self.llm.invoke(review_prompt)
                review_content = response.content
            else:
                review_content = "Portfolio review not available without LLM. Please configure Gemini API."
            
            return {
                'status': 'success',
                'agent_id': self.agent_id,
                'user_id': user_id,
                'portfolio_review': review_content,
                'recommended_allocation': {
                    'stocks': '70%' if profile.risk_tolerance == 'aggressive' else '60%' if profile.risk_tolerance == 'moderate' else '40%',
                    'bonds': '20%' if profile.risk_tolerance == 'aggressive' else '30%' if profile.risk_tolerance == 'moderate' else '50%',
                    'cash': '10%'
                },
                'action_items': [
                    'Review current allocation vs. recommended',
                    'Consider rebalancing if significantly off target',
                    'Evaluate individual holdings for quality'
                ],
                'vault_source': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._error_response(f"Portfolio review failed: {str(e)}")
    
    def _goal_progress_check(self, user_id: str, parameters: Dict[str, Any], token: HushhConsentToken) -> Dict[str, Any]:
        """Check progress toward investment goals."""
        try:
            profile = self._load_user_profile(user_id)
            if not profile:
                return self._error_response("No profile found. Please setup profile first.")
            
            if not profile.investment_goals:
                return self._error_response("No goals found. Please add goals first.")
            
            goal_progress = []
            
            for goal in profile.investment_goals:
                # Calculate progress (simplified - in real implementation would track actual investments)
                months_since_creation = 1  # Simplified
                estimated_saved = profile.investment_budget * months_since_creation
                progress_percentage = (estimated_saved / goal['target_amount']) * 100
                
                # Calculate timeline
                target_date = datetime.strptime(goal['target_date'], '%Y-%m-%d')
                months_remaining = (target_date.year - datetime.now().year) * 12 + (target_date.month - datetime.now().month)
                monthly_needed = (goal['target_amount'] - estimated_saved) / max(months_remaining, 1)
                
                goal_progress.append({
                    'goal_name': goal['name'],
                    'target_amount': goal['target_amount'],
                    'estimated_saved': estimated_saved,
                    'progress_percentage': min(progress_percentage, 100),
                    'months_remaining': months_remaining,
                    'monthly_needed': monthly_needed,
                    'on_track': monthly_needed <= profile.investment_budget,
                    'priority': goal['priority']
                })
            
            return {
                'status': 'success',
                'agent_id': self.agent_id,
                'user_id': user_id,
                'goal_progress': goal_progress,
                'overall_assessment': 'On track' if all(g['on_track'] for g in goal_progress) else 'Needs adjustment',
                'recommendations': [
                    'Consider increasing investment budget if possible',
                    'Review goal timelines for realism',
                    'Focus on highest priority goals first'
                ],
                'vault_source': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._error_response(f"Goal progress check failed: {str(e)}")
    
    # ===== LLM-POWERED ANALYSIS METHODS =====
    
    def _generate_personal_stock_analysis(self, ticker: str, financial_data: Dict, 
                                        current_price: float, profile: PersonalFinancialProfile) -> str:
        """Generate personalized stock analysis using LLM."""
        if not self.llm:
            return "LLM analysis not available. Please check Gemini API configuration."
        
        try:
            # Create context-rich prompt
            prompt = f"""
            You are a personal financial advisor analyzing {ticker} for a specific client.
            
            CLIENT PROFILE:
            - Age: {profile.age}
            - Monthly Income: ${profile.monthly_income:,.2f}
            - Monthly Expenses: ${profile.monthly_expenses:,.2f}
            - Savings Rate: {profile.savings_rate:.1%}
            - Investment Budget: ${profile.investment_budget:,.2f}
            - Risk Tolerance: {profile.risk_tolerance}
            - Experience Level: {profile.investment_experience}
            - Investment Goals: {profile.investment_goals}
            
            STOCK INFORMATION:
            - Ticker: {ticker}
            - Current Price: ${current_price}
            - Company: {financial_data.get('company_name', 'Unknown')}
            - Recent Revenue: ${financial_data.get('income_statements', [{}])[-1].get('revenue', 0):,.0f}
            
            Provide a personalized analysis that considers:
            1. Whether this stock fits their risk tolerance and experience level
            2. How it aligns with their investment goals
            3. Position sizing based on their budget
            4. Specific risks and opportunities for this individual
            5. Educational explanations appropriate for their experience level
            
            Format as a conversational, personalized recommendation.
            """
            
            response = self.llm.invoke(prompt)
            return response.content
            
        except Exception as e:
            return f"LLM analysis failed: {str(e)}"
    
    def _generate_welcome_message(self, profile: PersonalFinancialProfile) -> str:
        """Generate a personalized welcome message using LLM."""
        if not self.llm:
            return f"Welcome! Your financial profile has been set up with ${profile.monthly_income:,.2f} monthly income."
        
        try:
            prompt = f"""
            Create a warm, encouraging welcome message for a new user who just set up their financial profile.
            
            Their details:
            - Monthly Income: ${profile.monthly_income:,.2f}
            - Monthly Expenses: ${profile.monthly_expenses:,.2f}
            - Savings Rate: {profile.savings_rate:.1%}
            - Age: {profile.age}
            - Experience: {profile.investment_experience}
            - Risk Tolerance: {profile.risk_tolerance}
            
            The message should:
            1. Congratulate them on taking control of their finances
            2. Highlight positive aspects of their financial situation
            3. Provide encouragement if there are areas for improvement
            4. Set expectations for what we can help them achieve
            5. Be warm, personal, and motivating
            
            Keep it under 150 words and make it feel like a personal financial advisor speaking.
            """
            
            response = self.llm.invoke(prompt)
            return response.content
            
        except Exception as e:
            return f"Welcome! Your profile is set up. I'm here to help with your financial journey."
    
    # ===== UTILITY METHODS =====
    
    def _calculate_position_size(self, stock_price: float, profile: PersonalFinancialProfile) -> Dict[str, Any]:
        """Calculate appropriate position size based on user's budget and risk tolerance."""
        
        # Base allocation percentages by risk tolerance
        risk_allocations = {
            'conservative': 0.05,  # 5% of investment budget per stock
            'moderate': 0.10,      # 10% of investment budget per stock
            'aggressive': 0.15     # 15% of investment budget per stock
        }
        
        allocation_pct = risk_allocations.get(profile.risk_tolerance, 0.10)
        max_position_value = profile.investment_budget * allocation_pct
        max_shares = int(max_position_value / stock_price) if stock_price > 0 else 0
        
        return {
            'max_position_value': max_position_value,
            'max_shares': max_shares,
            'allocation_percentage': allocation_pct,
            'reasoning': f"Based on {profile.risk_tolerance} risk tolerance, allocating {allocation_pct:.1%} of investment budget"
        }
    
    def _fetch_financial_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch basic financial data for a ticker."""
        # Mock financial data for demonstration
        return {
            'ticker': ticker,
            'company_name': f"{ticker} Corporation",
            'income_statements': [
                {
                    'year': 2023,
                    'revenue': 1200000000,
                    'operating_income': 240000000,
                    'net_income': 180000000
                }
            ],
            'current_price': 100.0,
            'market_cap': 10000000000
        }
    
    def _summarize_profile(self, profile: PersonalFinancialProfile) -> Dict[str, Any]:
        """Create a summary of the user's financial profile."""
        return {
            'monthly_income': f"${profile.monthly_income:,.2f}",
            'monthly_expenses': f"${profile.monthly_expenses:,.2f}",
            'current_savings': f"${profile.current_savings:,.2f}",
            'savings_rate': f"{profile.savings_rate:.1%}",
            'investment_budget': f"${profile.investment_budget:,.2f}",
            'risk_tolerance': profile.risk_tolerance,
            'experience_level': profile.investment_experience,
            'age': profile.age,
            'number_of_goals': len(profile.investment_goals)
        }
    
    def _suggest_next_steps(self, profile: PersonalFinancialProfile) -> List[str]:
        """Suggest next steps based on the user's profile."""
        suggestions = []
        
        if profile.savings_rate < 0.1:  # Less than 10% savings rate
            suggestions.append("Consider reviewing your budget to increase your savings rate")
        
        if not profile.investment_goals:
            suggestions.append("Add specific investment goals to create a targeted strategy")
        
        if profile.investment_experience == 'beginner':
            suggestions.append("Start with our investment education features to build knowledge")
        
        if profile.investment_budget > 0:
            suggestions.append("Begin analyzing stocks that match your risk tolerance")
        
        return suggestions
    
    def _analyze_budget(self, profile: PersonalFinancialProfile) -> Dict[str, Any]:
        """Analyze user's budget and provide insights."""
        detailed_budget = profile.detailed_budget
        
        if not detailed_budget:
            return {'message': 'No detailed budget available'}
        
        # Calculate percentages
        total = sum(detailed_budget.values())
        if total == 0:
            return {'message': 'No budget data available'}
        
        budget_percentages = {k: (v / total) * 100 for k, v in detailed_budget.items()}
        
        # Provide recommendations based on common guidelines
        recommendations = []
        if budget_percentages.get('housing', 0) > 30:
            recommendations.append("Housing costs are above recommended 30% of income")
        if budget_percentages.get('food', 0) > 15:
            recommendations.append("Food costs are above recommended 15% of income")
        
        return {
            'budget_percentages': budget_percentages,
            'recommendations': recommendations,
            'total_expenses': total
        }
    
    def _analyze_goal_feasibility(self, goal_data: Dict[str, Any], profile: PersonalFinancialProfile) -> Dict[str, Any]:
        """Analyze the feasibility of achieving a financial goal."""
        target_amount = goal_data['target_amount']
        target_date = datetime.strptime(goal_data['target_date'], '%Y-%m-%d')
        months_to_goal = (target_date.year - datetime.now().year) * 12 + (target_date.month - datetime.now().month)
        
        monthly_needed = target_amount / max(months_to_goal, 1)
        current_budget = profile.investment_budget
        
        feasibility = "Achievable" if monthly_needed <= current_budget else "Challenging"
        
        return {
            'months_to_goal': months_to_goal,
            'monthly_savings_needed': monthly_needed,
            'current_monthly_budget': current_budget,
            'feasibility': feasibility,
            'budget_utilization': (monthly_needed / current_budget) * 100 if current_budget > 0 else 0
        }
    
    def _calculate_profile_health_score(self, profile: PersonalFinancialProfile) -> Dict[str, Any]:
        """Calculate a health score for the user's financial profile."""
        score = 0
        
        # Savings rate (30 points max)
        if profile.savings_rate >= 0.2:  # 20% or more
            score += 30
        elif profile.savings_rate >= 0.1:  # 10-20%
            score += 20
        elif profile.savings_rate >= 0.05:  # 5-10%
            score += 10
        
        # Debt-to-income ratio (25 points max)
        debt_ratio = profile.debt_to_income_ratio
        if debt_ratio <= 0.1:  # 10% or less
            score += 25
        elif debt_ratio <= 0.3:  # 10-30%
            score += 15
        elif debt_ratio <= 0.5:  # 30-50%
            score += 5
        
        # Investment budget (20 points max)
        if profile.investment_budget >= profile.monthly_income * 0.15:  # 15% or more
            score += 20
        elif profile.investment_budget >= profile.monthly_income * 0.1:  # 10-15%
            score += 15
        elif profile.investment_budget >= profile.monthly_income * 0.05:  # 5-10%
            score += 10
        
        # Goals (15 points max)
        if len(profile.investment_goals) >= 3:
            score += 15
        elif len(profile.investment_goals) >= 1:
            score += 10
        
        # Emergency fund (estimated - 10 points max)
        emergency_months = profile.current_savings / profile.monthly_expenses if profile.monthly_expenses > 0 else 0
        if emergency_months >= 6:
            score += 10
        elif emergency_months >= 3:
            score += 5
        
        final_score = min(score, 100)  # Cap at 100
        
        # Determine health rating
        if final_score >= 90:
            health_rating = "Excellent"
        elif final_score >= 75:
            health_rating = "Good"
        elif final_score >= 60:
            health_rating = "Fair"
        elif final_score >= 40:
            health_rating = "Needs Improvement"
        else:
            health_rating = "Poor"
        
        return {
            'total_score': final_score,
            'max_score': 100,
            'percentage': f"{final_score}%",
            'health_rating': health_rating,
            'breakdown': {
                'savings_rate': min(30, score) if profile.savings_rate >= 0.05 else 0,
                'debt_management': 25 if debt_ratio <= 0.1 else 15 if debt_ratio <= 0.3 else 5 if debt_ratio <= 0.5 else 0,
                'investment_preparedness': 20 if profile.investment_budget >= profile.monthly_income * 0.15 else 15 if profile.investment_budget >= profile.monthly_income * 0.1 else 10 if profile.investment_budget >= profile.monthly_income * 0.05 else 0,
                'goal_setting': 15 if len(profile.investment_goals) >= 3 else 10 if len(profile.investment_goals) >= 1 else 0,
                'emergency_fund': 10 if emergency_months >= 6 else 5 if emergency_months >= 3 else 0
            }
        }
    
    def _assess_stock_risk_for_user(self, ticker: str, profile: PersonalFinancialProfile) -> Dict[str, Any]:
        """Assess how risky a stock is for this specific user."""
        # This would normally involve complex analysis, but for demo:
        risk_factors = []
        
        if profile.investment_experience == 'beginner':
            risk_factors.append("Consider starting with index funds before individual stocks")
        
        if profile.risk_tolerance == 'conservative':
            risk_factors.append("This individual stock may be riskier than your preferred allocation")
        
        return {
            'overall_risk': 'moderate',
            'risk_factors': risk_factors,
            'suitability_score': 75  # Out of 100
        }
    
    def _check_goal_alignment(self, ticker: str, profile: PersonalFinancialProfile) -> Dict[str, Any]:
        """Check how well this stock aligns with user's goals."""
        aligned_goals = []
        
        for goal in profile.investment_goals:
            if 'growth' in goal.get('name', '').lower():
                aligned_goals.append(f"Aligns with your {goal['name']} goal")
        
        return {
            'aligned_goals': aligned_goals,
            'alignment_score': 80  # Out of 100
        }
    
    def _explain_like_im_new(self, user_id: str, parameters: Dict[str, Any], token: HushhConsentToken) -> Dict[str, Any]:
        """Provide beginner-friendly explanations."""
        try:
            ticker = parameters.get('ticker', '')
            topic = parameters.get('topic', '')
            
            if not topic:
                return self._error_response("Missing required parameter: topic")
            
            profile = self._load_user_profile(user_id)
            if not profile:
                return self._error_response("No profile found. Please setup profile first.")
            
            if not self.llm:
                return self._error_response("LLM not available for explanations")
            
            explanation_prompt = f"""
            You are explaining "{topic}" to a complete beginner investor.
            
            Context:
            - They're interested in {ticker} stock
            - Experience Level: {profile.investment_experience}
            - Age: {profile.age}
            - Risk Tolerance: {profile.risk_tolerance}
            
            Explain the concept using:
            1. Simple analogies they can relate to
            2. Real-world examples
            3. Why it matters for their situation
            4. Common mistakes to avoid
            
            Make it engaging and easy to understand.
            """
            
            response = self.llm.invoke(explanation_prompt)
            
            return {
                'status': 'success',
                'agent_id': self.agent_id,
                'user_id': user_id,
                'topic': topic,
                'ticker': ticker,
                'explanation': response.content,
                'key_takeaways': [
                    f'Understanding {topic} helps make better investment decisions',
                    f'Consider {topic} when evaluating {ticker}',
                    'Start simple and build knowledge over time'
                ],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._error_response(f"Explanation failed: {str(e)}")
    
    def _investment_education(self, user_id: str, parameters: Dict[str, Any], token: HushhConsentToken) -> Dict[str, Any]:
        """Provide educational content on investment topics."""
        try:
            topic = parameters.get('topic', '')
            
            if not topic:
                return self._error_response("Missing required parameter: topic")
            
            profile = self._load_user_profile(user_id)
            if not profile:
                return self._error_response("No profile found. Please setup profile first.")
            
            if not self.llm:
                return self._error_response("LLM not available for education")
            
            education_prompt = f"""
            Provide comprehensive education on: {topic}
            
            Student Profile:
            - Experience Level: {profile.investment_experience}
            - Age: {profile.age}
            - Risk Tolerance: {profile.risk_tolerance}
            - Learning Goal: Build investment knowledge
            
            Structure your response with:
            1. What is it? (Definition)
            2. Why does it matter? (Importance)
            3. How does it work? (Mechanics)
            4. What should they know? (Key concepts)
            5. How to get started? (Action steps)
            
            Adapt complexity to their experience level.
            """
            
            response = self.llm.invoke(education_prompt)
            
            return {
                'status': 'success',
                'agent_id': self.agent_id,
                'user_id': user_id,
                'topic': topic,
                'educational_content': response.content,
                'learning_objectives': [
                    f'Understand the fundamentals of {topic}',
                    'Apply knowledge to personal investment decisions',
                    'Build confidence in investment terminology'
                ],
                'next_steps': [
                    'Practice with small amounts',
                    'Continue learning related concepts',
                    'Seek additional resources'
                ],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._error_response(f"Education failed: {str(e)}")
    
    def _behavioral_coaching(self, user_id: str, parameters: Dict[str, Any], token: HushhConsentToken) -> Dict[str, Any]:
        """Provide behavioral finance coaching."""
        try:
            topic = parameters.get('topic', '')
            
            if not topic:
                return self._error_response("Missing required parameter: topic")
            
            profile = self._load_user_profile(user_id)
            if not profile:
                return self._error_response("No profile found. Please setup profile first.")
            
            if not self.llm:
                return self._error_response("LLM not available for coaching")
            
            coaching_prompt = f"""
            As a behavioral finance expert, provide coaching for: {topic}
            
            User Profile Context:
            - Experience Level: {profile.investment_experience}
            - Risk Tolerance: {profile.risk_tolerance}
            - Age: {profile.age}
            - Financial Situation: {profile.monthly_income - profile.monthly_expenses} surplus monthly
            
            Provide specific, actionable advice to overcome this behavioral bias.
            Focus on practical strategies they can implement.
            """
            
            response = self.llm.invoke(coaching_prompt)
            
            return {
                'status': 'success',
                'agent_id': self.agent_id,
                'user_id': user_id,
                'topic': topic,
                'coaching_advice': response.content,
                'action_items': [
                    'Practice mindful investing decisions',
                    'Set up systematic investment plans',
                    'Review investment decisions with cooled emotions'
                ],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._error_response(f"Behavioral coaching failed: {str(e)}")
    
    def _update_income(self, user_id: str, parameters: Dict[str, Any], token: HushhConsentToken) -> Dict[str, Any]:
        """Update user's monthly income."""
        try:
            new_income = parameters.get('income')
            if not new_income:
                return self._error_response("Missing required parameter: income")
            
            profile = self._load_user_profile(user_id)
            if not profile:
                return self._error_response("No profile found. Please setup profile first.")
            
            old_income = profile.monthly_income
            profile.update_financial_info(monthly_income=float(new_income))
            
            # Recalculate investment budget if needed
            new_surplus = profile.monthly_income - profile.monthly_expenses
            if profile.investment_budget > new_surplus * 0.8:  # Keep 20% buffer
                profile.update_financial_info(investment_budget=max(new_surplus * 0.5, 100))
            
            # Save updated profile
            if not self._save_user_profile(user_id, profile, token):
                return self._error_response("Failed to save income update to vault")
            
            return {
                'status': 'success',
                'agent_id': self.agent_id,
                'user_id': user_id,
                'message': 'Income updated successfully',
                'old_income': old_income,
                'new_income': profile.monthly_income,
                'new_savings_rate': profile.savings_rate * 100,
                'updated_investment_budget': profile.investment_budget,
                'vault_stored': True,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._error_response(f"Income update failed: {str(e)}")
    
    def _error_response(self, message: str) -> Dict[str, Any]:
        """Generate standardized error response."""
        return {
            'status': 'error',
            'agent_id': self.agent_id,
            'error': message,
            'timestamp': datetime.now().isoformat()
        }


# Main entry point for HushhMCP API integration
def run_agent(**kwargs):
    """Entry point for the personal financial agent."""
    agent = PersonalFinancialAgent()
    return agent.handle(**kwargs)
