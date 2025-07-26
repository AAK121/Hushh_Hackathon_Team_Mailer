from django.contrib import admin
from .models import Conversation, Message, EmailTemplate, EmailCampaign, EmailLog

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['session_id']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'message_type', 'content_preview', 'timestamp']
    list_filter = ['message_type', 'timestamp']
    search_fields = ['content', 'conversation__session_id']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['subject', 'conversation', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['subject', 'content']
    readonly_fields = ['created_at']

@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    list_display = ['email_template', 'status', 'total_emails', 'sent_emails', 'failed_emails', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['email_template__subject']
    readonly_fields = ['created_at', 'completed_at']

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['recipient_email', 'recipient_name', 'status', 'status_code', 'sent_at']
    list_filter = ['status', 'sent_at']
    search_fields = ['recipient_email', 'recipient_name']
    readonly_fields = ['sent_at']
