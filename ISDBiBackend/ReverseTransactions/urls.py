from django.urls import path
from .views import ReverseTransactionsPromptView

urlpatterns = [
    path('prompt/', ReverseTransactionsPromptView.as_view(), name='reverse-prompt'),
]
