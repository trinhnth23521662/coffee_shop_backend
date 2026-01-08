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
        #now = timezone.now()

        khuyen_mai = KhuyenMai.objects.filter(
            #ngay_bd__lte=now,
            #ngay_kt__gte=now,
            trang_thai='Đang áp dụng'
        )

        serializer = KhuyenMaiSerializer(khuyen_mai, many=True)
        return Response(serializer.data)

    def post(self, request):
        permission_classes = [IsStaff | IsAdmin]
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

    def get(self, request, ma_km):
        try:
            km = KhuyenMai.objects.get(pk=ma_km)
        except KhuyenMai.DoesNotExist:
            return Response(
                {'error': 'Khuyến mãi không tồn tại'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = KhuyenMaiSerializer(km)
        return Response(serializer.data)

    def put(self, request, ma_km):
        permission_classes = [IsStaff | IsAdmin]

        try:
            km = KhuyenMai.objects.get(pk=ma_km)
        except KhuyenMai.DoesNotExist:
            return Response({'error': 'Khuyến mãi không tồn tại'}, status=404)

        serializer = KhuyenMaiSerializer(km, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Cập nhật thành công'})

        return Response(serializer.errors, status=400)

    def delete(self, request, ma_km):
        permission_classes = [IsStaff | IsAdmin]

        try:
            km = KhuyenMai.objects.get(pk=ma_km)
        except KhuyenMai.DoesNotExist:
            return Response(
                {'error': 'Khuyến mãi không tồn tại'},
                status=status.HTTP_404_NOT_FOUND
            )

        km.delete()
        return Response(
            {'message': 'Xóa khuyến mãi thành công'},
            status=status.HTTP_200_OK
        )

