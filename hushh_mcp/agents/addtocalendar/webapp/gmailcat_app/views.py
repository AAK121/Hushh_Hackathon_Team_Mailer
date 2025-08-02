# webapp/gmailcat_app/views.py

import os
import sys
from django.shortcuts import render
from django.http import JsonResponse
from dotenv import load_dotenv

# --- Dynamic Path Configuration ---
# This ensures the module can be found regardless of how the server is run.
# It navigates up from this file's location to the project's root directory.
hushh_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
if hushh_root not in sys.path:
    sys.path.insert(0, hushh_root)
# --------------------------------

# Now we can import from the hushh_mcp package
from hushh_mcp.consent.token import issue_token
from hushh_mcp.agents.addtocalendar.index import AddToCalendarAgent
from hushh_mcp.agents.addtocalendar.manifest import manifest

# Load the .env file from the agent's root directory
dotenv_path = os.path.join(hushh_root, 'hushh_mcp/agents/addtocalendar/.env')
load_dotenv(dotenv_path=dotenv_path)

def index(request):
    """Renders the main chat interface."""
    return render(request, 'index.html')

def run_agent_view(request):
    """This view acts as the bridge between the UI and the agent."""
    if request.method == 'POST':
        try:
            user_id = "web_demo_user_001"
            consent_token = issue_token(
                user_id=user_id,
                agent_id=manifest["id"],
                scope=manifest["scopes"],
                expires_in_ms=600 * 1000
            )
            agent = AddToCalendarAgent()
            result = agent.handle(user_id, consent_token.token)
            return JsonResponse({'status': 'success', 'data': result})
        except FileNotFoundError as e:
            error_message = f"Configuration Error: {e}. Have you run the 'run_agent_cli.py' script once to authenticate with Google?"
            return JsonResponse({'status': 'error', 'message': error_message}, status=500)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
