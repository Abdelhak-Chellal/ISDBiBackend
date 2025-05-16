from django.urls import path
from .views import StandardsEnhancementPromptView

urlpatterns = [
    path('prompt/', StandardsEnhancementPromptView.as_view(), name='standards-prompt'),
]
