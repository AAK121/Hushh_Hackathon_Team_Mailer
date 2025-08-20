#!/usr/bin/env python3

"""
Personal Financial Advisor CLI - HushhMCP Compliant Version
===========================================================

Command-line interface for the Personal Financial Advisor agent with proper
HushhMCP consent token validation and encrypted vault storage.

Features:
- Comprehensive personal information management
- Encrypted vault storage for all financial data
- LLM-powered personalized investment advice
- Goal-based financial planning
- Risk-appropriate recommendations
"""

import argparse
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import HushhMCP components
from hushh_mcp.consent.token import issue_token
from hushh_mcp.constants import ConsentScope
from hushh_mcp.agents.chandufinance.index import PersonalFinancialAgent


def create_test_consent_token(user_id: str, scope: str) -> str:
    """Create a test consent token for CLI usage."""
    try:
        token_obj = issue_token(
            user_id=user_id,
            agent_id="chandufinance",
            scope=ConsentScope(scope),
            expires_in_ms=1000 * 60 * 60 * 24  # 24 hours
        )
        return token_obj.token
    except Exception as e:
        print(f"⚠️ Failed to create consent token: {e}")
        return "test_token_for_cli"


def execute_agent_command(user_id: str, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute agent command with proper consent token."""
    
    # Determine required scope based on command (use the highest permission needed)
    if command in ['setup_profile', 'update_personal_info', 'update_income', 'set_budget', 'add_goal']:
        scope = ConsentScope.VAULT_WRITE_FILE.value
    elif command in ['personal_stock_analysis', 'portfolio_review']:
        scope = ConsentScope.VAULT_READ_FINANCE.value
    else:
        scope = ConsentScope.VAULT_READ_FILE.value
    
    # Create consent token
    token = create_test_consent_token(user_id, scope)
    
    # Initialize agent
    agent = PersonalFinancialAgent()
    
    # Execute command
    return agent.handle(
        user_id=user_id,
        token=token,
        parameters={'command': command, **parameters}
    )


def format_currency(amount: float) -> str:
    """Format currency values."""
    return f"${amount:,.2f}"


def format_percentage(decimal: float) -> str:
    """Format percentage values."""
    return f"{decimal * 100:.1f}%"


def print_header(title: str):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"🏦 {title}")
    print("=" * 60)


def print_section(title: str):
    """Print formatted section."""
    print(f"\n📊 {title.upper()}:")
    print("-" * 40)


def display_results(result: Dict[str, Any], json_output: bool = False):
    """Display command results in a user-friendly format."""
    
    if json_output:
        import json
        print(json.dumps(result, indent=2, default=str))
        return
    
    if result.get('status') == 'error':
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
        return
    
    command = result.get('command', 'unknown')
    
    if command == 'setup_profile':
        display_profile_setup_results(result)
    elif command == 'personal_stock_analysis':
        display_stock_analysis_results(result)
    elif command == 'view_profile':
        display_profile_view_results(result)
    elif command == 'add_goal':
        display_goal_results(result)
    else:
        display_generic_results(result)


def display_profile_setup_results(result: Dict[str, Any]):
    """Display profile setup results."""
    print_header("PERSONAL FINANCIAL PROFILE CREATED!")
    
    profile_summary = result.get('profile_summary', {})
    
    if 'personal_snapshot' in profile_summary:
        personal = profile_summary['personal_snapshot']
        print_section("PERSONAL INFORMATION")
        if personal.get('name'):
            print(f"👤 Name: {personal['name']}")
        print(f"🎂 Age: {personal.get('age', 'N/A')}")
        if personal.get('occupation'):
            print(f"💼 Occupation: {personal['occupation']}")
        print(f"👨‍👩‍👧‍👦 Family Status: {personal.get('family_status', 'N/A')}")
        print(f"👶 Dependents: {personal.get('dependents', 0)}")
    
    if 'financial_snapshot' in profile_summary:
        financial = profile_summary['financial_snapshot']
        print_section("FINANCIAL SNAPSHOT")
        print(f"💰 Monthly Income: {format_currency(financial.get('monthly_income', 0))}")
        print(f"💸 Monthly Expenses: {format_currency(financial.get('monthly_expenses', 0))}")
        print(f"📈 Savings Rate: {financial.get('savings_rate', '0%')}")
        print(f"💼 Investment Budget: {format_currency(financial.get('investment_budget', 0))}")
        if financial.get('current_savings'):
            print(f"🏦 Current Savings: {format_currency(financial['current_savings'])}")
        if financial.get('debt_to_income_ratio'):
            print(f"📊 Debt-to-Income Ratio: {financial['debt_to_income_ratio']}")
    
    if 'investment_profile' in profile_summary:
        investment = profile_summary['investment_profile']
        print_section("INVESTMENT PROFILE")
        print(f"⚖️ Risk Tolerance: {investment.get('risk_tolerance', 'N/A').title()}")
        print(f"🎓 Experience Level: {investment.get('experience_level', 'N/A').title()}")
        print(f"⏰ Time Horizon: {investment.get('time_horizon', 'N/A').replace('_', ' ').title()}")
        print(f"🎯 Active Goals: {investment.get('active_goals', 0)}")
    
    # Display personalized welcome message
    if result.get('welcome_message'):
        print_section("PERSONALIZED MESSAGE")
        print(result['welcome_message'])
    
    # Display next steps
    if result.get('next_steps'):
        print_section("RECOMMENDED NEXT STEPS")
        for i, step in enumerate(result['next_steps'], 1):
            print(f"{i}. {step}")
    
    print(f"\n✅ Profile saved to encrypted vault!")


def display_stock_analysis_results(result: Dict[str, Any]):
    """Display stock analysis results."""
    ticker = result.get('ticker', 'UNKNOWN')
    price = result.get('current_price', 0)
    
    print_header(f"PERSONAL STOCK ANALYSIS: {ticker}")
    print(f"💰 Current Price: {format_currency(price)}")
    
    # Personal Analysis from LLM
    if result.get('personal_analysis'):
        print_section("AI-POWERED PERSONAL ANALYSIS")
        print(result['personal_analysis'])
    
    # Position Sizing
    if result.get('position_sizing'):
        sizing = result['position_sizing']
        print_section("POSITION SIZING RECOMMENDATION")
        print(f"💵 Max Position Value: {format_currency(sizing.get('max_position_value', 0))}")
        print(f"📈 Max Shares: {sizing.get('max_shares', 0)}")
        print(f"📊 Allocation %: {sizing.get('allocation_percentage', 0):.1f}%")
        if sizing.get('reasoning'):
            print(f"💡 Reasoning: {sizing['reasoning']}")
    
    # Risk Assessment
    if result.get('risk_assessment'):
        risk = result['risk_assessment']
        print_section("PERSONAL RISK ASSESSMENT")
        print(f"🎯 Overall Risk: {risk.get('overall_risk', 'N/A')}")
        if risk.get('suitability_score'):
            print(f"📊 Suitability Score: {risk['suitability_score']}/100")
        if risk.get('risk_factors'):
            print("⚠️ Risk Factors for You:")
            for factor in risk['risk_factors']:
                print(f"  • {factor}")
    
    # Goal Alignment
    if result.get('goal_alignment'):
        alignment = result['goal_alignment']
        print_section("GOAL ALIGNMENT")
        if alignment.get('alignment_score'):
            print(f"📊 Alignment Score: {alignment['alignment_score']}/100")
        if alignment.get('aligned_goals'):
            for goal in alignment['aligned_goals']:
                print(f"✅ {goal}")


def display_profile_view_results(result: Dict[str, Any]):
    """Display comprehensive profile view."""
    print_header("YOUR COMPLETE FINANCIAL PROFILE")
    
    # Personal Information
    if result.get('personal_info'):
        personal = result['personal_info']
        print_section("PERSONAL INFORMATION")
        for key, value in personal.items():
            if value:
                formatted_key = key.replace('_', ' ').title()
                print(f"👤 {formatted_key}: {value}")
    
    # Financial Information
    if result.get('financial_info'):
        financial = result['financial_info']
        print_section("FINANCIAL INFORMATION")
        for key, value in financial.items():
            if value:
                formatted_key = key.replace('_', ' ').title()
                if 'rate' in key or 'ratio' in key:
                    print(f"📊 {formatted_key}: {format_percentage(value) if isinstance(value, float) and value < 1 else value}")
                elif isinstance(value, (int, float)) and 'amount' in key or 'income' in key or 'expense' in key or 'budget' in key or 'savings' in key:
                    print(f"💰 {formatted_key}: {format_currency(value)}")
                else:
                    print(f"📋 {formatted_key}: {value}")
    
    # Investment Preferences
    if result.get('preferences'):
        prefs = result['preferences']
        print_section("INVESTMENT PREFERENCES")
        for key, value in prefs.items():
            if value:
                formatted_key = key.replace('_', ' ').title()
                print(f"⚙️ {formatted_key}: {value.title() if isinstance(value, str) else value}")
    
    # Goals
    if result.get('goals'):
        print_section("INVESTMENT GOALS")
        for i, goal in enumerate(result['goals'], 1):
            print(f"🎯 Goal {i}: {goal.get('name', 'Unnamed Goal')}")
            if goal.get('target_amount'):
                print(f"   💰 Target: {format_currency(goal['target_amount'])}")
            if goal.get('target_date'):
                print(f"   📅 Date: {goal['target_date']}")
            if goal.get('priority'):
                print(f"   ⭐ Priority: {goal['priority'].title()}")
    
    # Health Score
    if result.get('profile_health_score'):
        health = result['profile_health_score']
        print_section("FINANCIAL HEALTH SCORE")
        print(f"📊 Overall Score: {health.get('total_score', 0)}/{health.get('max_score', 100)} ({health.get('percentage', '0%')})")
        print(f"🏆 Rating: {health.get('health_rating', 'Unknown')}")


def display_goal_results(result: Dict[str, Any]):
    """Display goal addition results."""
    goal_details = result.get('goal_details', {})
    goal_analysis = result.get('goal_analysis', {})
    
    print_header(f"INVESTMENT GOAL ADDED: {goal_details.get('name', 'Unknown')}")
    
    print_section("GOAL DETAILS")
    print(f"🎯 Name: {goal_details.get('name', 'N/A')}")
    print(f"💰 Target Amount: {format_currency(goal_details.get('target_amount', 0))}")
    print(f"📅 Target Date: {goal_details.get('target_date', 'N/A')}")
    print(f"⭐ Priority: {goal_details.get('priority', 'medium').title()}")
    
    if goal_analysis and 'error' not in goal_analysis:
        print_section("FEASIBILITY ANALYSIS")
        print(f"📅 Months to Goal: {goal_analysis.get('months_to_goal', 'N/A')}")
        print(f"💵 Monthly Needed: {format_currency(goal_analysis.get('monthly_needed', 0))}")
        print(f"📊 % of Budget: {goal_analysis.get('percentage_of_budget', 0):.1f}%")
        print(f"✅ Assessment: {goal_analysis.get('assessment', 'Unknown')}")
        
        if goal_analysis.get('with_growth'):
            growth = goal_analysis['with_growth']
            print(f"📈 Expected Return: {growth.get('expected_return', 0):.1f}%")
            print(f"🚀 Projected Value: {format_currency(growth.get('projected_value', 0))}")


def display_generic_results(result: Dict[str, Any]):
    """Display generic results."""
    print(f"\n✅ Command completed successfully!")
    
    message = result.get('message')
    if message:
        print(f"📝 {message}")
    
    # Display any other interesting fields
    for key, value in result.items():
        if key not in ['status', 'agent_id', 'user_id', 'timestamp', 'message'] and value:
            formatted_key = key.replace('_', ' ').title()
            if isinstance(value, (list, dict)):
                print(f"📋 {formatted_key}: {len(value) if isinstance(value, list) else 'Available'}")
            else:
                print(f"📋 {formatted_key}: {value}")


def main():
    """Main CLI entry point."""
    
    print("✅ Personal Financial Agent loaded successfully")
    
    parser = argparse.ArgumentParser(
        description="Personal Financial Advisor CLI - AI-Powered Wealth Management (HushhMCP Compliant)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Set up your comprehensive financial profile
  python personal_advisor_cli_v2.py --command setup_profile --full-name "John Smith" --income 5000 --expenses 3000 --age 28 --risk moderate --occupation "Software Engineer"
  
  # Update personal information
  python personal_advisor_cli_v2.py --command update_personal_info --full-name "John A. Smith" --occupation "Senior Developer"
  
  # Analyze Apple stock with your personal context
  python personal_advisor_cli_v2.py --command personal_stock_analysis --ticker AAPL --price 175.50
  
  # View your complete profile
  python personal_advisor_cli_v2.py --command view_profile
  
  # Add a financial goal
  python personal_advisor_cli_v2.py --command add_goal --goal-name "Emergency Fund" --target-amount 10000 --target-date "2025-12-31"

Available commands:
  Personal Information:
  - setup_profile: Create comprehensive financial profile
  - update_personal_info: Update personal details
  - update_income: Update monthly income
  - set_budget: Set detailed budget categories
  - add_goal: Add investment goals
  - view_profile: View complete profile

  Investment Analysis:
  - personal_stock_analysis: Get personalized stock analysis
  - portfolio_review: Review your portfolio

  Education & Coaching:
  - explain_like_im_new: Beginner-friendly explanations
  - investment_education: Learn investment concepts
  - behavioral_coaching: Overcome investment biases
        """
    )
    
    # Required arguments
    parser.add_argument('--command', '-c', required=True,
                        choices=[
                            'setup_profile', 'update_personal_info', 'update_income', 'set_budget', 'add_goal', 'view_profile',
                            'personal_stock_analysis', 'portfolio_review', 'goal_progress_check',
                            'explain_like_im_new', 'investment_education', 'behavioral_coaching'
                        ],
                        help='Financial command to execute')
    
    # Personal Information Arguments
    parser.add_argument('--full-name', help='Full name')
    parser.add_argument('--occupation', help='Occupation/job title')
    parser.add_argument('--family-status', choices=['single', 'married', 'divorced', 'widowed'], help='Family status')
    parser.add_argument('--dependents', type=int, help='Number of dependents')
    
    # Financial Arguments
    parser.add_argument('--income', type=float, help='Monthly income')
    parser.add_argument('--expenses', type=float, help='Monthly expenses') 
    parser.add_argument('--current-savings', type=float, help='Current savings amount')
    parser.add_argument('--current-debt', type=float, help='Current debt amount')
    parser.add_argument('--investment-budget', type=float, help='Monthly investment budget')
    
    # Preference Arguments
    parser.add_argument('--age', type=int, default=30, help='Your age (default: 30)')
    parser.add_argument('--risk', choices=['conservative', 'moderate', 'aggressive'], 
                        default='moderate', help='Risk tolerance (default: moderate)')
    parser.add_argument('--experience', choices=['beginner', 'intermediate', 'advanced'], 
                        default='beginner', help='Investment experience level (default: beginner)')
    parser.add_argument('--time-horizon', choices=['short_term', 'medium_term', 'long_term'],
                        default='long_term', help='Investment time horizon (default: long_term)')
    
    # Stock Analysis Arguments
    parser.add_argument('--ticker', '-t', help='Stock ticker symbol (e.g., AAPL, MSFT)')
    parser.add_argument('--price', '-p', type=float, help='Current stock price')
    
    # Goal Arguments
    parser.add_argument('--goal-name', help='Name of the investment goal')
    parser.add_argument('--target-amount', type=float, help='Target amount for the goal')
    parser.add_argument('--target-date', help='Target date for the goal (YYYY-MM-DD)')
    parser.add_argument('--priority', choices=['low', 'medium', 'high'], 
                        default='medium', help='Goal priority (default: medium)')
    parser.add_argument('--description', help='Goal description')
    
    # Education Arguments
    parser.add_argument('--topic', help='Topic to learn about or explain')
    
    # System Arguments
    parser.add_argument('--user-id', '-u', default='cli_user_001', help='User ID for the analysis (default: cli_user_001)')
    parser.add_argument('--output', '-o', help='Output file to save results (optional)')
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    
    args = parser.parse_args()
    
    # Print CLI header
    print("💼 Personal Financial Advisor CLI - HushhMCP Compliant")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n🏦 Personal Financial Advisor")
    print(f"🔧 Command: {args.command}")
    print(f"👤 User ID: {args.user_id}")
    print("=" * 60)
    
    # Build parameters from arguments
    parameters = {}
    
    # Personal information parameters
    if args.full_name:
        parameters['full_name'] = args.full_name
    if args.occupation:
        parameters['occupation'] = args.occupation
    if args.family_status:
        parameters['family_status'] = args.family_status
    if args.dependents is not None:
        parameters['dependents'] = args.dependents
    
    # Financial parameters
    if args.income is not None:
        parameters['monthly_income'] = parameters['income'] = args.income
    if args.expenses is not None:
        parameters['monthly_expenses'] = parameters['expenses'] = args.expenses
    if args.current_savings is not None:
        parameters['current_savings'] = args.current_savings
    if args.current_debt is not None:
        parameters['current_debt'] = args.current_debt
    if args.investment_budget is not None:
        parameters['investment_budget'] = args.investment_budget
    
    # Preference parameters
    parameters['age'] = args.age
    parameters['risk_tolerance'] = parameters['risk'] = args.risk
    parameters['investment_experience'] = parameters['experience'] = args.experience
    parameters['time_horizon'] = args.time_horizon
    
    # Stock analysis parameters
    if args.ticker:
        parameters['ticker'] = args.ticker
    if args.price is not None:
        parameters['price'] = parameters['current_price'] = args.price
    
    # Goal parameters
    if args.goal_name:
        parameters['goal_name'] = args.goal_name
    if args.target_amount is not None:
        parameters['target_amount'] = args.target_amount
    if args.target_date:
        parameters['target_date'] = args.target_date
    parameters['priority'] = args.priority
    if args.description:
        parameters['description'] = args.description
    
    # Education parameters
    if args.topic:
        parameters['topic'] = args.topic
    
    try:
        # Execute the command
        result = execute_agent_command(args.user_id, args.command, parameters)
        
        # Display results
        display_results(result, args.json)
        
        # Save to file if requested
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"\n📁 Results saved to: {args.output}")
        
        if result.get('status') == 'success':
            print(f"\n✅ Command completed successfully!")
            print(f"🔒 Data stored securely in encrypted vault!")
            sys.exit(0)
        else:
            print(f"\n❌ Command failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Command interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Command failed: {str(e)}")
        if args.json:
            import json
            print(json.dumps({'status': 'error', 'error': str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
