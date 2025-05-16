# chat/models.py

from django.db import models
from django.utils import timezone

class ChatMessage(models.Model):
    chat_id = models.CharField(max_length=100, db_index=True)
    question = models.TextField()
    answer = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['timestamp']
