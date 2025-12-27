from django.urls import path
from .views import AdminReportAPIView

urlpatterns = [
    path('admin/reports/', AdminReportAPIView.as_view()),
]
