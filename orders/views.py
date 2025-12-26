from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import DonHang, ChiTietDonHang
from menu.models import SanPham          
from tables.models import Ban    
from accounts.models import KhachHang
from decimal import Decimal
from datetime import datetime
import json


# ============= HELPER FUNCTION =============
def check_staff_permission(request):
    """Kiem tra quyen Nhan vien"""
    vai_tro = request.session.get('vai_tro')
    if vai_tro != 'Nhân viên':
        return False
    return True


# ============= DON HANG API (CASHIER) - CHI NHAN VIEN =============
@csrf_exempt
@require_http_methods(["POST"])
def api_tao_don(request):
    """POST tao don moi (offline/online) - CHI NHAN VIEN"""
    if not check_staff_permission(request):
        return JsonResponse({'status': 'error', 'message': 'Khong co quyen truy cap'}, status=403)

    try:
        body = json.loads(request.body)
        ma_ban = body.get('ma_ban')
        nguon_don = body.get('nguon_don', 'offline')
        ma_kh = body.get('ma_kh')
        ngay_tao_str = body.get('ngay_tao')  # Format: "YYYY-MM-DD" hoac "YYYY-MM-DD HH:MM:SS"

        # Xu ly ngay tao
        if ngay_tao_str:
            try:
                if len(ngay_tao_str) == 10:  # YYYY-MM-DD
                    ngay_tao = datetime.strptime(ngay_tao_str, '%Y-%m-%d')
                else:  # YYYY-MM-DD HH:MM:SS
                    ngay_tao = datetime.strptime(ngay_tao_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return JsonResponse({'status': 'error',
                                     'message': 'Dinh dang ngay khong hop le. Dung: YYYY-MM-DD hoac YYYY-MM-DD HH:MM:SS'},
                                    status=400)
        else:
            ngay_tao = datetime.now()  # Mac dinh la hom nay

        don_hang = DonHang(
            ma_kh_id=ma_kh if ma_kh else None,
            ma_ban_id=ma_ban if ma_ban else None,
            ma_nv=request.session.get('user_id', 2),  # Lay tu session hoac mac dinh 2
            nguon_don=nguon_don,
            trang_thai='Chờ xác nhận',
            tong_tien=0,
            giam_gia=0,
            phuong_thuc_tt='Tiền mặt',
            ngay_tao=ngay_tao
        )
        don_hang.save()

        if ma_ban:
            Ban.objects.filter(ma_ban=ma_ban).update(trang_thai='Đang phục vụ')

        return JsonResponse({
            'status': 'success',
            'message': 'Tao don thanh cong',
            'data': {
                'ma_dh': don_hang.ma_dh,
                'ma_ban': ma_ban,
                'nguon_don': nguon_don,
                'trang_thai': don_hang.trang_thai,
                'ngay_tao': don_hang.ngay_tao.strftime('%Y-%m-%d %H:%M:%S')
            }
        }, status=201)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_them_mon(request):
    """POST them mon vao don - CHI NHAN VIEN"""
    if not check_staff_permission(request):
        return JsonResponse({'status': 'error', 'message': 'Khong co quyen truy cap'}, status=403)

    try:
        body = json.loads(request.body)
        ma_dh = body.get('ma_dh')
        ma_mon = body.get('ma_mon')
        so_luong = body.get('so_luong', 1)
        ghi_chu = body.get('ghi_chu', '')

        if not all([ma_dh, ma_mon]):
            return JsonResponse({'status': 'error', 'message': 'Thieu thong tin'}, status=400)

        chi_tiet = ChiTietDonHang.objects.create(
            ma_dh_id=ma_dh,
            ma_mon_id=ma_mon,
            so_luong=so_luong,
            ghi_chu=ghi_chu,
            trang_thai_mon='Chờ làm'
        )

        # Cap nhat tong tien
        chi_tiets = ChiTietDonHang.objects.filter(ma_dh=ma_dh).select_related('ma_mon')
        tong = sum(ct.so_luong * ct.ma_mon.gia for ct in chi_tiets)
        DonHang.objects.filter(ma_dh=ma_dh).update(tong_tien=tong)

        return JsonResponse({
            'status': 'success',
            'message': 'Them mon thanh cong',
            'data': {
                'ma_ctdh': chi_tiet.ma_ctdh,
                'ma_dh': ma_dh,
                'so_luong': so_luong,
                'tong_tien': float(tong)
            }
        }, status=201)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def api_sua_mon(request, ma_ctdh):
    """PUT cap nhat mon trong don - CHI NHAN VIEN"""
    if not check_staff_permission(request):
        return JsonResponse({'status': 'error', 'message': 'Khong co quyen truy cap'}, status=403)

    try:
        chi_tiet = ChiTietDonHang.objects.get(ma_ctdh=ma_ctdh)
        body = json.loads(request.body)

        chi_tiet.so_luong = body.get('so_luong', chi_tiet.so_luong)
        chi_tiet.ghi_chu = body.get('ghi_chu', chi_tiet.ghi_chu)
        chi_tiet.trang_thai_mon = body.get('trang_thai_mon', chi_tiet.trang_thai_mon)
        chi_tiet.save()

        # Cap nhat tong tien
        chi_tiets = ChiTietDonHang.objects.filter(ma_dh=chi_tiet.ma_dh).select_related('ma_mon')
        tong = sum(ct.so_luong * ct.ma_mon.gia for ct in chi_tiets)
        DonHang.objects.filter(ma_dh=chi_tiet.ma_dh).update(tong_tien=tong)

        return JsonResponse({
            'status': 'success',
            'message': 'Cap nhat mon thanh cong',
            'data': {
                'ma_ctdh': chi_tiet.ma_ctdh,
                'so_luong': chi_tiet.so_luong,
                'ghi_chu': chi_tiet.ghi_chu,
                'trang_thai_mon': chi_tiet.trang_thai_mon
            }
        })
    except ChiTietDonHang.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Khong tim thay mon'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def api_xoa_mon(request, ma_ctdh):
    """DELETE xoa mon khoi don - CHI NHAN VIEN"""
    if not check_staff_permission(request):
        return JsonResponse({'status': 'error', 'message': 'Khong co quyen truy cap'}, status=403)

    try:
        chi_tiet = ChiTietDonHang.objects.get(ma_ctdh=ma_ctdh)
        ma_dh = chi_tiet.ma_dh.ma_dh
        chi_tiet.delete()

        # Cap nhat tong tien
        chi_tiets = ChiTietDonHang.objects.filter(ma_dh=ma_dh).select_related('ma_mon')
        tong = sum(ct.so_luong * ct.ma_mon.gia for ct in chi_tiets)
        DonHang.objects.filter(ma_dh=ma_dh).update(tong_tien=tong)

        return JsonResponse({
            'status': 'success',
            'message': 'Xoa mon thanh cong'
        })
    except ChiTietDonHang.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Khong tim thay mon'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_thanh_toan(request):
    """POST thanh toan don hang - CHI NHAN VIEN"""
    if not check_staff_permission(request):
        return JsonResponse({'status': 'error', 'message': 'Khong co quyen truy cap'}, status=403)

    try:
        body = json.loads(request.body)
        ma_dh = body.get('ma_dh')
        phuong_thuc_tt = body.get('phuong_thuc_tt', 'Tiền mặt')
        giam_gia = Decimal(str(body.get('giam_gia', 0)))

        if not ma_dh:
            return JsonResponse({'status': 'error', 'message': 'Thieu ma_dh'}, status=400)

        don_hang = DonHang.objects.get(ma_dh=ma_dh)
        don_hang.trang_thai = 'Hoàn thành'
        don_hang.phuong_thuc_tt = phuong_thuc_tt
        don_hang.giam_gia = giam_gia
        don_hang.tong_tien = don_hang.tong_tien - giam_gia
        don_hang.save()

        # Cap nhat trang thai ban
        if don_hang.ma_ban:
            Ban.objects.filter(ma_ban=don_hang.ma_ban.ma_ban).update(trang_thai='Trống')

        return JsonResponse({
            'status': 'success',
            'message': 'Thanh toan thanh cong',
            'data': {
                'ma_dh': don_hang.ma_dh,
                'tong_tien': float(don_hang.tong_tien),
                'giam_gia': float(don_hang.giam_gia),
                'phuong_thuc_tt': don_hang.phuong_thuc_tt,
                'trang_thai': don_hang.trang_thai
            }
        })
    except DonHang.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Khong tim thay don hang'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_xem_don(request, ma_dh):
    """GET xem chi tiet don hang"""
    try:
        don_hang = DonHang.objects.select_related('ma_ban', 'ma_kh').get(ma_dh=ma_dh)
        chi_tiets = ChiTietDonHang.objects.filter(ma_dh=ma_dh).select_related('ma_mon')

        return JsonResponse({
            'status': 'success',
            'data': {
                'ma_dh': don_hang.ma_dh,
                'ban': don_hang.ma_ban.ten_ban if don_hang.ma_ban else None,
                'khach_hang': don_hang.ma_kh.ho_ten if don_hang.ma_kh else None,
                'nguon_don': don_hang.nguon_don,
                'trang_thai': don_hang.trang_thai,
                'tong_tien': float(don_hang.tong_tien),
                'giam_gia': float(don_hang.giam_gia),
                'phuong_thuc_tt': don_hang.phuong_thuc_tt,
                'ngay_tao': don_hang.ngay_tao.strftime('%Y-%m-%d %H:%M:%S'),
                'chi_tiet': [{
                    'ma_ctdh': ct.ma_ctdh,
                    'ten_mon': ct.ma_mon.ten_sp,
                    'so_luong': ct.so_luong,
                    'gia': float(ct.ma_mon.gia),
                    'thanh_tien': float(ct.so_luong * ct.ma_mon.gia),
                    'ghi_chu': ct.ghi_chu,
                    'trang_thai_mon': ct.trang_thai_mon
                } for ct in chi_tiets]
            }
        })
    except DonHang.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Khong tim thay don hang'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_danh_sach_don(request):
    """GET danh sách đơn hàng với filter"""
    try:
        # Lấy tham số filter từ query string
        trang_thai = request.GET.get('trang_thai')
        nguon_don = request.GET.get('nguon_don')
        ngay_tu = request.GET.get('ngay_tu')
        ngay_den = request.GET.get('ngay_den')

        # Query cơ bản
        don_hangs = DonHang.objects.select_related('ma_ban', 'ma_kh').all().order_by('-ngay_tao')

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
            so_mon = ChiTietDonHang.objects.filter(ma_dh=dh.ma_dh).count()

            data.append({
                'ma_dh': dh.ma_dh,
                'ban': dh.ma_ban.ten_ban if dh.ma_ban else 'Không có bàn',
                'khach_hang': dh.ma_kh.ho_ten if dh.ma_kh else 'Khách vãng lai',
                'nguon_don': dh.nguon_don,
                'trang_thai': dh.trang_thai,
                'tong_tien': float(dh.tong_tien),
                'so_mon': so_mon,
                'ngay_tao': dh.ngay_tao.strftime('%Y-%m-%d %H:%M:%S'),
                'phuong_thuc_tt': dh.phuong_thuc_tt
            })

        return JsonResponse({
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
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_tao_don_online(request):

    if request.method == "GET":
        ma_nd = request.GET.get("ma_nd")


    else:
        if not request.body:
            return JsonResponse(
                {"error": "Body JSON trống"},
                status=400
            )

        body = json.loads(request.body)
        ma_nd = body.get("ma_nd")

    if not ma_nd:
        return JsonResponse({"error": "Thiếu ma_nd"}, status=400)

    try:
        kh = KhachHang.objects.get(ma_nd_id=ma_nd)
    except KhachHang.DoesNotExist:
        return JsonResponse({"error": "Khách hàng không tồn tại"}, status=404)

    don = DonHang.objects.create(
        ma_kh=kh,
        ma_ban=None,
        ma_nv=2,
        nguon_don="online",
        trang_thai="Chờ xác nhận",
        tong_tien=0,
        giam_gia=0,
        phuong_thuc_tt="Tiền mặt",
        ngay_tao=datetime.now()
    )

    return JsonResponse({
        "status": "success",
        "message": "Tạo đơn online thành công",
        "ma_dh": don.ma_dh
    }, status=201)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_them_chi_tiet_online(request):
    try:
        body = json.loads(request.body)
        ma_dh = body.get("ma_dh")
        ma_sp = body.get("ma_sp")
        so_luong = int(body.get("so_luong", 1))
        ghi_chu = body.get("ghi_chu", "")

        if not ma_dh or not ma_sp:
            return JsonResponse(
                {"error": "Thiếu mã đơn hoặc mã sản phẩm"},
                status=400
            )

        try:
            don = DonHang.objects.get(ma_dh=ma_dh, nguon_don='online')
            sp = SanPham.objects.get(ma_sp=ma_sp)
        except DonHang.DoesNotExist:
            return JsonResponse({"error": "Đơn online không tồn tại"}, status=404)
        except SanPham.DoesNotExist:
            return JsonResponse({"error": "Sản phẩm không tồn tại"}, status=404)

        ChiTietDonHang.objects.create(
            ma_dh=don,
            ma_mon=sp,
            so_luong=so_luong,
            ghi_chu=ghi_chu,
            trang_thai_mon='Chờ làm'
        )

        #  Cập nhật tổng tiền
        tong = sum(
            ct.ma_mon.gia * ct.so_luong
            for ct in ChiTietDonHang.objects.filter(ma_dh=don)
        )

        don.tong_tien = tong
        don.save()

        return JsonResponse({
            "status": "success",
            "message": "Thêm món thành công",
            "tong_tien": float(don.tong_tien)
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def api_xem_don_online(request):
    ma_dh = request.GET.get("ma_dh")

    if not ma_dh:
        return JsonResponse({"error": "Thiếu mã đơn"}, status=400)

    try:
        don = DonHang.objects.get(ma_dh=ma_dh)
    except DonHang.DoesNotExist:
        return JsonResponse({"error": "Không tìm thấy đơn"}, status=404)

    return JsonResponse({
        "ma_dh": don.ma_dh,
        "nguon_don": don.nguon_don,
        "trang_thai": don.trang_thai,
        "tong_tien": float(don.tong_tien),
        "khach_hang": don.ma_kh.ho_ten if don.ma_kh else None,
        "ds_san_pham": [
            {
                "ten_sp": ct.ma_mon.ten_sp,
                "gia": float(ct.ma_mon.gia),
                "so_luong": ct.so_luong,
                "ghi_chu": ct.ghi_chu,
                "trang_thai_mon": ct.trang_thai_mon
            }
            for ct in don.chi_tiet.all()
        ]
    })

@csrf_exempt
@require_http_methods(["GET"])
def api_lich_su_don_online(request):
    ma_nd = request.GET.get("ma_nd")
    trang_thai = request.GET.get("trang_thai")  # optional

    if not ma_nd:
        return JsonResponse(
            {"error": "Thiếu ma_nd"},
            status=400
        )

    try:
        kh = KhachHang.objects.get(ma_nd_id=ma_nd, loai_khach="online")
    except KhachHang.DoesNotExist:
        return JsonResponse(
            {"error": "Khách hàng online không tồn tại"},
            status=404
        )

    # Lấy đơn ONLINE của khách
    don_hangs = DonHang.objects.filter(
        ma_kh=kh,
        nguon_don="online"
    ).order_by("-ngay_tao")


    if trang_thai:
        don_hangs = don_hangs.filter(trang_thai=trang_thai)

    data = []
    for dh in don_hangs:
        so_mon = ChiTietDonHang.objects.filter(ma_dh=dh).count()

        data.append({
            "ma_dh": dh.ma_dh,
            "trang_thai": dh.trang_thai,
            "tong_tien": float(dh.tong_tien),
            "so_mon": so_mon,
            "ngay_tao": dh.ngay_tao.strftime("%Y-%m-%d %H:%M:%S")
        })

    return JsonResponse({
        "status": "success",
        "ma_nd": ma_nd,
        "total": len(data),
        "data": data
    })

