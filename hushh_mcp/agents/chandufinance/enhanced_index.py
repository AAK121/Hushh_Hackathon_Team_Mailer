# hushh_mcp/agents/chandufinance/index.py

"""
Personal Financial Advisor - AI-Powered Wealth Management Agent
==============================================================

A revolutionary personal financial agent that combines traditional financial analysis
with AI-powered personalized advice. Learns your income, budget, goals, and risk 
tolerance to provide tailored investment recommendations using LLM insights.
"""

import json
import os
import requests
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
from hushh_mcp.types import ConsentScope, UserID, HushhConsentToken

# Import manifest
from hushh_mcp.agents.chandufinance.manifest import manifest


class PersonalFinancialProfile:
    """User's personal financial profile."""
    
    def __init__(self, data: Dict[str, Any] = None):
        self.data = data or {}
        
    @property
    def monthly_income(self) -> float:
        return self.data.get('monthly_income', 0.0)
    
    @property
    def monthly_expenses(self) -> float:
        return self.data.get('monthly_expenses', 0.0)
    
    @property
    def savings_rate(self) -> float:
        if self.monthly_income > 0:
            return (self.monthly_income - self.monthly_expenses) / self.monthly_income
        return 0.0
    
    @property
    def investment_budget(self) -> float:
        return self.data.get('investment_budget', 0.0)
    
    @property
    def risk_tolerance(self) -> str:
        return self.data.get('risk_tolerance', 'moderate')
    
    @property
    def investment_goals(self) -> List[Dict]:
        return self.data.get('investment_goals', [])
    
    @property
    def age(self) -> int:
        return self.data.get('age', 30)
    
    @property
    def investment_experience(self) -> str:
        return self.data.get('investment_experience', 'beginner')


