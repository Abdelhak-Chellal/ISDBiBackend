
# chat/urls.py

from django.urls import path
from .views import ChatHistoryView, ChatIDListView

urlpatterns = [
    path('history/<str:chat_id>/', ChatHistoryView.as_view(), name='chat_history'),
    path("chat-ids/", ChatIDListView.as_view(), name="chat-id-list"),

]
