from django.db import models
import json

class Conversation(models.Model):
    session_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Conversation {self.session_id}"

class Message(models.Model):
    MESSAGE_TYPES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."

class EmailTemplate(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='email_templates')
    subject = models.CharField(max_length=255)
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    placeholders = models.JSONField(default=list, blank=True)  # Store placeholder names like ['name', 'email', 'company_name']
    
    def __str__(self):
        return f"Template: {self.subject}"

class EmailCampaign(models.Model):
    CAMPAIGN_STATUS = [
        ('draft', 'Draft'),
        ('sending', 'Sending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='campaigns')
    email_template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=CAMPAIGN_STATUS, default='draft')
    total_emails = models.IntegerField(default=0)
    sent_emails = models.IntegerField(default=0)
    failed_emails = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    excel_file = models.FileField(upload_to='excel_uploads/', null=True, blank=True)
    
    def __str__(self):
        return f"Campaign: {self.email_template.subject} - {self.status}"

class EmailLog(models.Model):
    EMAIL_STATUS = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    campaign = models.ForeignKey(EmailCampaign, on_delete=models.CASCADE, related_name='email_logs')
    recipient_email = models.EmailField()
    recipient_name = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=10, choices=EMAIL_STATUS, default='pending')
    status_code = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Email to {self.recipient_email} - {self.status}"
