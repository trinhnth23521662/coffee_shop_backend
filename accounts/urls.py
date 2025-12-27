from django.urls import path
from .views import (
    LoginAPIView,
    RegisterAPIView,
    DashboardAPIView,
)

urlpatterns = [
    path('login/', LoginAPIView.as_view()),
    path('register/', RegisterAPIView.as_view()),
    path('dashboard/', DashboardAPIView.as_view()),
]
