from django.urls import path
from .views import PromotionAPIView, PromotionDetailAPIView

urlpatterns = [
    path('promotions/', PromotionAPIView.as_view()),
    path('promotions/<int:ma_km>/', PromotionDetailAPIView.as_view()),
]