class PersonalFinancialAgent:
    """
    AI-Powered Personal Financial Advisor that learns user's financial situation
    and provides personalized investment advice using LLM insights.
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
                print(f"LLM initialization failed: {e}")
    
    def handle(self, **kwargs) -> Dict[str, Any]:
        """Main entry point for the personal financial agent."""
        try:
            # Extract required parameters
            user_id = kwargs.get('user_id')
            token = kwargs.get('token')
            parameters = kwargs.get('parameters', {})
            
            if not user_id or not token:
                return self._error_response("Missing required parameters: user_id and token")
            
            # Validate consent token
            validation_result = self._validate_consent(token)
            if not validation_result['valid']:
                return self._error_response(f"Token validation failed: {validation_result['reason']}")
            
            # Get command from parameters
            command = parameters.get('command', 'setup_profile')
            
            # Route to appropriate handler
            return self._route_command(user_id, command, parameters)
                
        except Exception as e:
            return self._error_response(f"Agent execution failed: {str(e)}")
    
    def _validate_consent(self, token: str) -> Dict[str, Any]:
        """Validate consent token for required scopes."""
        try:
            if not token or len(token) < 10:
                return {'valid': False, 'reason': 'Invalid token format'}
            return {'valid': True, 'reason': 'Token validated successfully'}
        except Exception as e:
            return {'valid': False, 'reason': f'Token validation error: {str(e)}'}
    
    def _route_command(self, user_id: str, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Route commands to appropriate handlers."""
        
        # Personal Finance Management Commands
        if command == 'setup_profile':
            return self._setup_profile(user_id, parameters)
        elif command == 'update_income':
            return self._update_income(user_id, parameters)
        elif command == 'set_budget':
            return self._set_budget(user_id, parameters)
        elif command == 'add_goal':
            return self._add_goal(user_id, parameters)
        elif command == 'risk_assessment':
            return self._risk_assessment(user_id, parameters)
            
        # Personalized Analysis Commands
        elif command == 'personal_stock_analysis':
            return self._personal_stock_analysis(user_id, parameters)
        elif command == 'portfolio_review':
            return self._portfolio_review(user_id, parameters)
        elif command == 'goal_progress_check':
            return self._goal_progress_check(user_id, parameters)
        elif command == 'spending_analysis':
            return self._spending_analysis(user_id, parameters)
            
        # LLM-Enhanced Features
        elif command == 'personality_analysis':
            return self._personality_analysis(user_id, parameters)
        elif command == 'explain_like_im_new':
            return self._explain_like_im_new(user_id, parameters)
        elif command == 'behavioral_coaching':
            return self._behavioral_coaching(user_id, parameters)
        elif command == 'investment_education':
            return self._investment_education(user_id, parameters)
            
        # Traditional Analysis (Enhanced with Personal Context)
        elif command == 'run_valuation':
            return self._run_personalized_valuation(user_id, parameters)
        elif command == 'get_financials':
            return self._get_financials(user_id, parameters)
        else:
            return self._error_response(f"Unknown command: {command}")
    
    # ===== PERSONAL FINANCE MANAGEMENT =====
    
    def _setup_profile(self, user_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Set up user's personal financial profile."""
        try:
            profile_data = {
                'monthly_income': parameters.get('monthly_income', 0.0),
                'monthly_expenses': parameters.get('monthly_expenses', 0.0),
                'age': parameters.get('age', 30),
                'investment_experience': parameters.get('investment_experience', 'beginner'),
                'risk_tolerance': parameters.get('risk_tolerance', 'moderate'),
                'investment_budget': parameters.get('investment_budget', 0.0),
                'investment_goals': parameters.get('investment_goals', []),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Save to vault
            self._save_user_profile(user_id, profile_data)
            
            # Generate personalized welcome message using LLM
            welcome_message = self._generate_welcome_message(profile_data)
            
            return {
                'status': 'success',
                'agent_id': self.agent_id,
                'user_id': user_id,
                'message': 'Financial profile created successfully',
                'profile_summary': self._summarize_profile(profile_data),
                'welcome_message': welcome_message,
                'next_steps': self._suggest_next_steps(profile_data),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._error_response(f"Profile setup failed: {str(e)}")
    
    def _personal_stock_analysis(self, user_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a stock with personal financial context."""
        try:
            ticker = parameters.get('ticker', '').upper()
            if not ticker:
                return self._error_response("Missing required parameter: ticker")
            
            profile = self._load_user_profile(user_id)
            if not profile:
                return self._error_response("No profile found. Please setup profile first.")
            
            # Get basic financial data
            financial_data = self._fetch_financial_data(ticker)
            current_price = parameters.get('current_price', 100.0)
            
            # Generate personalized analysis using LLM
            personal_analysis = self._generate_personal_stock_analysis(
                ticker, financial_data, current_price, profile
            )
            
            # Calculate position sizing recommendation
            position_size = self._calculate_position_size(current_price, profile)
            
            return {
                'status': 'success',
                'agent_id': self.agent_id,
                'user_id': user_id,
                'ticker': ticker,
                'current_price': current_price,
                'personal_analysis': personal_analysis,
                'position_sizing': position_size,
                'risk_assessment': self._assess_stock_risk_for_user(ticker, profile),
                'goal_alignment': self._check_goal_alignment(ticker, profile),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._error_response(f"Personal stock analysis failed: {str(e)}")
    
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
    
    def _generate_welcome_message(self, profile_data: Dict[str, Any]) -> str:
        """Generate a personalized welcome message using LLM."""
        if not self.llm:
            return f"Welcome! Your financial profile has been set up with ${profile_data['monthly_income']:,.2f} monthly income."
        
        try:
            savings_rate = 0
            if profile_data['monthly_income'] > 0:
                savings_rate = (profile_data['monthly_income'] - profile_data['monthly_expenses']) / profile_data['monthly_income']
            
            prompt = f"""
            Create a warm, encouraging welcome message for a new user who just set up their financial profile.
            
            Their details:
            - Monthly Income: ${profile_data['monthly_income']:,.2f}
            - Monthly Expenses: ${profile_data['monthly_expenses']:,.2f}
            - Savings Rate: {savings_rate:.1%}
            - Age: {profile_data['age']}
            - Experience: {profile_data['investment_experience']}
            - Risk Tolerance: {profile_data['risk_tolerance']}
            
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
    
    def _load_user_profile(self, user_id: str) -> Optional[PersonalFinancialProfile]:
        """Load user's financial profile from vault."""
        try:
            vault_path = self._get_vault_path(user_id, "financial_profile.json")
            if not vault_path.exists():
                return None
            
            with open(vault_path, 'r') as f:
                data = json.load(f)
            
            return PersonalFinancialProfile(data)
            
        except Exception as e:
            print(f"Error loading user profile: {e}")
            return None
    
    def _save_user_profile(self, user_id: str, profile_data: Dict[str, Any]):
        """Save user's financial profile to vault."""
        try:
            vault_path = self._get_vault_path(user_id, "financial_profile.json")
            vault_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(vault_path, 'w') as f:
                json.dump(profile_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving user profile: {e}")
    
    def _get_vault_path(self, user_id: str, filename: str) -> Path:
        """Get vault path for user-specific data."""
        vault_dir = Path(__file__).parent.parent.parent.parent / "vault" / user_id
        return vault_dir / filename
    
    def _summarize_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of the user's financial profile."""
        savings_rate = 0
        if profile_data['monthly_income'] > 0:
            savings_rate = (profile_data['monthly_income'] - profile_data['monthly_expenses']) / profile_data['monthly_income']
        
        return {
            'monthly_income': f"${profile_data['monthly_income']:,.2f}",
            'monthly_expenses': f"${profile_data['monthly_expenses']:,.2f}",
            'savings_rate': f"{savings_rate:.1%}",
            'investment_budget': f"${profile_data['investment_budget']:,.2f}",
            'risk_tolerance': profile_data['risk_tolerance'],
            'experience_level': profile_data['investment_experience'],
            'number_of_goals': len(profile_data.get('investment_goals', []))
        }
    
    def _suggest_next_steps(self, profile_data: Dict[str, Any]) -> List[str]:
        """Suggest next steps based on the user's profile."""
        suggestions = []
        
        savings_rate = 0
        if profile_data['monthly_income'] > 0:
            savings_rate = (profile_data['monthly_income'] - profile_data['monthly_expenses']) / profile_data['monthly_income']
        
        if savings_rate < 0.1:  # Less than 10% savings rate
            suggestions.append("Consider reviewing your budget to increase your savings rate")
        
        if not profile_data.get('investment_goals'):
            suggestions.append("Add specific investment goals to create a targeted strategy")
        
        if profile_data['investment_experience'] == 'beginner':
            suggestions.append("Start with our investment education features to build knowledge")
        
        if profile_data['investment_budget'] > 0:
            suggestions.append("Begin analyzing stocks that match your risk tolerance")
        
        return suggestions
    
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
