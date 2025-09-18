"""
Interactive Chat Demo for the HushhMCP Personal Financial Agent
Natural conversation interface - just type what you want to do!
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

from hushh_mcp.agents.chandufinance.index import PersonalFinancialAgent
from hushh_mcp.constants import ConsentScope
from hushh_mcp.consent.token import issue_token


class FinancialChatDemo:
    """Natural language chat interface for the HushhMCP Personal Financial Agent"""
    
    def __init__(self):
        self.user_id = "financial_demo_user"
        self.agent_id = "chandufinance"
        self.agent = PersonalFinancialAgent()
        self.tokens = self.create_demo_tokens()
        self.conversation_count = 0
        self.profile_setup = False
        
    def create_demo_tokens(self) -> str:
        """Create demo tokens for the session with proper vault access"""
        # Create proper HushhConsentTokens for financial operations with vault access
        scopes = [
            ConsentScope.VAULT_READ_FILE,
            ConsentScope.VAULT_WRITE_FILE,
            ConsentScope.VAULT_READ_FINANCE,
            ConsentScope.AGENT_FINANCE_ANALYZE,
        ]
        
        # Use VAULT_WRITE_FILE scope for comprehensive access to personal financial data
        token = issue_token(
            user_id=self.user_id,
            agent_id=self.agent_id,
            scope=ConsentScope.VAULT_WRITE_FILE,  # Allows reading and writing profile data
            expires_in_ms=1000 * 60 * 60 * 24  # 24 hours
        )
        
        return token.token
    
    def print_welcome(self):
        """Print welcome message"""
        print("🏦 HUSHHMCP PERSONAL FINANCIAL ADVISOR - INTERACTIVE CHAT")
        print("=" * 70)
        print("Welcome to your AI-powered personal financial advisor!")
        print("I can help you manage your finances, analyze investments, and plan for the future.")
        print("=" * 70)
        
        # Check API key
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            print(f"✅ Gemini API Key: {gemini_key[:10]}...")
            print("🤖 AI-powered personalized advice: ENABLED")
        else:
            print("⚠️ Warning: GEMINI_API_KEY not found - Limited AI features")
        
        print(f"\n💡 Try saying things like:")
        print(f"  • 'setup my profile' (first-time setup)")
        print(f"  • 'I earn $5000 monthly and spend $3500'")
        print(f"  • 'add goal: save $20000 for house down payment by 2026-12-01'")
        print(f"  • 'analyze AAPL stock for me'")
        print(f"  • 'explain dividend investing like I'm new'")
        print(f"  • 'show my financial profile'")
        print(f"  • 'check my goal progress'")
        print(f"  • 'help' (for more examples)")
        print(f"  • 'quit' or 'exit' to leave")
        print()
    
    def show_help(self):
        """Show help with examples"""
        print("\n💡 HELP - EXAMPLE COMMANDS")
        print("=" * 60)
        print("📝 PROFILE SETUP:")
        print("  • setup my profile")
        print("  • I'm 28 years old, work as software engineer")
        print("  • update my income to $6000")
        print("  • set my budget: housing $1500, food $800, transport $300")
        print()
        print("🎯 GOAL MANAGEMENT:")
        print("  • add goal: save $50000 for retirement by 2030-01-01")
        print("  • add goal: emergency fund $15000 by 2026-06-15")
        print("  • check my goal progress")
        print("  • show my goals")
        print()
        print("📈 INVESTMENT ANALYSIS:")
        print("  • analyze AAPL stock for me")
        print("  • what do you think about Tesla stock?")
        print("  • review my portfolio")
        print("  • give me investment advice")
        print()
        print("🎓 FINANCIAL EDUCATION:")
        print("  • explain dividend investing like I'm new")
        print("  • teach me about compound interest")
        print("  • what is dollar cost averaging?")
        print("  • help me understand risk management")
        print()
        print("📊 PROFILE & ANALYSIS:")
        print("  • show my financial profile")
        print("  • view my profile")
        print("  • what's my financial health score?")
        print("  • give me a financial summary")
        print()
        print("🧠 BEHAVIORAL COACHING:")
        print("  • help me with emotional investing")
        print("  • I'm scared to invest during market volatility")
        print("  • behavioral coaching for FOMO investing")
        print("-" * 60)
    
    def handle_special_commands(self, user_input: str) -> bool:
        """Handle special commands like help, quit, etc. Returns True if handled."""
        user_input_lower = user_input.lower().strip()
        
        if user_input_lower in ['quit', 'exit', 'bye', 'goodbye']:
            print("\n👋 Thank you for using the HushhMCP Personal Financial Advisor!")
            print("🎉 Remember: Good financial habits compound over time!")
            print("💡 Keep tracking your progress and stay consistent with your goals!")
            return True
        
        elif user_input_lower in ['help', '?', 'examples']:
            self.show_help()
            return True
        
        elif user_input_lower in ['clear', 'cls']:
            os.system('cls' if os.name == 'nt' else 'clear')
            self.print_welcome()
            return True
        
        return False
    
    def parse_natural_language_command(self, user_input: str) -> Dict[str, Any]:
        """Parse natural language input into agent commands with actual data extraction"""
        user_input_lower = user_input.lower().strip()
        import re
        
        # Profile setup commands - Extract actual data from user input
        if any(phrase in user_input_lower for phrase in ['setup profile', 'create profile', 'setup my profile']):
            # Extract age if mentioned
            age_match = re.search(r'\b(\d{1,2})\s*(?:years?\s*old|yr|age)', user_input_lower)
            age = int(age_match.group(1)) if age_match else None
            
            # Extract savings amount
            savings_patterns = [
                r'savings?\s*(?:of\s*)?[\$₹]?(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'have\s*[\$₹]?(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'[\$₹](\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:savings?|saved)'
            ]
            current_savings = 0
            for pattern in savings_patterns:
                savings_match = re.search(pattern, user_input_lower)
                if savings_match:
                    savings_str = savings_match.group(1).replace(',', '')
                    current_savings = float(savings_str)
                    # Convert rupees to dollars for consistency (rough conversion)
                    if '₹' in user_input or 'rupees' in user_input_lower or 'rupee' in user_input_lower:
                        current_savings = current_savings / 83  # Rough USD conversion
                    break
            
            # Extract income if mentioned
            income_patterns = [
                r'earn\s*[\$₹]?(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'income\s*[\$₹]?(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'make\s*[\$₹]?(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'salary\s*[\$₹]?(\d+(?:,\d{3})*(?:\.\d{2})?)'
            ]
            monthly_income = 0
            for pattern in income_patterns:
                income_match = re.search(pattern, user_input_lower)
                if income_match:
                    income_str = income_match.group(1).replace(',', '')
                    monthly_income = float(income_str)
                    # Convert rupees to dollars for consistency
                    if '₹' in user_input or 'rupees' in user_input_lower or 'rupee' in user_input_lower:
                        monthly_income = monthly_income / 83
                    break
            
            # Determine risk tolerance based on age and text
            risk_tolerance = 'moderate'
            if age and age < 25:
                risk_tolerance = 'aggressive'
            elif age and age > 50:
                risk_tolerance = 'conservative'
            elif not age:  # If no age extracted, default to young aggressive
                age = 25
                risk_tolerance = 'aggressive'
            
            # Look for risk-related keywords
            if any(word in user_input_lower for word in ['conservative', 'safe', 'low risk']):
                risk_tolerance = 'conservative'
            elif any(word in user_input_lower for word in ['aggressive', 'high risk', 'risky']):
                risk_tolerance = 'aggressive'
            
            # Determine investment experience
            experience = 'beginner'
            if any(word in user_input_lower for word in ['experienced', 'expert', 'advanced']):
                experience = 'advanced'
            elif any(word in user_input_lower for word in ['intermediate', 'some experience']):
                experience = 'intermediate'
            
            # Extract occupation if mentioned
            occupation_keywords = {
                'engineer': 'Software Engineer',
                'developer': 'Software Developer', 
                'doctor': 'Doctor',
                'teacher': 'Teacher',
                'student': 'Student',
                'manager': 'Manager',
                'analyst': 'Analyst'
            }
            occupation = 'Professional'
            for keyword, job_title in occupation_keywords.items():
                if keyword in user_input_lower:
                    occupation = job_title
                    break
            
            # Calculate basic budget if we have income
            monthly_expenses = monthly_income * 0.7 if monthly_income > 0 else 0
            investment_budget = max(0, monthly_income - monthly_expenses) if monthly_income > 0 else 0
            
            # Prepare result with conversion info
            result = {
                'command': 'setup_profile',
                'full_name': 'User',  # Could extract from input if provided
                'age': age if age else 25,
                'occupation': occupation,
                'monthly_income': monthly_income if monthly_income > 0 else 0,
                'monthly_expenses': monthly_expenses,
                'current_savings': current_savings,
                'investment_budget': investment_budget,
                'risk_tolerance': risk_tolerance,
                'investment_experience': experience
            }
            
            # Add conversion notes if currency conversion happened
            if '₹' in user_input or 'rupees' in user_input_lower or 'rupee' in user_input_lower:
                result['conversion_note'] = f"💱 Currency converted from INR to USD (rate: ₹83 ≈ $1)"
            
            return result
        
        # Income update with actual extraction
        elif any(phrase in user_input_lower for phrase in ['earn', 'income', 'salary', 'make']) and any(char.isdigit() for char in user_input):
            income_match = re.search(r'[\$₹]?(\d+(?:,\d{3})*(?:\.\d{2})?)', user_input)
            if income_match:
                income_str = income_match.group(1).replace(',', '')
                income = float(income_str)
                # Convert rupees to dollars
                if '₹' in user_input or 'rupees' in user_input_lower:
                    income = income / 83
                
                return {
                    'command': 'update_income',
                    'monthly_income': income
                }
        
        # Goal addition with actual data extraction
        elif 'goal' in user_input_lower and any(phrase in user_input_lower for phrase in ['add', 'save', 'target']):
            # Extract amount
            amount_match = re.search(r'[\$₹]?(\d+(?:,\d{3})*(?:\.\d{2})?)', user_input)
            target_amount = 50000  # default
            if amount_match:
                amount_str = amount_match.group(1).replace(',', '')
                target_amount = float(amount_str)
                # Convert rupees to dollars
                if '₹' in user_input or 'rupees' in user_input_lower:
                    target_amount = target_amount / 83
            
            # Extract date
            date_match = re.search(r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})', user_input)
            target_date = date_match.group(1) if date_match else '2026-12-31'
            
            # Determine goal type
            goal_name = "Financial Goal"
            if any(word in user_input_lower for word in ['house', 'home', 'property']):
                goal_name = "House Down Payment"
            elif any(word in user_input_lower for word in ['retirement', 'retire']):
                goal_name = "Retirement Savings"
            elif any(word in user_input_lower for word in ['emergency', 'emergency fund']):
                goal_name = "Emergency Fund"
            elif any(word in user_input_lower for word in ['car', 'vehicle']):
                goal_name = "Car Purchase"
            elif any(word in user_input_lower for word in ['education', 'study', 'college']):
                goal_name = "Education Fund"
            
            return {
                'command': 'add_goal',
                'goal_name': goal_name,
                'target_amount': target_amount,
                'target_date': target_date,
                'priority': 'high'
            }
        
        # Stock analysis with ticker extraction
        elif any(phrase in user_input_lower for phrase in ['analyze', 'analysis', 'stock', 'ticker']):
            # Extract ticker symbol - look for 2-5 letter combinations in caps
            ticker_match = re.search(r'\\b([A-Z]{2,5})\\b', user_input.upper())
            ticker = ticker_match.group(1) if ticker_match else 'AAPL'
            
            # Also check for common stock names
            stock_names = {
                'apple': 'AAPL', 'microsoft': 'MSFT', 'google': 'GOOGL', 
                'tesla': 'TSLA', 'amazon': 'AMZN', 'meta': 'META',
                'netflix': 'NFLX', 'nvidia': 'NVDA'
            }
            
            for name, symbol in stock_names.items():
                if name in user_input_lower:
                    ticker = symbol
                    break
            
            return {
                'command': 'personal_stock_analysis',
                'ticker': ticker
            }
        
        # Profile viewing
        elif any(phrase in user_input_lower for phrase in ['show profile', 'view profile', 'my profile', 'profile summary']):
            return {
                'command': 'view_profile'
            }
        
        # Goal progress checking
        elif any(phrase in user_input_lower for phrase in ['goal progress', 'check goals', 'my goals', 'progress']):
            return {
                'command': 'goal_progress_check'
            }
        
        # Educational content
        elif any(phrase in user_input_lower for phrase in ['explain', 'teach', 'what is', 'help me understand']):
            # Extract the topic
            topic = user_input_lower
            if 'dividend' in topic:
                topic = 'dividend investing'
            elif 'compound' in topic:
                topic = 'compound interest'
            elif 'dollar cost' in topic or 'dca' in topic:
                topic = 'dollar cost averaging'
            elif 'risk' in topic:
                topic = 'risk management'
            else:
                topic = 'general investing'
            
            return {
                'command': 'explain_like_im_new',
                'topic': topic,
                'complexity': 'beginner'
            }
        
        # Portfolio review
        elif any(phrase in user_input_lower for phrase in ['portfolio', 'review', 'investments']):
            return {
                'command': 'portfolio_review'
            }
        
        # Default fallback - treat as general query
        else:
            return {
                'command': 'explain_like_im_new',
                'topic': user_input,
                'complexity': 'beginner'
            }
    
    def display_result(self, result: Dict[str, Any]):
        """Display the result in a conversational way"""
        print(f"\n🤖 Financial Advisor Response:")
        print("-" * 40)
        
        if result.get('status') == 'success':
            print(f"✅ {result.get('message', 'Success!')}")
            
            # Display specific information based on command type
            if 'profile_summary' in result:
                summary = result['profile_summary']
                print(f"\n📊 PROFILE SUMMARY:")
                print(f"� Age: {summary.get('age', 'N/A')}")
                print(f"�💰 Monthly Income: {summary.get('monthly_income', 'N/A')}")
                print(f"💸 Monthly Expenses: {summary.get('monthly_expenses', 'N/A')}")
                print(f"� Current Savings: {summary.get('current_savings', 'N/A')}")
                print(f"�📈 Savings Rate: {summary.get('savings_rate', 'N/A')}")
                print(f"🎯 Investment Budget: {summary.get('investment_budget', 'N/A')}")
                print(f"🎭 Risk Tolerance: {summary.get('risk_tolerance', 'N/A')}")
                print(f"📚 Experience: {summary.get('experience_level', 'N/A')}")
            
            if 'welcome_message' in result:
                print(f"\n💬 PERSONALIZED MESSAGE:")
                print(result['welcome_message'])
            
            if 'ticker' in result:
                print(f"\n📈 STOCK ANALYSIS: {result['ticker']}")
                print(f"💰 Current Price: ${result.get('current_price', 'N/A')}")
                if 'personalized_analysis' in result:
                    print(f"\n🤖 AI ANALYSIS:")
                    print(result['personalized_analysis'])
            
            if 'explanation' in result:
                print(f"\n🎓 EDUCATIONAL CONTENT:")
                print(result['explanation'])
            
            if 'coaching_advice' in result:
                print(f"\n🧠 BEHAVIORAL COACHING:")
                print(result['coaching_advice'])
            
            if 'conversion_note' in result:
                print(f"\n{result['conversion_note']}")
            
            if 'goal_details' in result:
                goal = result['goal_details']
                print(f"\n🎯 GOAL ADDED:")
                print(f"📝 Name: {goal.get('name', 'N/A')}")
                print(f"💰 Target: ${goal.get('target_amount', 0):,.2f}")
                print(f"📅 Date: {goal.get('target_date', 'N/A')}")
            
            if 'profile_health_score' in result:
                health = result['profile_health_score']
                if isinstance(health, dict):
                    print(f"\n🏆 FINANCIAL HEALTH SCORE:")
                    print(f"📊 Score: {health.get('total_score', 0)}/100 ({health.get('percentage', '0%')})")
                    print(f"🎯 Rating: {health.get('health_rating', 'Unknown')}")
            
        else:
            print(f"❌ {result.get('error', result.get('message', 'An error occurred'))}")
            
            # Provide helpful suggestions for common errors
            error_msg = result.get('error', '').lower()
            if 'no profile' in error_msg:
                print(f"\n💡 TIP: Try saying 'setup my profile' first!")
            elif 'missing' in error_msg:
                print(f"\n💡 TIP: Try providing more details in your request")
        
        print("-" * 40)
    
    def process_input(self, user_input: str):
        """Process user input through the agent"""
        print(f"\n🔄 Processing: {user_input}")
        
        try:
            # Parse natural language to command parameters
            command_params = self.parse_natural_language_command(user_input)
            
            # Call the agent
            result = self.agent.handle(
                user_id=self.user_id,
                token=self.tokens,
                parameters=command_params
            )
            
            # Track if profile is set up
            if command_params.get('command') == 'setup_profile' and result.get('status') == 'success':
                self.profile_setup = True
            
            self.display_result(result)
            
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            print("💡 Try rephrasing your request or type 'help' for examples.")
    
    def run(self):
        """Run the interactive chat demo"""
        self.print_welcome()
        
        print("🚀 Financial Advisor ready! Let's start managing your finances...")
        print("✅ Ready for your commands!")
        
        print(f"\n💬 Start chatting! (Type 'help' for examples, 'quit' to exit)")
        print("=" * 70)
        
        while True:
            try:
                # Get user input
                user_input = input(f"\n[{self.conversation_count + 1}] 🗣️ You: ").strip()
                
                if not user_input:
                    print("💭 (Please say something or type 'help' for examples)")
                    continue
                
                # Handle special commands
                if self.handle_special_commands(user_input):
                    if user_input.lower().strip() in ['quit', 'exit', 'bye', 'goodbye']:
                        break
                    continue
                
                # Process through the agent
                self.process_input(user_input)
                self.conversation_count += 1
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Thank you for using the HushhMCP Personal Financial Advisor!")
                print("🎉 Remember: Good financial habits compound over time!")
                print("💡 Keep tracking your progress and stay consistent with your goals!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {str(e)}")
                print("💡 Try again or type 'quit' to exit.")


def main():
    """Main function to start the chat demo"""
    print("🚀 Starting HushhMCP Personal Financial Advisor Chat Demo...")
    
    # Check environment
    if not os.getenv('GEMINI_API_KEY'):
        print("\n⚠️ Warning: GEMINI_API_KEY not found in environment variables.")
        print("The agent will work but AI-powered personalized advice will be limited.")
        try:
            response = input("Continue anyway? (y/n): ").strip().lower()
            if response not in ['y', 'yes']:
                print("👋 Goodbye!")
                return
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            return
    
    # Start the chat demo
    try:
        demo = FinancialChatDemo()
        demo.run()
    except Exception as e:
        print(f"\n❌ Failed to start demo: {str(e)}")
        print("Please check your environment and try again.")


if __name__ == "__main__":
    main()
