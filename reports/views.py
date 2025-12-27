from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdmin
from accounts.models import User
from orders.models import DonHang


class AdminReportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        return Response({
            "total_users": User.objects.count(),
            "total_staff": User.objects.filter(vai_tro='Nhân viên').count(),
            "total_customers": User.objects.filter(vai_tro='Khách hàng').count(),
            "total_orders": DonHang.objects.count(),
            "revenue": 0
        })
