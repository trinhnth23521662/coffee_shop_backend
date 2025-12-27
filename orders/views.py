from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from accounts.permissions import IsAdmin, IsStaff
from accounts.models import User, NhanVien
from .models import DonHang, ChiTietDonHang
from menu.models import SanPham
from tables.models import Ban

@method_decorator(csrf_exempt, name='dispatch')
class TaoDonHangAPIView(APIView):
    permission_classes = [IsStaff]

    def post(self, request):
        nguon_don = request.data.get('nguon_don', 'offline')
        ma_ban = request.data.get('ma_ban')
        phuong_thuc_tt = request.data.get('phuong_thuc_tt', 'Tiền mặt')

        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'error': 'Chưa đăng nhập'}, status=401)

        try:
            user = User.objects.get(ma_nd=user_id)
            nhan_vien = NhanVien.objects.get(ma_nd=user)
        except (User.DoesNotExist, NhanVien.DoesNotExist):
            return Response({'error': 'Không tìm thấy nhân viên'}, status=404)

        ban = None
        if ma_ban:
            try:
                ban = Ban.objects.get(ma_ban=ma_ban)
            except Ban.DoesNotExist:
                return Response({'error': 'Bàn không tồn tại'}, status=404)

        don = DonHang.objects.create(
            nhan_vien=nhan_vien,
            ban=ban,
            nguon_don=nguon_don,
            phuong_thuc_tt=phuong_thuc_tt
        )

        return Response({
            'message': 'Tạo đơn hàng thành công',
            'ma_dh': don.ma_dh
        }, status=status.HTTP_201_CREATED)

@method_decorator(csrf_exempt, name='dispatch')
class ThemChiTietDonAPIView(APIView):
    permission_classes = [IsStaff]

    def post(self, request, ma_dh):
        ma_sp = request.data.get('ma_sp')
        so_luong = int(request.data.get('so_luong', 1))
        ghi_chu = request.data.get('ghi_chu', '')

        if not ma_sp:
            return Response({'error': 'Thiếu mã sản phẩm'}, status=400)

        try:
            don = DonHang.objects.get(ma_dh=ma_dh)
            sp = SanPham.objects.get(ma_sp=ma_sp)
        except (DonHang.DoesNotExist, SanPham.DoesNotExist):
            return Response({'error': 'Không tìm thấy đơn hoặc sản phẩm'}, status=404)

        ChiTietDonHang.objects.create(
            don_hang=don,
            san_pham=sp,
            so_luong=so_luong,
            ghi_chu=ghi_chu
        )

        # cập nhật tổng tiền
        don.tong_tien = sum(
            ct.san_pham.gia * ct.so_luong
            for ct in don.chi_tiet.all()
        )
        don.save()

        return Response({'message': 'Thêm món vào đơn thành công'})

class XemDonHangAPIView(APIView):
    permission_classes = [IsAdmin | IsStaff]

    def get(self, request, ma_dh):
        try:
            don = DonHang.objects.get(ma_dh=ma_dh)
        except DonHang.DoesNotExist:
            return Response({'error': 'Không tìm thấy đơn'}, status=404)

        return Response({
            'ma_dh': don.ma_dh,
            'trang_thai': don.trang_thai,
            'tong_tien': float(don.tong_tien),
            'ban': don.ban.ten_ban if don.ban else None,
            'ds_san_pham': [
                {
                    'ten_sp': ct.san_pham.ten_sp,
                    'gia': float(ct.san_pham.gia),
                    'so_luong': ct.so_luong,
                    'ghi_chu': ct.ghi_chu,
                    'trang_thai_mon': ct.trang_thai_mon
                }
                for ct in don.chi_tiet.all()
            ]
        })