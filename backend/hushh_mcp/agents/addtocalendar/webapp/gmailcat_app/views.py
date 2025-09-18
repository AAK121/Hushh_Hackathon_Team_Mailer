# webapp/gmailcat_app/views.py

import os
import sys
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
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
from hushh_mcp.agents.addtocalendar.manifest import manifest as calendar_manifest
from hushh_mcp.agents.mailerpanda.index import MassMailerAgent
from hushh_mcp.agents.mailerpanda.manifest import manifest as mailer_manifest
from hushh_mcp.constants import ConsentScope

# Load environment files
addtocalendar_env = os.path.join(hushh_root, 'hushh_mcp/agents/addtocalendar/.env')
mailerpanda_env = os.path.join(hushh_root, 'hushh_mcp/agents/mailerpanda/.env')
load_dotenv(dotenv_path=addtocalendar_env)
load_dotenv(dotenv_path=mailerpanda_env)

def gmail_interface(request):
    """Renders the main Gmail-like interface."""
    return render(request, 'minecraft_interface.html')

def dashboard_view(request):
    """Renders the dashboard with feature overview."""
    return render(request, 'minecraft_dashboard.html')

# ================ REST API ENDPOINTS ================

@api_view(['GET'])
def api_features(request):
    """Returns available features and agent information."""
    features = {
        'agents': {
            'gmailcat': {
                'name': calendar_manifest['name'],
                'description': calendar_manifest['description'],
                'version': calendar_manifest['version'],
                'features': [
                    'Smart Email Analysis',
                    'AI Event Extraction',
                    'Automatic Calendar Creation',
                    'Privacy-First Processing'
                ]
            },
            'mailerpanda': {
                'name': mailer_manifest['name'],
                'description': mailer_manifest['description'],
                'version': mailer_manifest['version'],
                'features': mailer_manifest.get('features', [])
            }
        },
        'capabilities': {
            'email_processing': True,
            'calendar_integration': True,
            'mass_emailing': True,
            'ai_content_generation': True,
            'human_in_loop': True,
            'consent_management': True
        }
    }
    return Response(features)

