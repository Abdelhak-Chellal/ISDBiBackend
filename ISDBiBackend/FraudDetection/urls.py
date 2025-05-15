from django.urls import path
from .views import FraudDetectionPromptView

urlpatterns = [
    path('prompt/', FraudDetectionPromptView.as_view(), name='fraud-prompt'),
]
