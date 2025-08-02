# webapp/gmailcat_app/urls.py

from django.urls import path
from . import views

app_name = 'gmailcat_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('run-agent/', views.run_agent_view, name='run_agent'),
]
