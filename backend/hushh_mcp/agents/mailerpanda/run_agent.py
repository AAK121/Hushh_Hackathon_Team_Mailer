
import os
import sys
import json
from dotenv import load_dotenv

# --- Dynamic Path Configuration ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --------------------------------

from hushh_mcp.consent.token import issue_token
from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
from hushh_mcp.agents.mailerpanda.manifest import manifest

def run():
    """Interactive AI-powered email campaign agent with human-in-the-loop approval."""
    
    # Load environment variables
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path=env_path)
    
    # Validate required environment variables
    required_vars = ["MAILJET_API_KEY", "MAILJET_API_SECRET", "GOOGLE_API_KEY"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"‼️ ERROR: Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file in the 'mailerpanda' directory.")
        return

    print("🚀 Initializing AI-Powered MailerPanda Agent with LangGraph...")
    print("🤖 Features: AI Content Generation, Human-in-the-Loop, Mass Email Support")
    print("=" * 60)

    user_id = "mailerpanda_user_001"

    # Get user input for email campaign
    print("\n📝 Email Campaign Setup:")
    user_input = input("Describe the email you want to send (e.g., 'Send congratulations to all interns for being selected'): ").strip()
    
    if not user_input:
        print("❌ No input provided. Exiting...")
        return

    # Issue consent token
    from hushh_mcp.constants import ConsentScope
    
    multi_scope_token = issue_token(
        user_id=user_id,
        agent_id=manifest["id"],
        scope=ConsentScope.CUSTOM_TEMPORARY,
        expires_in_ms=3600 * 1000  # 1 hour
    )
    print(f"✅ Consent token issued for user '{user_id}'.")

    # Initialize and run the agent
    try:
        agent = MassMailerAgent()
        # Convert single token to dictionary format expected by handle method
        consent_tokens = {
            'email_send': multi_scope_token.token,
            'vault_write': multi_scope_token.token
        }
        result = agent.handle(user_id, consent_tokens, user_input)
        
        print("\n🎉 Email Campaign Agent Execution Complete!")
        print("📊 Final Results:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"\n💥 An error occurred: {e}")
        import traceback
        traceback.print_exc()

def run_predefined_campaign():
    """Runs a predefined email campaign for quick testing."""
    
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path=env_path)
    
    if not os.environ.get("MAILJET_API_KEY"):
        print("‼️ ERROR: Mailjet API keys are not set.")
        return

    print("🚀 Running Predefined Email Campaign...")

    user_id = "mailerpanda_user_001"
    
    # Predefined campaign
    user_input = "Send emails to all contacts to congratulate them on being selected for internships. Make it professional and warm."

    from hushh_mcp.constants import ConsentScope
    
    multi_scope_token = issue_token(
        user_id=user_id,
        agent_id=manifest["id"],
        scope=ConsentScope.CUSTOM_TEMPORARY,
        expires_in_ms=3600 * 1000
    )

    try:
        agent = MassMailerAgent()
        result = agent.handle(user_id, multi_scope_token.token, user_input)
        print("📊 Results:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    # Check for command line argument
    if len(sys.argv) > 1 and sys.argv[1] == "--predefined":
        run_predefined_campaign()
    else:
        run()
