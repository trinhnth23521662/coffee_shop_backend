from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from datetime import datetime
from decimal import Decimal
import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from accounts.permissions import IsAdmin, IsStaff
from accounts.models import User, NhanVien, KhachHang
from .models import DonHang, ChiTietDonHang
from menu.models import SanPham
from tables.models import Ban


# ==================== DANH SÁCH ĐƠN HÀNG ====================
class OrderListAPIView(APIView):
    permission_classes = [IsAdmin | IsStaff]

    def get(self, request):
        try:
            # Lấy tham số filter từ query string
            trang_thai = request.GET.get('trang_thai')
            nguon_don = request.GET.get('nguon_don')
            ngay_tu = request.GET.get('ngay_tu')
            ngay_den = request.GET.get('ngay_den')

            # Query cơ bản
            don_hangs = DonHang.objects.select_related('ban', 'khach_hang', 'nhan_vien').all().order_by('-ngay_tao')

            # Áp dụng filter
            if trang_thai:
                don_hangs = don_hangs.filter(trang_thai=trang_thai)
            if nguon_don:
                don_hangs = don_hangs.filter(nguon_don=nguon_don)
            if ngay_tu:
                don_hangs = don_hangs.filter(ngay_tao__gte=ngay_tu)
            if ngay_den:
                don_hangs = don_hangs.filter(ngay_tao__lte=ngay_den)

            # Format dữ liệu
            data = []
            for dh in don_hangs:
                # Đếm số món trong đơn
                so_mon = ChiTietDonHang.objects.filter(don_hang=dh).count()

                data.append({
                    'ma_dh': dh.ma_dh,
                    'ban': dh.ban.ten_ban if dh.ban else 'Không có bàn',
                    'khach_hang': dh.khach_hang.ho_ten if dh.khach_hang else 'Khách vãng lai',
                    'nhan_vien': dh.nhan_vien.ho_ten if dh.nhan_vien else 'Không xác định',
                    'nguon_don': dh.nguon_don,
                    'trang_thai': dh.trang_thai,
                    'tong_tien': float(dh.tong_tien),
                    'so_mon': so_mon,
                    'ngay_tao': dh.ngay_tao.strftime('%Y-%m-%d %H:%M:%S'),
                    'phuong_thuc_tt': dh.phuong_thuc_tt
                })

            return Response({
                'status': 'success',
                'data': data,
                'total': len(data),
                'filters': {
                    'trang_thai': trang_thai,
                    'nguon_don': nguon_don,
                    'ngay_tu': ngay_tu,
                    'ngay_den': ngay_den
                }
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)


# ==================== TẠO ĐƠN HÀNG ====================
@method_decorator(csrf_exempt, name='dispatch')
class CreateOrderAPIView(APIView):
    permission_classes = [IsStaff]

    def post(self, request):
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return Response({'error': 'JSON không hợp lệ'}, status=400)

        ma_ban = body.get('ma_ban')
        nguon_don = body.get('nguon_don', 'offline')
        ma_kh = body.get('ma_kh')
        phuong_thuc_tt = body.get('phuong_thuc_tt', 'Tiền mặt')

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
                # KIỂM TRA BÀN CÓ SẴN KHÔNG
                if ban.trang_thai != 'Trống':
                    return Response({
                        'error': f'Bàn {ban.ten_ban} đang {ban.trang_thai}, không thể tạo đơn'
                    }, status=400)
                # CẬP NHẬT TRẠNG THÁI BÀN THÀNH "Đang phục vụ"
                ban.trang_thai = 'Đang phục vụ'
                ban.save()
            except Ban.DoesNotExist:
                return Response({'error': 'Bàn không tồn tại'}, status=404)

        khach_hang = None
        if ma_kh:
            try:
                khach_hang = KhachHang.objects.get(ma_kh=ma_kh)
            except KhachHang.DoesNotExist:
                return Response({'error': 'Khách hàng không tồn tại'}, status=404)

        # Tạo đơn hàng
        don = DonHang.objects.create(
            nhan_vien=nhan_vien,
            ban=ban,
            khach_hang=khach_hang,
            nguon_don=nguon_don,
            trang_thai='Chờ xác nhận',
            tong_tien=0,
            giam_gia=0,
            phuong_thuc_tt=phuong_thuc_tt,
            ngay_tao=datetime.now()
        )

        return Response({
            'status': 'success',
            'message': 'Tạo đơn hàng thành công',
            'data': {
                'ma_dh': don.ma_dh,
                'ma_ban': ma_ban,
                'ten_ban': ban.ten_ban if ban else None,
                'trang_thai_ban': ban.trang_thai if ban else None,
                'khach_hang': khach_hang.ho_ten if khach_hang else None,
                'nhan_vien': nhan_vien.ho_ten,
                'nguon_don': nguon_don,
                'trang_thai': don.trang_thai,
                'phuong_thuc_tt': don.phuong_thuc_tt,
                'ngay_tao': don.ngay_tao.strftime('%Y-%m-%d %H:%M:%S')
            }
        }, status=status.HTTP_201_CREATED)


# ==================== XEM CHI TIẾT ĐƠN HÀNG ====================
class OrderDetailAPIView(APIView):
    permission_classes = [IsAdmin | IsStaff]

    def get(self, request, ma_dh):
        try:
            don = DonHang.objects.get(ma_dh=ma_dh)
        except DonHang.DoesNotExist:
            return Response({'error': 'Không tìm thấy đơn'}, status=404)

        chi_tiet = ChiTietDonHang.objects.filter(don_hang=don).select_related('san_pham')

        return Response({
            'status': 'success',
            'data': {
                'ma_dh': don.ma_dh,
                'ban': {
                    'ma_ban': don.ban.ma_ban if don.ban else None,
                    'ten_ban': don.ban.ten_ban if don.ban else None,
                    'trang_thai': don.ban.trang_thai if don.ban else None,
                },
                'khach_hang': {
                    'ma_kh': don.khach_hang.ma_kh if don.khach_hang else None,
                    'ho_ten': don.khach_hang.ho_ten if don.khach_hang else None,
                    'so_dien_thoai': don.khach_hang.so_dien_thoai if don.khach_hang else None,
                },
                'nhan_vien': {
                    'ma_nv': don.nhan_vien.ma_nv if don.nhan_vien else None,
                    'ho_ten': don.nhan_vien.ho_ten if don.nhan_vien else None,
                },
                'nguon_don': don.nguon_don,
                'trang_thai': don.trang_thai,
                'tong_tien': float(don.tong_tien),
                'giam_gia': float(don.giam_gia),
                'phuong_thuc_tt': don.phuong_thuc_tt,
                'ngay_tao': don.ngay_tao.strftime('%Y-%m-%d %H:%M:%S'),
                'chi_tiet': [
                    {
                        'ma_ctdh': ct.ma_ctdh,
                        'ma_sp': ct.san_pham.ma_sp,
                        'ten_sp': ct.san_pham.ten_sp,
                        'gia': float(ct.san_pham.gia),
                        'so_luong': ct.so_luong,
                        'thanh_tien': float(ct.san_pham.gia * ct.so_luong),
                        'ghi_chu': ct.ghi_chu,
                        'trang_thai_mon': ct.trang_thai_mon
                    }
                    for ct in chi_tiet
                ]
            }
        })


# ==================== THÊM MÓN VÀO ĐƠN HÀNG ====================
@method_decorator(csrf_exempt, name='dispatch')
class AddItemToOrderAPIView(APIView):
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
            ghi_chu=ghi_chu,
            trang_thai_mon='Chờ làm'
        )

        # cập nhật tổng tiền
        don.tong_tien = sum(
            ct.san_pham.gia * ct.so_luong
            for ct in don.chi_tiet.all()
        )
        don.save()

        return Response({
            'status': 'success',
            'message': 'Thêm món vào đơn thành công',
            'data': {
                'ma_dh': don.ma_dh,
                'tong_tien': float(don.tong_tien)
            }
        })


