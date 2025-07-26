import json
import uuid
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Conversation, Message, EmailTemplate, EmailCampaign, EmailLog
from .services import MailerService
import os
from datetime import datetime

class ChatView(TemplateView):
    template_name = 'mailer/chat.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Hushh Mailer Agent'
        return context

@method_decorator(csrf_exempt, name='dispatch')
class SendMessageView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            session_id = data.get('session_id')
            
            if not user_message:
                return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get or create session
            if not session_id:
                session_id = str(uuid.uuid4())
            
            conversation, created = Conversation.objects.get_or_create(session_id=session_id)
            
            # Save user message
            user_msg = Message.objects.create(
                conversation=conversation,
                message_type='user',
                content=user_message
            )
            
            # Initialize mailer service
            mailer_service = MailerService()
            
            # Check if this is feedback for existing template
            last_message = Message.objects.filter(
                conversation=conversation,
                message_type='assistant'
            ).order_by('-timestamp').first()
            
            feedback = None
            if last_message and 'email template' in last_message.content.lower():
                feedback = user_message
            
            # Generate response
            if user_message.lower() in ['yes', 'approve', 'approved', 'y', 'looks good', 'perfect']:
                # User approved the template
                assistant_response = "Great! Your email template has been approved. You can now upload an Excel file with your contact list to send the emails."
                
                # Mark the last template as approved
                last_template = EmailTemplate.objects.filter(conversation=conversation).order_by('-created_at').first()
                if last_template:
                    last_template.is_approved = True
                    last_template.save()
                    
            elif feedback and last_message:
                # User provided feedback, regenerate template
                result = mailer_service.generate_email_template(
                    user_input="Update the email template",
                    feedback=feedback
                )
                
                # Create new template
                email_template = EmailTemplate.objects.create(
                    conversation=conversation,
                    subject=result['subject'],
                    content=result['template'],
                    placeholders=result['placeholders'],
                    is_approved=False
                )
                
                assistant_response = f"""I've updated your email template based on your feedback:

**Subject:** {result['subject']}

**Email Content:**
{result['template']}

**Detected Placeholders:** {', '.join(['{' + p + '}' for p in result['placeholders']])}

Does this look better? You can approve it or provide more feedback."""
                
            else:
                # Generate new email template
                result = mailer_service.generate_email_template(user_input=user_message)
                
                # Save email template
                email_template = EmailTemplate.objects.create(
                    conversation=conversation,
                    subject=result['subject'],
                    content=result['template'],
                    placeholders=result['placeholders'],
                    is_approved=False
                )
                
                assistant_response = f"""I've created an email template for you:

**Subject:** {result['subject']}

**Email Content:**
{result['template']}

**Detected Placeholders:** {', '.join(['{' + p + '}' for p in result['placeholders']])}

Does this look good? You can approve it or provide feedback to improve it."""
            
            # Save assistant response
            Message.objects.create(
                conversation=conversation,
                message_type='assistant',
                content=assistant_response
            )
            
            return Response({
                'response': assistant_response,
                'session_id': session_id,
                'conversation_id': conversation.id
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class UploadExcelView(APIView):
    def post(self, request):
        try:
            session_id = request.POST.get('session_id')
            excel_file = request.FILES.get('excel_file')
            
            if not session_id or not excel_file:
                return Response({'error': 'Session ID and Excel file are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get conversation
            try:
                conversation = Conversation.objects.get(session_id=session_id)
            except Conversation.DoesNotExist:
                return Response({'error': 'Invalid session'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if there's an approved template
            approved_template = EmailTemplate.objects.filter(
                conversation=conversation,
                is_approved=True
            ).order_by('-created_at').first()
            
            if not approved_template:
                return Response({'error': 'Please approve an email template first'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Save file
            file_name = f"excel_{uuid.uuid4()}_{excel_file.name}"
            file_path = default_storage.save(f'excel_uploads/{file_name}', ContentFile(excel_file.read()))
            full_file_path = default_storage.path(file_path)
            
            # Process Excel file
            mailer_service = MailerService()
            contacts = mailer_service.process_excel_file(full_file_path)
            
            if not contacts:
                return Response({'error': 'No valid contacts found in Excel file'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create email campaign
            campaign = EmailCampaign.objects.create(
                conversation=conversation,
                email_template=approved_template,
                total_emails=len(contacts),
                excel_file=file_path
            )
            
            # Create email logs for each contact
            for contact in contacts:
                EmailLog.objects.create(
                    campaign=campaign,
                    recipient_email=contact.get('email', ''),
                    recipient_name=contact.get('name', ''),
                    status='pending'
                )
            
            # Save message about upload
            Message.objects.create(
                conversation=conversation,
                message_type='assistant',
                content=f"Excel file uploaded successfully! Found {len(contacts)} contacts. Ready to send emails. Click 'Send Emails' to proceed."
            )
            
            return Response({
                'message': f'Excel file processed successfully. Found {len(contacts)} contacts.',
                'contacts_count': len(contacts),
                'campaign_id': campaign.id,
                'preview_contacts': contacts[:5]  # Show first 5 for preview
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class SendEmailsView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            campaign_id = data.get('campaign_id')
            
            if not session_id or not campaign_id:
                return Response({'error': 'Session ID and Campaign ID are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get campaign
            try:
                campaign = EmailCampaign.objects.get(id=campaign_id)
                conversation = Conversation.objects.get(session_id=session_id)
            except (EmailCampaign.DoesNotExist, Conversation.DoesNotExist):
                return Response({'error': 'Invalid campaign or session'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Update campaign status
            campaign.status = 'sending'
            campaign.save()
            
            # Get contacts from Excel file
            mailer_service = MailerService()
            file_path = campaign.excel_file.path
            contacts = mailer_service.process_excel_file(file_path)
            
            # Send emails
            sent_count = 0
            failed_count = 0
            
            for contact in contacts:
                try:
                    # Fill template with contact data
                    content = campaign.email_template.content
                    subject = campaign.email_template.subject
                    
                    # Replace placeholders
                    for placeholder in campaign.email_template.placeholders:
                        placeholder_value = contact.get(placeholder, f'[{placeholder}]')
                        content = content.replace(f'{{{placeholder}}}', str(placeholder_value))
                        subject = subject.replace(f'{{{placeholder}}}', str(placeholder_value))
                    
                    # Send email
                    result = mailer_service.send_email_via_mailjet(
                        to_email=contact['email'],
                        to_name=contact.get('name', ''),
                        subject=subject,
                        content=content
                    )
                    
                    # Update email log
                    email_log = EmailLog.objects.filter(
                        campaign=campaign,
                        recipient_email=contact['email']
                    ).first()
                    
                    if email_log:
                        if result['success']:
                            email_log.status = 'sent'
                            email_log.status_code = result['status_code']
                            email_log.sent_at = datetime.now()
                            sent_count += 1
                        else:
                            email_log.status = 'failed'
                            email_log.status_code = result.get('status_code', 500)
                            email_log.error_message = result.get('error', 'Unknown error')
                            failed_count += 1
                        email_log.save()
                
                except Exception as e:
                    failed_count += 1
                    # Log error
                    email_log = EmailLog.objects.filter(
                        campaign=campaign,
                        recipient_email=contact.get('email', '')
                    ).first()
                    if email_log:
                        email_log.status = 'failed'
                        email_log.error_message = str(e)
                        email_log.save()
            
            # Update campaign
            campaign.sent_emails = sent_count
            campaign.failed_emails = failed_count
            campaign.status = 'completed' if failed_count == 0 else 'failed'
            campaign.completed_at = datetime.now()
            campaign.save()
            
            # Send completion message
            Message.objects.create(
                conversation=conversation,
                message_type='assistant',
                content=f"Email campaign completed! ✅ {sent_count} emails sent successfully, ❌ {failed_count} failed."
            )
            
            return Response({
                'message': f'Email campaign completed!',
                'sent_count': sent_count,
                'failed_count': failed_count,
                'total_count': len(contacts)
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
