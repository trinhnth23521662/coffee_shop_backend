from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from accounts.permissions import IsAdmin, IsStaff
from .models import KhuyenMai
from .serializers import KhuyenMaiSerializer

@method_decorator(csrf_exempt, name='dispatch')
class PromotionAPIView(APIView):
    def get(self, request):
        now = timezone.now()

        khuyen_mai = KhuyenMai.objects.filter(
            ngay_bd__lte=now,
            ngay_kt__gte=now,
            trang_thai='DANG_AP_DUNG'
        )

        serializer = KhuyenMaiSerializer(khuyen_mai, many=True)
        return Response(serializer.data)

    def post(self, request):
        vai_tro = request.session.get('vai_tro')

        if vai_tro not in ['Admin', 'Staff']:
            return Response(
                {'error': 'Không có quyền tạo khuyến mãi'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = KhuyenMaiSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Tạo khuyến mãi thành công'},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class PromotionDetailAPIView(APIView):
    def get_object(self, ma_km):
        try:
            return KhuyenMai.objects.get(pk=ma_km)
        except KhuyenMai.DoesNotExist:
            return None

    def put(self, request, ma_km):
        vai_tro = request.session.get('vai_tro')

        if vai_tro not in ['ADMIN', 'STAFF']:
            return Response(
                {'error': 'Không có quyền cập nhật khuyến mãi'},
                status=403
            )

        km = self.get_object(ma_km)
        if not km:
            return Response({'error': 'Khuyến mãi không tồn tại'}, status=404)

        serializer = KhuyenMaiSerializer(km, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Cập nhật thành công'})

        return Response(serializer.errors, status=400)

    def delete(self, request, ma_km):
        vai_tro = request.session.get('vai_tro')

        if vai_tro != 'ADMIN':
            return Response(
                {'error': 'Chỉ Admin được xóa khuyến mãi'},
                status=403
            )

        km = self.get_object(ma_km)
        if not km:
            return Response({'error': 'Khuyến mãi không tồn tại'}, status=404)

        km.delete()
        return Response({'message': 'Xóa khuyến mãi thành công'}, status=204)