@api_view(['POST'])
def api_gmailcat_process(request):
    """Process emails and create calendar events."""
    try:
        user_id = request.data.get('user_id', 'web_user_001')
        
        # Issue consent tokens
        email_token = issue_token(
            user_id=user_id,
            agent_id=calendar_manifest["id"],
            scope=ConsentScope.VAULT_READ_EMAIL,
            expires_in_ms=3600 * 1000
        )
        
        calendar_token = issue_token(
            user_id=user_id,
            agent_id=calendar_manifest["id"],
            scope=ConsentScope.VAULT_WRITE_CALENDAR,
            expires_in_ms=3600 * 1000
        )
        
        # Execute the agent
        agent = AddToCalendarAgent()
        result = agent.handle(user_id, email_token.token, calendar_token.token)
        
        return Response({
            'status': 'success',
            'result': result,
            'message': 'Email processing completed successfully'
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def api_mailerpanda_draft(request):
    """Generate email draft using AI."""
    try:
        user_input = request.data.get('user_input', '')
        user_id = request.data.get('user_id', 'web_user_001')
        
        if not user_input:
            return Response({
                'status': 'error',
                'message': 'User input is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Issue consent token
        consent_token = issue_token(
            user_id=user_id,
            agent_id=mailer_manifest["id"],
            scope=ConsentScope.CUSTOM_TEMPORARY,
            expires_in_ms=3600 * 1000
        )
        
        # Initialize agent and generate draft
        agent = MassMailerAgent()
        
        # Create initial state for draft generation
        initial_state = {
            "user_input": user_input,
            "user_email": "",
            "mass": False,
            "subject": "",
            "email_template": "",
            "receiver_email": [],
            "user_feedback": "",
            "approved": False,
            "consent_token": consent_token.token,
            "user_id": user_id
        }
        
        # Generate draft content
        draft_result = agent._draft_content(initial_state)
        
        return Response({
            'status': 'success',
            'draft': {
                'subject': draft_result.get('subject', ''),
                'content': draft_result.get('email_template', ''),
                'mass': draft_result.get('mass', False),
                'user_email': draft_result.get('user_email', ''),
                'receiver_emails': draft_result.get('receiver_email', [])
            },
            'message': 'Email draft generated successfully'
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def api_mailerpanda_send(request):
    """Send emails using MailerPanda agent."""
    try:
        subject = request.data.get('subject', '')
        content = request.data.get('content', '')
        user_email = request.data.get('user_email', '')
        receiver_emails = request.data.get('receiver_emails', [])
        mass = request.data.get('mass', False)
        user_id = request.data.get('user_id', 'web_user_001')
        
        if not subject or not content:
            return Response({
                'status': 'error',
                'message': 'Subject and content are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Issue consent token
        consent_token = issue_token(
            user_id=user_id,
            agent_id=mailer_manifest["id"],
            scope=ConsentScope.CUSTOM_TEMPORARY,
            expires_in_ms=3600 * 1000
        )
        
        # Initialize agent
        agent = MassMailerAgent()
        
        # Create state for sending
        send_state = {
            "subject": subject,
            "email_template": content,
            "user_email": user_email,
            "receiver_email": receiver_emails,
            "mass": mass,
            "approved": True,
            "consent_token": consent_token.token,
            "user_id": user_id
        }
        
        # Send emails
        result = agent._send_emails(send_state)
        
        return Response({
            'status': 'success',
            'result': result,
            'message': 'Emails sent successfully'
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def api_mailerpanda_contacts(request):
    """Get contact list from Excel file."""
    try:
        agent = MassMailerAgent()
        contacts = agent._read_contacts()
        
        return Response({
            'status': 'success',
            'contacts': contacts,
            'total': len(contacts)
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e),
            'contacts': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def api_refine_draft(request):
    """Refine email draft based on user feedback."""
    try:
        feedback = request.data.get('feedback', '')
        current_template = request.data.get('current_template', '')
        user_id = request.data.get('user_id', 'web_user_001')
        
        if not feedback or not current_template:
            return Response({
                'status': 'error',
                'message': 'Feedback and current template are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Issue consent token
        consent_token = issue_token(
            user_id=user_id,
            agent_id=mailer_manifest["id"],
            scope=ConsentScope.CUSTOM_TEMPORARY,
            expires_in_ms=3600 * 1000
        )
        
        # Initialize agent
        agent = MassMailerAgent()
        
        # Create state for refinement
        refine_state = {
            "email_template": current_template,
            "user_feedback": feedback,
            "consent_token": consent_token.token,
            "user_id": user_id
        }
        
        # Refine draft
        refined_result = agent._draft_content(refine_state)
        
        return Response({
            'status': 'success',
            'refined_draft': {
                'subject': refined_result.get('subject', ''),
                'content': refined_result.get('email_template', ''),
                'mass': refined_result.get('mass', False),
                'user_email': refined_result.get('user_email', ''),
                'receiver_emails': refined_result.get('receiver_email', [])
            },
            'message': 'Email draft refined successfully'
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    """This view acts as the bridge between the UI and the agent."""
    if request.method == 'POST':
        try:
            user_id = "web_demo_user_001"
            
            # Issue tokens for both email reading and calendar writing
            email_consent_token = issue_token(
                user_id=user_id,
                agent_id=manifest["id"],
                scope=manifest["scopes"][0],  # VAULT_READ_EMAIL
                expires_in_ms=3600 * 1000  # 1 hour
            )
            
            calendar_consent_token = issue_token(
                user_id=user_id,
                agent_id=manifest["id"],
                scope=manifest["scopes"][1],  # VAULT_WRITE_CALENDAR
                expires_in_ms=3600 * 1000  # 1 hour
            )
            
            agent = AddToCalendarAgent()
            result = agent.handle(user_id, email_consent_token.token, calendar_consent_token.token)
            return JsonResponse({'status': 'success', 'data': result})
        except FileNotFoundError as e:
            error_message = f"Configuration Error: {e}. Have you run the 'run_agent_cli.py' script once to authenticate with Google?"
            return JsonResponse({'status': 'error', 'message': error_message}, status=500)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
