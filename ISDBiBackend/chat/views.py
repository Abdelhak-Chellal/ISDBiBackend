# chat/views.py

from rest_framework.generics import ListAPIView
from .models import ChatMessage
from .serializers import ChatMessageSerializer

class ChatHistoryView(ListAPIView):
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        chat_id = self.kwargs["chat_id"]
        return ChatMessage.objects.filter(chat_id=chat_id)
