from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from accounts.permissions import IsAdmin, IsStaff, IsCustomer
from accounts.models import User, NhanVien, KhachHang
from .models import DonHang, ChiTietDonHang
from menu.models import SanPham
from tables.models import Ban
from django.utils import timezone
from decimal import Decimal
from promotions.models import KhuyenMai

def tinh_giam_gia(tong_tien):
    #now = timezone.now()

    khuyen_mais = KhuyenMai.objects.filter(
        trang_thai='Đang áp dụng',
        #ngay_bd__lte=now,
        #ngay_kt__gte=now,
        dieu_kien__lte=tong_tien
    )

    giam_gia_max = Decimal('0')

    for km in khuyen_mais:
        if km.loai_km == 'Phần trăm':
            giam = tong_tien * km.gia_tri / Decimal('100')
        else:  # Tiền mặt
            giam = km.gia_tri

        if giam > giam_gia_max:
            giam_gia_max = giam
            km_ap_dung = km

    # Không cho giảm quá tổng tiền
    return min(giam_gia_max, tong_tien), km_ap_dung

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

                # kiểm tra trạng thái bàn
                if ban.trang_thai != 'Trống':
                    return Response(
                        {'error': 'Bàn đang được sử dụng'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # chuyển bàn sang đang phục vụ
                ban.trang_thai = 'Đang phục vụ'
                ban.save()

            except Ban.DoesNotExist:
                return Response({'error': 'Bàn không tồn tại'}, status=404)

        #tạo đơn hàng
        don = DonHang.objects.create(
            nhan_vien=nhan_vien,
            ban=ban,
            nguon_don=nguon_don,
            phuong_thuc_tt=phuong_thuc_tt,
            trang_thai='Chờ xác nhận'
        )

        return Response({
            'message': 'Tạo đơn hàng thành công',
            'ma_dh': don.ma_dh
        }, status=status.HTTP_201_CREATED)

@method_decorator(csrf_exempt, name='dispatch')
class ThemChiTietDonAPIView(APIView):
    permission_classes = [IsStaff]

    def post(self, request, ma_dh):
        body = request.data

        ma_sp = body.get('ma_sp')
        so_luong = int(body.get('so_luong', 1))
        ghi_chu = body.get('ghi_chu', '')

        if not ma_sp:
            return Response({'error': 'Thiếu mã sản phẩm'}, status=400)

        try:
            don = DonHang.objects.get(ma_dh=ma_dh)
            sp = SanPham.objects.get(ma_sp=ma_sp)
        except (DonHang.DoesNotExist, SanPham.DoesNotExist):
            return Response(
                {'error': 'Không tìm thấy đơn hoặc sản phẩm'},
                status=404
            )

        # ===== THÊM / CẬP NHẬT CHI TIẾT =====
        item, created = ChiTietDonHang.objects.get_or_create(
            don_hang=don,
            san_pham=sp,
            defaults={
                'so_luong': so_luong,
                'ghi_chu': ghi_chu
            }
        )

        if not created:
            item.so_luong += so_luong
            item.ghi_chu = ghi_chu
            item.save()

        # ===== TÍNH TỔNG TIỀN =====
        tong_tien = sum(
            ct.so_luong * ct.san_pham.gia
            for ct in don.chi_tiet.all()
        )

        # ===== TÍNH GIẢM GIÁ (NẾU CÓ) =====
        giam_gia, km = tinh_giam_gia(tong_tien)

        # ===== CẬP NHẬT ĐƠN =====
        don.tong_tien = tong_tien
        don.giam_gia = giam_gia
        don.save()

        return Response({
            'status': 'success',
            'ma_dh': don.ma_dh,
            'tong_tien': tong_tien,
            'giam_gia': giam_gia,
            'can_thanh_toan': tong_tien - giam_gia,
            'khuyen_mai': {
                'ten_km': km.ten_km,
                'loai_km': km.loai_km,
                'gia_tri': km.gia_tri,
                'dieu_kien': km.dieu_kien
            } if km else None,
            'items': [
                {
                    'san_pham': ct.san_pham.ten_sp,
                    'so_luong': ct.so_luong,
                    'don_gia': ct.san_pham.gia,
                    'thanh_tien': ct.so_luong * ct.san_pham.gia
                }
                for ct in don.chi_tiet.all()
            ]
        }, status=200)

class XemDonHangAPIView(APIView):
    permission_classes = [IsAdmin | IsStaff]

    def get(self, request, ma_dh):
        try:
            don = DonHang.objects.get(ma_dh=ma_dh)
        except DonHang.DoesNotExist:
            return Response({'error': 'Không tìm thấy đơn'}, status=404)

        # ===== TÌM KHUYẾN MÃI ĐÃ ÁP DỤNG =====
        km = None
        if don.giam_gia > 0:
            khuyen_mais = KhuyenMai.objects.filter(
                trang_thai='Đang áp dụng',
                dieu_kien__lte=don.tong_tien
            )

            giam_max = Decimal('0')
            for k in khuyen_mais:
                if k.loai_km == 'Phần trăm':
                    giam = don.tong_tien * k.gia_tri / Decimal('100')
                else:
                    giam = k.gia_tri

                if giam == don.giam_gia:
                    km = k
                    break

        return Response({
            'ma_dh': don.ma_dh,
            'trang_thai': don.trang_thai,
            'ban': don.ban.ten_ban if don.ban else None,

            # ===== TIỀN =====
            'tong_tien': float(don.tong_tien),
            'giam_gia': float(don.giam_gia),
            'can_thanh_toan': float(don.tong_tien - don.giam_gia),

            # ===== KHUYẾN MÃI =====
            'khuyen_mai': {
                'ten_km': km.ten_km,
                'loai_km': km.loai_km,
                'gia_tri': float(km.gia_tri),
                'dieu_kien': float(km.dieu_kien)
            } if km else None,

            # ===== DANH SÁCH MÓN =====
            'ds_san_pham': [
                {
                    'ten_sp': ct.san_pham.ten_sp,
                    'don_gia': float(ct.san_pham.gia),
                    'so_luong': ct.so_luong,
                    'thanh_tien': float(ct.san_pham.gia * ct.so_luong),
                    'ghi_chu': ct.ghi_chu,
                    'trang_thai_mon': ct.trang_thai_mon
                }
                for ct in don.chi_tiet.all()
            ]
        })

@method_decorator(csrf_exempt, name='dispatch')
class CustomerCreateOrderAPIView(APIView):
    permission_classes = [IsCustomer]

    def post(self, request):
        nguon_don = request.data.get('nguon_don', 'online')
        ma_ban = request.data.get('ma_ban')
        phuong_thuc_tt = request.data.get('phuong_thuc_tt', 'Tiền mặt')

        # ===== LẤY USER ĐANG ĐĂNG NHẬP =====
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'error': 'Chưa đăng nhập'}, status=401)

        try:
            user = User.objects.get(ma_nd=user_id)
            khach_hang = KhachHang.objects.get(ma_nd=user)
        except (User.DoesNotExist, KhachHang.DoesNotExist):
            return Response({'error': 'Không tìm thấy khách hàng'}, status=404)

        # ===== XỬ LÝ BÀN =====
        # ===== CUSTOMER XỬ LÝ BÀN (SỬA Ở ĐÂY) =====
        ban = None
        if ma_ban:
            try:
                ban = Ban.objects.get(ma_ban=ma_ban)
            except Ban.DoesNotExist:
                return Response({'error': 'Bàn không tồn tại'}, status=404)

        # ===== TẠO ĐƠN HÀNG =====
        # LẤY NHÂN VIÊN MẶC ĐỊNH
        nhan_vien = NhanVien.objects.get(ma_nv=1)

        don = DonHang.objects.create(
            nhan_vien=nhan_vien,
            khach_hang=khach_hang,
            ban=ban,
            nguon_don='online',
            trang_thai='Chờ xác nhận',
            tong_tien=0,
            giam_gia=0,
            phuong_thuc_tt = phuong_thuc_tt
        )

        return Response({
            'message': 'Khách hàng tạo đơn thành công',
            'data': {
                'ma_dh': don.ma_dh,
                'khach_hang': khach_hang.ho_ten,
                'ban': ban.ten_ban if ban else None
            }
        }, status=status.HTTP_201_CREATED)

