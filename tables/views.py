from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from accounts.permissions import IsAdmin, IsStaff
from .models import Ban


# ==================== DANH SÁCH BÀN ====================
class TableListAPIView(APIView):
    permission_classes = [IsAdmin | IsStaff]

    def get(self, request):
        try:
            trang_thai = request.GET.get('trang_thai')

            ban_list = Ban.objects.all()
            if trang_thai:
                ban_list = ban_list.filter(trang_thai=trang_thai)

            data = [{
                'ma_ban': ban.ma_ban,
                'ten_ban': ban.ten_ban,
                'trang_thai': ban.trang_thai
            } for ban in ban_list]

            return Response({
                'status': 'success',
                'data': data,
                'total': len(data),
                'filters': {'trang_thai': trang_thai}
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)


# ==================== TẠO BÀN ====================
@method_decorator(csrf_exempt, name='dispatch')
class CreateTableAPIView(APIView):
    permission_classes = [IsAdmin | IsStaff]

    def post(self, request):
        try:
            ten_ban = request.data.get('ten_ban')
            trang_thai = request.data.get('trang_thai', 'Trống')

            if not ten_ban:
                return Response({'error': 'Thiếu tên bàn'}, status=400)

            # Kiểm tra tên bàn đã tồn tại chưa
            if Ban.objects.filter(ten_ban=ten_ban).exists():
                return Response({'error': 'Tên bàn đã tồn tại'}, status=400)

            ban = Ban.objects.create(
                ten_ban=ten_ban,
                trang_thai=trang_thai
            )

            return Response({
                'status': 'success',
                'message': 'Tạo bàn thành công',
                'data': {
                    'ma_ban': ban.ma_ban,
                    'ten_ban': ban.ten_ban,
                    'trang_thai': ban.trang_thai
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


# ==================== SỬA BÀN ====================
@method_decorator(csrf_exempt, name='dispatch')
class UpdateTableAPIView(APIView):
    permission_classes = [IsAdmin | IsStaff]

    def put(self, request, ma_ban):
        try:
            ban = Ban.objects.get(ma_ban=ma_ban)

            ten_ban = request.data.get('ten_ban')
            trang_thai = request.data.get('trang_thai')

            if ten_ban is not None:
                # Kiểm tra tên bàn đã tồn tại (trừ bàn hiện tại)
                if Ban.objects.filter(ten_ban=ten_ban).exclude(ma_ban=ma_ban).exists():
                    return Response({'error': 'Tên bàn đã tồn tại'}, status=400)
                ban.ten_ban = ten_ban

            if trang_thai is not None:
                ban.trang_thai = trang_thai

            ban.save()

            return Response({
                'status': 'success',
                'message': 'Cập nhật bàn thành công',
                'data': {
                    'ma_ban': ban.ma_ban,
                    'ten_ban': ban.ten_ban,
                    'trang_thai': ban.trang_thai
                }
            })
        except Ban.DoesNotExist:
            return Response({'error': 'Không tìm thấy bàn'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


# ==================== XÓA BÀN ====================
@method_decorator(csrf_exempt, name='dispatch')
class DeleteTableAPIView(APIView):
    permission_classes = [IsAdmin | IsStaff]

    def delete(self, request, ma_ban):
        try:
            ban = Ban.objects.get(ma_ban=ma_ban)

            # Kiểm tra xem bàn có đang được sử dụng không
            from orders.models import DonHang
            don_hang_dang_su_dung = DonHang.objects.filter(
                ban=ban,
                trang_thai__in=['Chờ xác nhận', 'Đang làm']
            ).exists()

            if don_hang_dang_su_dung:
                return Response({
                    'error': f'Bàn {ban.ten_ban} đang có đơn hàng chưa hoàn thành, không thể xóa'
                }, status=400)

            ban.delete()

            return Response({
                'status': 'success',
                'message': 'Xóa bàn thành công',
                'data': {
                    'ma_ban': ma_ban,
                    'ten_ban': ban.ten_ban
                }
            })
        except Ban.DoesNotExist:
            return Response({'error': 'Không tìm thấy bàn'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


# ==================== XEM CHI TIẾT BÀN ====================
class TableDetailAPIView(APIView):
    permission_classes = [IsAdmin | IsStaff]

    def get(self, request, ma_ban):
        try:
            ban = Ban.objects.get(ma_ban=ma_ban)

            return Response({
                'status': 'success',
                'data': {
                    'ma_ban': ban.ma_ban,
                    'ten_ban': ban.ten_ban,
                    'trang_thai': ban.trang_thai
                }
            })
        except Ban.DoesNotExist:
            return Response({'error': 'Không tìm thấy bàn'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

# ==================== CẬP NHẬT TRẠNG THÁI BÀN ====================
@method_decorator(csrf_exempt, name='dispatch')
class UpdateTableStatusAPIView(APIView):
    permission_classes = [IsAdmin | IsStaff]

    def patch(self, request, ma_ban):
        try:
            ban = Ban.objects.get(ma_ban=ma_ban)
            trang_thai = request.data.get('trang_thai')

            if not trang_thai:
                return Response({'error': 'Thiếu trạng thái'}, status=400)

            # Các giá trị hợp lệ
            valid_statuses = ['Trống', 'Đang phục vụ']
            if trang_thai not in valid_statuses:
                return Response({
                    'error': f'Trạng thái không hợp lệ. Chọn: {", ".join(valid_statuses)}'
                }, status=400)

            ban.trang_thai = trang_thai
            ban.save()

            return Response({
                'status': 'success',
                'message': 'Cập nhật trạng thái thành công',
                'data': {
                    'ma_ban': ban.ma_ban,
                    'ten_ban': ban.ten_ban,
                    'trang_thai': ban.trang_thai
                }
            })
        except Ban.DoesNotExist:
            return Response({'error': 'Không tìm thấy bàn'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
