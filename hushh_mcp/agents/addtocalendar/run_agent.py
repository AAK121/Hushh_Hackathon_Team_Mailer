# hushh_mcp/agents/addtocalendar/run_agent.py

import os
import sys
import json
from dotenv import load_dotenv
 
# --- Dynamic Path Configuration ---
# This ensures the script can find the 'hushh_mcp' package from its new location.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --------------------------------

from hushh_mcp.consent.token import issue_token
from hushh_mcp.agents.addtocalendar.index import AddToCalendarAgent
from hushh_mcp.agents.addtocalendar.manifest import manifest

def run():
    """Issues a consent token and executes the agent."""
    # Load .env file from the project root directory
    env_path = os.path.join(project_root, '.env')
    load_dotenv(env_path)
    print("🚀 Initializing Self-Contained Calendar Agent...")

    user_id = "demo_user_encapsulated_001"

    # 1. Issue tokens with all required permissions.
    # Issue tokens for both email reading and calendar writing
    email_consent_token = issue_token(
        user_id=user_id,
        agent_id=manifest["id"],
        scope=manifest["scopes"][0],  # VAULT_READ_EMAIL
        expires_in_ms=3600 * 1000  # 1 hour
    )
    print(f"✅ Email consent token issued for user '{user_id}' with scope '{manifest['scopes'][0].value}'.")
    
    calendar_consent_token = issue_token(
        user_id=user_id,
        agent_id=manifest["id"],
        scope=manifest["scopes"][1],  # VAULT_WRITE_CALENDAR
        expires_in_ms=3600 * 1000  # 1 hour
    )
    print(f"✅ Calendar consent token issued for user '{user_id}' with scope '{manifest['scopes'][1].value}'.")

    # 2. Initialize and run the agent.
    try:
        agent = AddToCalendarAgent()
        result = agent.handle(user_id, email_consent_token.token, calendar_consent_token.token)
        print("\n🎉 Agent execution finished.")
        print("📊 Results:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"\n💥 An error occurred: {e}")

if __name__ == "__main__":
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("‼️ ERROR: OPENAI_API_KEY is not properly set.")
        print("📝 Please:")
        print("   1. Get your API key from https://platform.openai.com/account/api-keys")
        print("   2. Update the OPENAI_API_KEY in the .env file")
        print("   3. Uncomment the line by removing the # at the beginning")
    else:
        run()