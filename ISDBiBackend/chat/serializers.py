# chat/serializers.py

from rest_framework import serializers
from .models import ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['chat_id', 'question', 'answer', 'timestamp']
