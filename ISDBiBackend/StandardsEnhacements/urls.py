from django.urls import path
from .views import StandardsEnhacementsPromptView

urlpatterns = [
    path('prompt/', StandardsEnhacementsPromptView.as_view(), name='standards-prompt'),
]
