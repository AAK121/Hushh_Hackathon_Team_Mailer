# hushh_mcp/agents/addtocalendar/run_agent_cli.py

import os
import sys
import json
from dotenv import load_dotenv

# --- Dynamic Path Configuration ---
# This allows the script to find the 'hushh_mcp' package
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --------------------------------

from hushh_mcp.consent.token import issue_token
from hushh_mcp.agents.addtocalendar.index import AddToCalendarAgent
from hushh_mcp.agents.addtocalendar.manifest import manifest

def run_cli():
    """
    Runs the agent from the command line.
    This is REQUIRED for the first-time Google Authentication flow.
    """
    load_dotenv()
    print("🚀 Running Agent CLI for initial Google Authentication...")
    user_id = "cli_auth_user"

    consent_token = issue_token(
        user_id=user_id,
        agent_id=manifest["id"],
        scope=manifest["scopes"],
        expires_in_ms=600 * 1000 # 10 minutes
    )
    print("✅ Consent token issued for auth.")

    try:
        agent = AddToCalendarAgent()
        # We only need to initialize the agent to trigger the auth flow.
        # The handle method doesn't need to be called here.
        agent._get_google_service('gmail', 'v1', ['https://www.googleapis.com/auth/gmail.readonly'], user_id)
        agent._get_google_service('calendar', 'v3', ['https://www.googleapis.com/auth/calendar.events'], user_id)
        print("\n✅ Google Authentication successful. Token files have been created.")
        print("You can now run the web application.")
    except Exception as e:
        print(f"\n💥 An error occurred during authentication: {e}")

if __name__ == "__main__":
    run_cli()
