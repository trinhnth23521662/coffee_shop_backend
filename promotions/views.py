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
    """API cho chức năng: Xem danh sách khuyến mãi và Tạo khuyến mãi"""

    def get(self, request):
        """Xem danh sách khuyến mãi"""
        # Lấy các tham số filter từ query string
        trang_thai = request.GET.get('trang_thai')
        loai_km = request.GET.get('loai_km')
        search = request.GET.get('search', '')

        # Khởi tạo queryset
        khuyen_mai = KhuyenMai.objects.all()

        # Filter theo trạng thái nếu có
        if trang_thai:
            khuyen_mai = khuyen_mai.filter(trang_thai=trang_thai)

        # Filter theo loại khuyến mãi
        if loai_km:
            khuyen_mai = khuyen_mai.filter(loai_km=loai_km)

        # Search theo tên khuyến mãi
        if search:
            khuyen_mai = khuyen_mai.filter(ten_km__icontains=search)

        # Order by ngày bắt đầu (mới nhất trước)
        khuyen_mai = khuyen_mai.order_by('-ngay_bd')

        serializer = KhuyenMaiSerializer(khuyen_mai, many=True)
        return Response({
            'status': 'success',
            'data': serializer.data,
            'total': khuyen_mai.count(),
            'filters': {
                'trang_thai': trang_thai,
                'loai_km': loai_km,
                'search': search
            }
        })

    def post(self, request):
        """Tạo khuyến mãi mới"""
        vai_tro = request.session.get('vai_tro')

        if vai_tro not in ['Admin', 'Staff']:
            return Response(
                {'status': 'error', 'message': 'Không có quyền tạo khuyến mãi'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = KhuyenMaiSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'status': 'success',
                    'message': 'Tạo khuyến mãi thành công',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {'status': 'error', 'message': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


@method_decorator(csrf_exempt, name='dispatch')
class PromotionDetailAPIView(APIView):
    """API cho chức năng: Xem chi tiết, Sửa, Xóa khuyến mãi"""

    def get_object(self, ma_km):
        """Lấy đối tượng KhuyenMai theo mã"""
        try:
            return KhuyenMai.objects.get(pk=ma_km)
        except KhuyenMai.DoesNotExist:
            return None

    def get(self, request, ma_km):
        """Xem chi tiết khuyến mãi"""
        km = self.get_object(ma_km)
        if not km:
            return Response(
                {'status': 'error', 'message': 'Khuyến mãi không tồn tại'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = KhuyenMaiSerializer(km)
        return Response({
            'status': 'success',
            'data': serializer.data
        })

    def put(self, request, ma_km):
        """Sửa khuyến mãi"""
        vai_tro = request.session.get('vai_tro')

        if vai_tro not in ['Admin', 'Staff']:
            return Response(
                {'status': 'error', 'message': 'Không có quyền cập nhật khuyến mãi'},
                status=status.HTTP_403_FORBIDDEN
            )

        km = self.get_object(ma_km)
        if not km:
            return Response(
                {'status': 'error', 'message': 'Khuyến mãi không tồn tại'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = KhuyenMaiSerializer(km, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Cập nhật khuyến mãi thành công',
                'data': serializer.data
            })

        return Response(
            {'status': 'error', 'message': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, ma_km):
        """Xóa khuyến mãi"""
        vai_tro = request.session.get('vai_tro')

        if vai_tro != 'Admin':
            return Response(
                {'status': 'error', 'message': 'Chỉ Admin được xóa khuyến mãi'},
                status=status.HTTP_403_FORBIDDEN
            )

        km = self.get_object(ma_km)
        if not km:
            return Response(
                {'status': 'error', 'message': 'Khuyến mãi không tồn tại'},
                status=status.HTTP_404_NOT_FOUND
            )

        km.delete()
        return Response(
            {'status': 'success', 'message': 'Xóa khuyến mãi thành công'},
            status=status.HTTP_204_NO_CONTENT
        )
