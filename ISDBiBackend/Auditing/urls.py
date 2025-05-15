# Auditing/urls.py

from django.urls import path
from .views import AuditingPromptView

urlpatterns = [
    path('prompt/', AuditingPromptView.as_view(), name='auditing-prompt'),
]
