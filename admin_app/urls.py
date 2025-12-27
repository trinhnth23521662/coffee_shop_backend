from django.urls import path
from .views import EmployeeAPIView, AdminReportAPIView

urlpatterns = [
    path('employees/', EmployeeAPIView.as_view()),
    path('employees/<int:pk>/', EmployeeAPIView.as_view()),
    path('reports/', AdminReportAPIView.as_view()),
]
