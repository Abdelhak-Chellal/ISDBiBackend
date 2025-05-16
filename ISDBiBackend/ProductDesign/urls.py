from django.urls import path
from .views import ProductDesignPromptView

urlpatterns = [
    path("prompt/", ProductDesignPromptView.as_view(), name="product-design-prompt"),
]
