# webapp/gmailcat_app/urls.py

from django.urls import path
from . import views

app_name = 'gmailcat_app'

urlpatterns = [
    # Main UI Views
    path('', views.gmail_interface, name='gmail_interface'),  # Main Gmail-like interface
    path('dashboard/', views.dashboard_view, name='dashboard'),  # Admin dashboard
    
    # REST API Endpoints
    path('api/features/', views.api_features, name='api_features'),
    
    # GmailCat API
    path('api/gmailcat/process/', views.api_gmailcat_process, name='api_gmailcat_process'),
    
    # MailerPanda API
    path('api/mailerpanda/draft/', views.api_mailerpanda_draft, name='api_mailerpanda_draft'),
    path('api/mailerpanda/send/', views.api_mailerpanda_send, name='api_mailerpanda_send'),
    path('api/mailerpanda/contacts/', views.api_mailerpanda_contacts, name='api_mailerpanda_contacts'),
    path('api/mailerpanda/refine/', views.api_refine_draft, name='api_refine_draft'),
]
