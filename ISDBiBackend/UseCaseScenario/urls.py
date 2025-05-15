from django.urls import path
from .views import UseCaseScenarioPromptView

urlpatterns = [
    path('prompt/', UseCaseScenarioPromptView.as_view(), name='scenario-prompt'),
]