@method_decorator(csrf_exempt, name='dispatch')
class AddOnlineOrderItemAPIView(APIView):
    permission_classes = [IsCustomer]

    def post(self, request, ma_dh):
        body = request.data

        ma_sp = body.get("ma_sp")
        so_luong = int(body.get("so_luong", 1))
        ghi_chu = body.get("ghi_chu", "")

        try:
            don = DonHang.objects.get(ma_dh=ma_dh)
            sp = SanPham.objects.get(ma_sp=ma_sp)
        except (DonHang.DoesNotExist, SanPham.DoesNotExist):
            return Response(
                {'error': 'Đơn hàng hoặc sản phẩm không tồn tại'},
                status=404
            )

        if don.trang_thai != 'Chờ xác nhận':
            return Response(
                {'error': 'Không thể thêm món vào đơn đã xử lý'},
                status=400
            )

        # ===== THÊM / CẬP NHẬT CHI TIẾT =====
        item, created = ChiTietDonHang.objects.get_or_create(
            don_hang=don,
            san_pham=sp,
            defaults={
                'so_luong': so_luong,
                'ghi_chu': ghi_chu
            }
        )

        if not created:
            item.so_luong += so_luong
            item.ghi_chu = ghi_chu
            item.save()

        # ===== TÍNH TỔNG TIỀN (LẤY GIÁ TỪ SANPHAM) =====
        tong_tien = sum(
            ct.so_luong * ct.san_pham.gia
            for ct in don.chi_tiet.all()
        )

        # ===== TÍNH GIẢM GIÁ =====
        giam_gia, km= tinh_giam_gia(tong_tien)

        # ===== CẬP NHẬT ĐƠN =====
        don.tong_tien = tong_tien
        don.giam_gia = giam_gia
        don.save()

        return Response({
            'status': 'success',
            'ma_dh': don.ma_dh,
            'tong_tien': tong_tien,
            'giam_gia': giam_gia,
            'can_thanh_toan': tong_tien - giam_gia,
            'khuyen_mai': {
                'ten_km': km.ten_km,
                'loai_km': km.loai_km,
                'gia_tri': km.gia_tri,
                'dieu_kien': km.dieu_kien
            } if km else None,
            'items': [
                {
                    'san_pham': ct.san_pham.ten_sp,
                    'so_luong': ct.so_luong,
                    'don_gia': ct.san_pham.gia,
                    'thanh_tien': ct.so_luong * ct.san_pham.gia
                }
                for ct in don.chi_tiet.all()
            ]
        }, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class ThanhToanTienMatAPIView(APIView):
    permission_classes = [IsStaff]

    def post(self, request, ma_dh):
        try:
            don = DonHang.objects.select_related('ban').get(ma_dh=ma_dh)
        except DonHang.DoesNotExist:
            return Response(
                {"error": "Đơn hàng không tồn tại"},
                status=404
            )

        if don.trang_thai == "Hoàn thành":
            return Response(
                {"error": "Đơn hàng đã được thanh toán"},
                status=400
            )

        # ===== CẬP NHẬT TRẠNG THÁI =====
        don.trang_thai = "Hoàn thành"
        don.save()

        # Cập nhật trạng thái món
        ChiTietDonHang.objects.filter(
            don_hang=don
        ).update(trang_thai_mon="Xong")

        # Cập nhật trạng thái bàn
        if don.ban:
            don.ban.trang_thai = "Trống"
            don.ban.save()

        # ===== DỮ LIỆU TRẢ VỀ =====
        tong_tien = don.tong_tien
        giam_gia = don.giam_gia
        can_thanh_toan = tong_tien - giam_gia
        giam_gia, km = tinh_giam_gia(don.tong_tien)

        return Response({
            "message": "Thanh toán tiền mặt thành công",
            "don_hang": {
                "ma_dh": don.ma_dh,
                "trang_thai": don.trang_thai,
                "tong_tien": don.tong_tien,
                "giam_gia": giam_gia,
                "can_thanh_toan": don.tong_tien - giam_gia,
                "khuyen_mai": {
                    "ten_km": km.ten_km,
                    "loai_km": km.loai_km,
                    "gia_tri": km.gia_tri,
                    "dieu_kien": km.dieu_kien
                } if km else None
            },
            "ban": {
                "ma_ban": don.ban.ma_ban if don.ban else None,
                #"trang_thai": don.ban.trang_thai if don.ban else None
            },
            "chi_tiet": [
                {
                    "ten_sp": ct.san_pham.ten_sp,
                    "so_luong": ct.so_luong,
                    "don_gia": ct.san_pham.gia,
                    "thanh_tien": ct.so_luong * ct.san_pham.gia
                }
                for ct in don.chi_tiet.all()
            ]
        }, status=200)
