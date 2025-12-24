from django.urls import path
from .views import (
    LoginAPIView,
    RegisterAPIView,
    AdminDashboardAPIView,
    EmployeeAPIView,
    ReportAPIView,
    StaffDashboardAPIView,
    CustomerDashboardAPIView
)

urlpatterns = [
    # Auth
    path('login/', LoginAPIView.as_view()),
    path('register/', RegisterAPIView.as_view()),

    # Admin
    path('admin/dashboard/', AdminDashboardAPIView.as_view()),
    path('admin/employees/', EmployeeAPIView.as_view()),
    path('admin/employees/<int:id>/', EmployeeAPIView.as_view()),
    path('admin/reports/', ReportAPIView.as_view()),

    # Staff
    path('staff/dashboard/', StaffDashboardAPIView.as_view()),

    # Customer
    path('customer/dashboard/', CustomerDashboardAPIView.as_view()),
]
