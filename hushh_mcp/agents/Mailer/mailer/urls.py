from django.urls import path
from . import views

app_name = 'mailer'

urlpatterns = [
    path('', views.ChatView.as_view(), name='chat'),
    path('api/send-message/', views.SendMessageView.as_view(), name='send_message'),
    path('api/upload-excel/', views.UploadExcelView.as_view(), name='upload_excel'),
    path('api/send-emails/', views.SendEmailsView.as_view(), name='send_emails'),
]