# ==================== SỬA MÓN TRONG ĐƠN HÀNG ====================
@method_decorator(csrf_exempt, name='dispatch')
class UpdateOrderItemAPIView(APIView):
    permission_classes = [IsStaff]

    def put(self, request, ma_ctdh):
        try:
            chi_tiet = ChiTietDonHang.objects.get(ma_ctdh=ma_ctdh)

            so_luong = request.data.get('so_luong')
            ghi_chu = request.data.get('ghi_chu')
            trang_thai_mon = request.data.get('trang_thai_mon')

            if so_luong is not None:
                chi_tiet.so_luong = int(so_luong)
            if ghi_chu is not None:
                chi_tiet.ghi_chu = ghi_chu
            if trang_thai_mon is not None:
                chi_tiet.trang_thai_mon = trang_thai_mon

            chi_tiet.save()

            # Cập nhật tổng tiền
            don = chi_tiet.don_hang
            don.tong_tien = sum(
                ct.san_pham.gia * ct.so_luong
                for ct in don.chi_tiet.all()
            )
            don.save()

            return Response({
                'status': 'success',
                'message': 'Cập nhật món thành công',
                'data': {
                    'ma_ctdh': chi_tiet.ma_ctdh,
                    'so_luong': chi_tiet.so_luong,
                    'ghi_chu': chi_tiet.ghi_chu,
                    'trang_thai_mon': chi_tiet.trang_thai_mon,
                    'tong_tien': float(don.tong_tien)
                }
            })
        except ChiTietDonHang.DoesNotExist:
            return Response({'error': 'Không tìm thấy chi tiết đơn'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


# ==================== XÓA MÓN TRONG ĐƠN HÀNG ====================
@method_decorator(csrf_exempt, name='dispatch')
class DeleteOrderItemAPIView(APIView):
    permission_classes = [IsStaff]

    def delete(self, request, ma_ctdh):
        try:
            chi_tiet = ChiTietDonHang.objects.get(ma_ctdh=ma_ctdh)
            ma_dh = chi_tiet.don_hang.ma_dh
            chi_tiet.delete()

            # Cập nhật tổng tiền
            don = DonHang.objects.get(ma_dh=ma_dh)
            don.tong_tien = sum(
                ct.san_pham.gia * ct.so_luong
                for ct in don.chi_tiet.all()
            )
            don.save()

            return Response({
                'status': 'success',
                'message': 'Xóa món thành công',
                'data': {
                    'ma_dh': ma_dh,
                    'tong_tien': float(don.tong_tien)
                }
            })
        except ChiTietDonHang.DoesNotExist:
            return Response({'error': 'Không tìm thấy chi tiết đơn'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


# ==================== THANH TOÁN ĐƠN HÀNG ====================
@method_decorator(csrf_exempt, name='dispatch')
class ProcessPaymentAPIView(APIView):
    permission_classes = [IsStaff]

    def post(self, request, ma_dh):
        try:
            body = json.loads(request.body)
            phuong_thuc_tt = body.get('phuong_thuc_tt', 'Tiền mặt')
            giam_gia = Decimal(str(body.get('giam_gia', 0)))

            don = DonHang.objects.get(ma_dh=ma_dh)

            # Kiểm tra nếu đơn đã thanh toán
            if don.trang_thai == 'Hoàn thành':
                return Response({'error': 'Đơn hàng đã được thanh toán'}, status=400)

            don.trang_thai = 'Hoàn thành'
            don.phuong_thuc_tt = phuong_thuc_tt
            don.giam_gia = giam_gia
            don.tong_tien = max(0, don.tong_tien - giam_gia)  # Đảm bảo không âm
            don.save()

            # Cập nhật trạng thái bàn: Trống (nếu có bàn)
            if don.ban:
                don.ban.trang_thai = 'Trống'
                don.ban.save()

            return Response({
                'status': 'success',
                'message': 'Thanh toán thành công',
                'data': {
                    'ma_dh': don.ma_dh,
                    'tong_tien': float(don.tong_tien),
                    'giam_gia': float(don.giam_gia),
                    'thanh_toan': float(don.tong_tien),
                    'phuong_thuc_tt': don.phuong_thuc_tt,
                    'trang_thai': don.trang_thai,
                    'trang_thai_ban': don.ban.trang_thai if don.ban else None
                }
            })
        except DonHang.DoesNotExist:
            return Response({'error': 'Không tìm thấy đơn hàng'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


# ==================== HỦY ĐƠN HÀNG ====================
@method_decorator(csrf_exempt, name='dispatch')
class CancelOrderAPIView(APIView):
    permission_classes = [IsAdmin | IsStaff]

    def put(self, request, ma_dh):
        try:
            don = DonHang.objects.get(ma_dh=ma_dh)

            # Kiểm tra nếu đơn đã hoàn thành
            if don.trang_thai == 'Hoàn thành':
                return Response({'error': 'Không thể hủy đơn đã hoàn thành'}, status=400)

            don.trang_thai = 'Hủy'
            don.save()

            # Cập nhật trạng thái bàn: Trống (nếu có bàn)
            if don.ban:
                don.ban.trang_thai = 'Trống'
                don.ban.save()

            return Response({
                'status': 'success',
                'message': 'Hủy đơn thành công',
                'data': {
                    'ma_dh': don.ma_dh,
                    'trang_thai': don.trang_thai,
                    'trang_thai_ban': don.ban.trang_thai if don.ban else None
                }
            })
        except DonHang.DoesNotExist:
            return Response({'error': 'Không tìm thấy đơn hàng'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


# ==================== LỊCH SỬ ĐƠN HÀNG ====================
class OrderHistoryAPIView(APIView):
    permission_classes = [IsAdmin | IsStaff]

    def get(self, request):
        try:
            ma_kh = request.GET.get('ma_kh')
            ngay_tu = request.GET.get('ngay_tu')
            ngay_den = request.GET.get('ngay_den')
            trang_thai = request.GET.get('trang_thai')

            # Query đơn hàng
            don_hangs = DonHang.objects.select_related('ban', 'khach_hang', 'nhan_vien').all()

            # Áp dụng filter
            if ma_kh:
                try:
                    khach_hang = KhachHang.objects.get(ma_kh=ma_kh)
                    don_hangs = don_hangs.filter(khach_hang=khach_hang)
                except KhachHang.DoesNotExist:
                    return Response({'error': 'Khách hàng không tồn tại'}, status=404)

            if trang_thai:
                don_hangs = don_hangs.filter(trang_thai=trang_thai)
            if ngay_tu:
                don_hangs = don_hangs.filter(ngay_tao__gte=ngay_tu)
            if ngay_den:
                don_hangs = don_hangs.filter(ngay_tao__lte=ngay_den)

            # Format dữ liệu
            data = []
            for dh in don_hangs:
                # Đếm số món trong đơn
                so_mon = ChiTietDonHang.objects.filter(don_hang=dh).count()

                data.append({
                    'ma_dh': dh.ma_dh,
                    'khach_hang': {
                        'ma_kh': dh.khach_hang.ma_kh if dh.khach_hang else None,
                        'ho_ten': dh.khach_hang.ho_ten if dh.khach_hang else 'Khách vãng lai',
                    },
                    'ban': dh.ban.ten_ban if dh.ban else None,
                    'nhan_vien': dh.nhan_vien.ho_ten if dh.nhan_vien else None,
                    'nguon_don': dh.nguon_don,
                    'trang_thai': dh.trang_thai,
                    'tong_tien': float(dh.tong_tien),
                    'giam_gia': float(dh.giam_gia),
                    'so_mon': so_mon,
                    'phuong_thuc_tt': dh.phuong_thuc_tt,
                    'ngay_tao': dh.ngay_tao.strftime('%Y-%m-%d %H:%M:%S')
                })

            return Response({
                'status': 'success',
                'data': data,
                'total': len(data),
                'filters': {
                    'ma_kh': ma_kh,
                    'trang_thai': trang_thai,
                    'ngay_tu': ngay_tu,
                    'ngay_den': ngay_den
                }
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)
