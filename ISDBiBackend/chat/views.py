# chat/views.py

from rest_framework.generics import ListAPIView
from .models import ChatMessage
from .serializers import ChatMessageSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class ChatHistoryView(ListAPIView):
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        chat_id = self.kwargs["chat_id"]
        return ChatMessage.objects.filter(chat_id=chat_id)



class ChatIDListView(APIView):
    def get(self, request):
        chat_ids = ChatMessage.objects.values_list("chat_id", flat=True).distinct()
        return Response({"chat_ids": list(chat_ids)}, status=status.HTTP_200_OK)
