from django.urls import path
from .views import (
    BanListCreateAPIView,
    BanDetailAPIView,
    BanChangeStatusAPIView
)

urlpatterns = [
    path('', BanListCreateAPIView.as_view()),
    path('<int:ma_ban>/', BanDetailAPIView.as_view()),
    path('<int:ma_ban>/status/', BanChangeStatusAPIView.as_view()),
]
