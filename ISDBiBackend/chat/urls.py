
# chat/urls.py

from django.urls import path
from .views import ChatHistoryView

urlpatterns = [
    path('history/<str:chat_id>/', ChatHistoryView.as_view(), name='chat_history'),
]
