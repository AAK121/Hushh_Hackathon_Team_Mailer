#!/usr/bin/env python3
"""
Interactive demo script for the enhanced MailerPanda agent.
Showcases all advanced features including human-in-the-loop and AI content generation.
"""

import os
import sys
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from hushh_mcp.consent.token import issue_token
from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
from hushh_mcp.agents.mailerpanda.manifest import manifest
from hushh_mcp.constants import ConsentScope

def demo_interactive():
    """Interactive demo showcasing all features."""
    
    # Load environment
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path=env_path)
    
    print("🤖 MailerPanda Agent - Interactive Demo")
    print("=" * 50)
    print("🚀 Features:")
    print("   • AI-powered content generation (Gemini)")
    print("   • Human-in-the-loop approval workflow")
    print("   • LangGraph state management")
    print("   • Mass email with Excel placeholders")
    print("   • HushMCP consent validation")
    print("   • Real-time feedback integration")
    print("=" * 50)
    
    # Demo scenarios
    scenarios = [
        "Send congratulations to all interns for being selected for our program",
        "Send a welcome email to new team members with their training schedule",
        "Send a reminder to all contacts about the upcoming company meeting",
        "Send personalized thank you notes to all workshop participants"
    ]
    
    print("\n📝 Choose a scenario or enter your own:")
    for i, scenario in enumerate(scenarios, 1):
        print(f"   {i}. {scenario}")
    print("   5. Enter custom message")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice in ['1', '2', '3', '4']:
        user_input = scenarios[int(choice) - 1]
    elif choice == '5':
        user_input = input("Enter your custom email request: ").strip()
    else:
        print("❌ Invalid choice. Using default scenario.")
        user_input = scenarios[0]
    
    print(f"\n✅ Selected: {user_input}")
    
    # Issue consent token
    user_id = "demo_user_001"
    token = issue_token(
        user_id=user_id,
        agent_id=manifest["id"],
        scope=ConsentScope.CUSTOM_TEMPORARY,
        expires_in_ms=3600 * 1000
    )
    
    print(f"🔐 Consent token issued for user '{user_id}'")
    
    # Run the agent
    try:
        agent = MassMailerAgent()
        print("\n🎯 Starting LangGraph workflow...")
        result = agent.handle(user_id, token.token, user_input)
        
        print("\n🎉 Demo completed successfully!")
        print("📊 Summary:")
        if result.get("final_state", {}).get("approved"):
            print("   ✅ Email approved and sent")
            final_state = result["final_state"]
            if final_state.get("mass"):
                print("   📊 Mass email mode (using Excel file)")
            else:
                print(f"   👤 Individual emails to: {final_state.get('receiver_email', [])}")
        else:
            print("   ❌ Email was not approved or process was cancelled")
            
    except Exception as e:
        print(f"\n💥 Demo error: {e}")
        import traceback
        traceback.print_exc()

def demo_features():
    """Showcase individual features."""
    
    print("\n🔧 Feature Showcase:")
    print("1. 🤖 AI Content Generation - Uses Gemini to draft professional emails")
    print("2. 👨‍💼 Human-in-the-Loop - Requires human approval before sending")
    print("3. 🔄 Iterative Feedback - Allows multiple rounds of refinement")
    print("4. 📊 Mass Email Support - Processes Excel files with placeholders")
    print("5. 🔐 Consent Validation - Every operation requires explicit permission")
    print("6. 📈 LangGraph Workflow - Structured state management and routing")
    
    print("\n🛠️ Technical Stack:")
    print("   • LangGraph for workflow orchestration")
    print("   • Google Gemini for AI content generation")
    print("   • Mailjet for email delivery")
    print("   • HushMCP for consent management")
    print("   • Pandas for Excel processing")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--features":
        demo_features()
    else:
        demo_interactive()
