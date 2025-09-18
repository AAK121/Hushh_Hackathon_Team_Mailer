#!/usr/bin/env python3
"""
Personal Financial Advisor CLI
=============================

Command-line interface for the enhanced ChanduFinance Personal Financial Agent.
Helps users set up their financial profile, analyze investments with personal context,
and receive AI-powered personalized financial advice.

Usage Examples:
    # Set up financial profile
    python personal_advisor_cli.py --command setup_profile --income 5000 --expenses 3000 --age 28 --risk moderate

    # Analyze a stock with personal context  
    python personal_advisor_cli.py --command personal_stock_analysis --ticker AAPL --price 175.50

    # Get personalized investment education
    python personal_advisor_cli.py --command explain_like_im_new --ticker MSFT

    # Add investment goal
    python personal_advisor_cli.py --command add_goal --goal-name "House Down Payment" --target-amount 50000 --target-date "2026-12-31"
"""

import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the Personal Financial Agent
try:
    from hushh_mcp.agents.chandufinance.index import PersonalFinancialAgent, run_agent
    print("✅ Personal Financial Agent loaded successfully")
except ImportError as e:
    print(f"❌ Failed to import Personal Financial Agent: {e}")
    sys.exit(1)


class PersonalFinancialCLI:
    """Command-line interface for the Personal Financial Agent."""
    
    def __init__(self):
        self.agent = PersonalFinancialAgent()
        
    def run_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Run a financial analysis command with personal context.
        
        Args:
            command: Command to execute
            **kwargs: Additional parameters for the command
            
        Returns:
            Dictionary containing analysis results
        """
        # Generate user ID and token for CLI usage
        user_id = kwargs.get('user_id', 'cli_user_001')
        token = kwargs.get('token', 'HCT:personal_finance_token_for_cli.signature')
        
        # Prepare parameters
        parameters = {
            'command': command,
            **kwargs
        }
        
        # Remove non-parameter keys
        for key in ['user_id', 'token']:
            parameters.pop(key, None)
        
        print(f"🏦 Personal Financial Advisor")
        print(f"🔧 Command: {command}")
        print(f"👤 User ID: {user_id}")
        print("=" * 60)
        
        # Execute the agent
        try:
            result = self.agent.handle(
                user_id=user_id,
                token=token,
                parameters=parameters
            )
            
            return result
            
        except Exception as e:
            return {
                'status': 'error',
                'agent_id': 'personal_financial_agent',
                'error': f'CLI execution failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def format_profile_setup(self, results: Dict[str, Any]) -> str:
        """Format profile setup results for CLI display."""
        if results.get('status') != 'success':
            return f"❌ Error: {results.get('error', 'Unknown error')}"
        
        output = []
        output.append("🎉 FINANCIAL PROFILE CREATED!")
        output.append("=" * 50)
        
        # Profile Summary
        if 'profile_summary' in results:
            summary = results['profile_summary']
            output.append("📊 YOUR FINANCIAL SNAPSHOT:")
            output.append("-" * 30)
            output.append(f"💰 Monthly Income: {summary.get('monthly_income', 'N/A')}")
            output.append(f"💸 Monthly Expenses: {summary.get('monthly_expenses', 'N/A')}")
            output.append(f"📈 Savings Rate: {summary.get('savings_rate', 'N/A')}")
            output.append(f"💼 Investment Budget: {summary.get('investment_budget', 'N/A')}")
            output.append(f"⚖️ Risk Tolerance: {summary.get('risk_tolerance', 'N/A')}")
            output.append(f"🎓 Experience Level: {summary.get('experience_level', 'N/A')}")
        
        # Welcome Message
        if 'welcome_message' in results:
            output.append(f"\n💬 PERSONALIZED MESSAGE:")
            output.append("-" * 30)
            output.append(results['welcome_message'])
        
        # Next Steps
        if 'next_steps' in results:
            output.append(f"\n🎯 RECOMMENDED NEXT STEPS:")
            output.append("-" * 30)
            for i, step in enumerate(results['next_steps'], 1):
                output.append(f"{i}. {step}")
        
        return "\n".join(output)
    
    def format_stock_analysis(self, results: Dict[str, Any]) -> str:
        """Format personalized stock analysis for CLI display."""
        if results.get('status') != 'success':
            return f"❌ Error: {results.get('error', 'Unknown error')}"
        
        output = []
        output.append(f"📊 PERSONAL STOCK ANALYSIS: {results.get('ticker', 'N/A')}")
        output.append("=" * 60)
        
        # Basic Info
        output.append(f"💰 Current Price: ${results.get('current_price', 0):.2f}")
        
        # Personal Analysis
        if 'personal_analysis' in results:
            output.append(f"\n🧠 AI-POWERED PERSONAL ANALYSIS:")
            output.append("-" * 40)
            output.append(results['personal_analysis'])
        
        # Position Sizing
        if 'position_sizing' in results:
            sizing = results['position_sizing']
            output.append(f"\n💼 POSITION SIZING RECOMMENDATION:")
            output.append("-" * 40)
            output.append(f"💵 Max Position Value: ${sizing.get('max_position_value', 0):,.2f}")
            output.append(f"📈 Max Shares: {sizing.get('max_shares', 0):,}")
            output.append(f"📊 Allocation %: {sizing.get('allocation_percentage', 0):.1%}")
            output.append(f"💡 Reasoning: {sizing.get('reasoning', 'N/A')}")
        
        # Risk Assessment
        if 'risk_assessment' in results:
            risk = results['risk_assessment']
            output.append(f"\n⚠️ PERSONAL RISK ASSESSMENT:")
            output.append("-" * 40)
            output.append(f"🎯 Overall Risk: {risk.get('overall_risk', 'N/A')}")
            output.append(f"📊 Suitability Score: {risk.get('suitability_score', 0)}/100")
            if risk.get('risk_factors'):
                output.append("⚠️ Risk Factors for You:")
                for factor in risk['risk_factors']:
                    output.append(f"  • {factor}")
        
        # Goal Alignment
        if 'goal_alignment' in results:
            alignment = results['goal_alignment']
            output.append(f"\n🎯 GOAL ALIGNMENT:")
            output.append("-" * 40)
            output.append(f"📊 Alignment Score: {alignment.get('alignment_score', 0)}/100")
            if alignment.get('aligned_goals'):
                for goal in alignment['aligned_goals']:
                    output.append(f"✅ {goal}")
        
        return "\n".join(output)
    
    def format_goal_addition(self, results: Dict[str, Any]) -> str:
        """Format goal addition results for CLI display."""
        if results.get('status') != 'success':
            return f"❌ Error: {results.get('error', 'Unknown error')}"
        
        output = []
        output.append("🎯 INVESTMENT GOAL ADDED!")
        output.append("=" * 40)
        
        if 'goal_details' in results:
            goal = results['goal_details']
            output.append(f"📝 Goal Name: {goal.get('name', 'N/A')}")
            output.append(f"💰 Target Amount: ${goal.get('target_amount', 0):,.2f}")
            output.append(f"📅 Target Date: {goal.get('target_date', 'N/A')}")
            output.append(f"⭐ Priority: {goal.get('priority', 'N/A')}")
        
        if 'feasibility_analysis' in results:
            output.append(f"\n📊 FEASIBILITY ANALYSIS:")
            output.append("-" * 30)
            output.append(results['feasibility_analysis'])
        
        if 'investment_strategy' in results:
            output.append(f"\n💡 RECOMMENDED STRATEGY:")
            output.append("-" * 30)
            output.append(results['investment_strategy'])
        
        return "\n".join(output)
    
    def format_education(self, results: Dict[str, Any]) -> str:
        """Format investment education results for CLI display."""
        if results.get('status') != 'success':
            return f"❌ Error: {results.get('error', 'Unknown error')}"
        
        output = []
        output.append("🎓 INVESTMENT EDUCATION")
        output.append("=" * 40)
        
        if 'education_content' in results:
            output.append(results['education_content'])
        elif 'explanation' in results:
            output.append(results['explanation'])
        else:
            output.append("Educational content generated based on your profile and experience level.")
        
        return "\n".join(output)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Personal Financial Advisor CLI - AI-Powered Wealth Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Set up your financial profile
  python personal_advisor_cli.py --command setup_profile --income 5000 --expenses 3000 --age 28 --risk moderate

  # Analyze Apple stock with your personal context
  python personal_advisor_cli.py --command personal_stock_analysis --ticker AAPL --price 175.50

  # Get beginner-friendly explanation of a stock
  python personal_advisor_cli.py --command explain_like_im_new --ticker MSFT --topic "dividend investing"

  # Add a financial goal
  python personal_advisor_cli.py --command add_goal --goal-name "Emergency Fund" --target-amount 10000 --target-date "2025-12-31"

  # Update your income
  python personal_advisor_cli.py --command update_income --income 6000

Available commands:
  Personal Finance:
  - setup_profile: Create your financial profile
  - update_income: Update your monthly income
  - set_budget: Set detailed budget categories
  - add_goal: Add investment goals
  
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
                           'setup_profile', 'update_income', 'set_budget', 'add_goal',
                           'personal_stock_analysis', 'portfolio_review', 'goal_progress_check',
                           'explain_like_im_new', 'investment_education', 'behavioral_coaching'
                       ],
                       help='Financial command to execute')
    
    # Profile setup parameters
    parser.add_argument('--income', type=float, 
                       help='Monthly income (for profile setup)')
    parser.add_argument('--expenses', type=float,
                       help='Monthly expenses (for profile setup)')
    parser.add_argument('--age', type=int, default=30,
                       help='Your age (default: 30)')
    parser.add_argument('--risk', choices=['conservative', 'moderate', 'aggressive'], default='moderate',
                       help='Risk tolerance (default: moderate)')
    parser.add_argument('--experience', choices=['beginner', 'intermediate', 'advanced'], default='beginner',
                       help='Investment experience level (default: beginner)')
    parser.add_argument('--investment-budget', type=float,
                       help='Monthly investment budget')
    
    # Stock analysis parameters
    parser.add_argument('--ticker', '-t',
                       help='Stock ticker symbol (e.g., AAPL, MSFT)')
    parser.add_argument('--price', '-p', type=float,
                       help='Current stock price')
    
    # Goal parameters
    parser.add_argument('--goal-name',
                       help='Name of the investment goal')
    parser.add_argument('--target-amount', type=float,
                       help='Target amount for the goal')
    parser.add_argument('--target-date',
                       help='Target date for the goal (YYYY-MM-DD)')
    parser.add_argument('--priority', choices=['low', 'medium', 'high'], default='medium',
                       help='Goal priority (default: medium)')
    
    # Education parameters
    parser.add_argument('--topic',
                       help='Topic to learn about or explain')
    
    # Output options
    parser.add_argument('--user-id', '-u', default='cli_user_001',
                       help='User ID for the analysis (default: cli_user_001)')
    parser.add_argument('--output', '-o',
                       help='Output file to save results (optional)')
    parser.add_argument('--json', action='store_true',
                       help='Output results in JSON format')
    
    args = parser.parse_args()
    
    # Initialize CLI
    cli = PersonalFinancialCLI()
    
    # Prepare command parameters
    command_params = {
        'user_id': args.user_id,
    }
    
    # Add parameters based on command
    if args.command == 'setup_profile':
        command_params.update({
            'monthly_income': args.income or 0.0,
            'monthly_expenses': args.expenses or 0.0,
            'age': args.age,
            'risk_tolerance': args.risk,
            'investment_experience': args.experience,
            'investment_budget': args.investment_budget or 0.0,
            'investment_goals': []
        })
    elif args.command == 'personal_stock_analysis':
        if not args.ticker:
            print("❌ Error: --ticker is required for stock analysis")
            sys.exit(1)
        command_params.update({
            'ticker': args.ticker,
            'current_price': args.price or 100.0
        })
    elif args.command == 'add_goal':
        if not args.goal_name or not args.target_amount:
            print("❌ Error: --goal-name and --target-amount are required for adding goals")
            sys.exit(1)
        command_params.update({
            'goal_name': args.goal_name,
            'target_amount': args.target_amount,
            'target_date': args.target_date or '',
            'priority': args.priority
        })
    elif args.command == 'update_income':
        if not args.income:
            print("❌ Error: --income is required for updating income")
            sys.exit(1)
        command_params.update({
            'monthly_income': args.income
        })
    elif args.command in ['explain_like_im_new', 'investment_education']:
        command_params.update({
            'ticker': args.ticker,
            'topic': args.topic or ''
        })
    
    # Run the command
    print(f"💼 Personal Financial Advisor CLI")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    results = cli.run_command(args.command, **command_params)
    
    # Format and display results
    if args.json:
        formatted_output = json.dumps(results, indent=2)
    else:
        if args.command == 'setup_profile':
            formatted_output = cli.format_profile_setup(results)
        elif args.command == 'personal_stock_analysis':
            formatted_output = cli.format_stock_analysis(results)
        elif args.command == 'add_goal':
            formatted_output = cli.format_goal_addition(results)
        elif args.command in ['explain_like_im_new', 'investment_education', 'behavioral_coaching']:
            formatted_output = cli.format_education(results)
        else:
            formatted_output = json.dumps(results, indent=2)
    
    print(formatted_output)
    
    # Save to file if requested
    if args.output:
        try:
            with open(args.output, 'w') as f:
                if args.json:
                    json.dump(results, f, indent=2)
                else:
                    f.write(formatted_output)
            print(f"\n💾 Results saved to: {args.output}")
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")
    
    # Display status
    if results.get('status') == 'success':
        print(f"\n✅ Command completed successfully!")
    else:
        print(f"\n❌ Command failed: {results.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
