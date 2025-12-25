from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import DonHang, ChiTietDonHang, SanPham, Ban, LoaiSP, KhachHang
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


# ============= LOAI SAN PHAM API =============

@csrf_exempt
@require_http_methods(["GET"])
def api_loaisp_list(request):
    """GET danh sach loai san pham"""
    loai_sps = LoaiSP.objects.all()
    data = [{
        'ma_loaisp': loai.ma_loaisp,
        'ten_loaisp': loai.ten_loaisp
    } for loai in loai_sps]

    return JsonResponse({
        'status': 'success',
        'data': data,
        'total': len(data)
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_loaisp_create(request):
    """POST them loai san pham - CHI NHAN VIEN"""
    if not check_staff_permission(request):
        return JsonResponse({'status': 'error', 'message': 'Khong co quyen truy cap'}, status=403)

    try:
        body = json.loads(request.body)
        ten_loaisp = body.get('ten_loaisp')

        if not ten_loaisp:
            return JsonResponse({'status': 'error', 'message': 'Thieu ten_loaisp'}, status=400)

        loai_sp = LoaiSP.objects.create(ten_loaisp=ten_loaisp)

        return JsonResponse({
            'status': 'success',
            'message': 'Them loai san pham thanh cong',
            'data': {
                'ma_loaisp': loai_sp.ma_loaisp,
                'ten_loaisp': loai_sp.ten_loaisp
            }
        }, status=201)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def api_loaisp_update(request, ma_loaisp):
    """PUT cap nhat loai san pham - CHI NHAN VIEN"""
    if not check_staff_permission(request):
        return JsonResponse({'status': 'error', 'message': 'Khong co quyen truy cap'}, status=403)

    try:
        loai_sp = LoaiSP.objects.get(ma_loaisp=ma_loaisp)
        body = json.loads(request.body)

        loai_sp.ten_loaisp = body.get('ten_loaisp', loai_sp.ten_loaisp)
        loai_sp.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Cap nhat thanh cong',
            'data': {
                'ma_loaisp': loai_sp.ma_loaisp,
                'ten_loaisp': loai_sp.ten_loaisp
            }
        })
    except LoaiSP.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Khong tim thay loai san pham'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def api_loaisp_delete(request, ma_loaisp):
    """DELETE xoa loai san pham - CHI NHAN VIEN"""
    if not check_staff_permission(request):
        return JsonResponse({'status': 'error', 'message': 'Khong co quyen truy cap'}, status=403)

    try:
        loai_sp = LoaiSP.objects.get(ma_loaisp=ma_loaisp)
        loai_sp.delete()

        return JsonResponse({
            'status': 'success',
            'message': 'Xoa thanh cong'
        })
    except LoaiSP.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Khong tim thay loai san pham'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ============= SAN PHAM API =============

@csrf_exempt
@require_http_methods(["GET"])
def api_sanpham_list(request):
    """GET danh sach san pham (menu)"""
    san_phams = SanPham.objects.select_related('ma_loaisp').all()
    data = [{
        'ma_sp': sp.ma_sp,
        'ten_sp': sp.ten_sp,
        'gia': float(sp.gia),
        'trang_thai': sp.trang_thai,
        'ma_loaisp': sp.ma_loaisp.ma_loaisp,
        'ten_loaisp': sp.ma_loaisp.ten_loaisp
    } for sp in san_phams]

    return JsonResponse({
        'status': 'success',
        'data': data,
        'total': len(data)
    })


@csrf_exempt
@require_http_methods(["GET"])
def api_menu(request):
    """GET menu (chi lay san pham con hang)"""
    san_phams = SanPham.objects.select_related('ma_loaisp').filter(trang_thai='Còn')
    data = [{
        'ma_sp': sp.ma_sp,
        'ten_sp': sp.ten_sp,
        'gia': float(sp.gia),
        'trang_thai': sp.trang_thai,
        'loai': {
            'ma_loaisp': sp.ma_loaisp.ma_loaisp,
            'ten_loaisp': sp.ma_loaisp.ten_loaisp
        }
    } for sp in san_phams]

    return JsonResponse({
        'status': 'success',
        'data': data,
        'total': len(data)
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_sanpham_create(request):
    """POST them san pham - CHI NHAN VIEN"""
    if not check_staff_permission(request):
        return JsonResponse({'status': 'error', 'message': 'Khong co quyen truy cap'}, status=403)

    try:
        body = json.loads(request.body)
        ten_sp = body.get('ten_sp')
        gia = body.get('gia')
        ma_loaisp = body.get('ma_loaisp')
        trang_thai = body.get('trang_thai', 'Còn')

        if not all([ten_sp, gia, ma_loaisp]):
            return JsonResponse({'status': 'error', 'message': 'Thieu thong tin bat buoc'}, status=400)

        san_pham = SanPham.objects.create(
            ten_sp=ten_sp,
            gia=Decimal(str(gia)),
            trang_thai=trang_thai,
            ma_loaisp_id=ma_loaisp
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Them san pham thanh cong',
            'data': {
                'ma_sp': san_pham.ma_sp,
                'ten_sp': san_pham.ten_sp,
                'gia': float(san_pham.gia),
                'trang_thai': san_pham.trang_thai
            }
        }, status=201)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def api_sanpham_update(request, ma_sp):
    """PUT cap nhat san pham - CHI NHAN VIEN"""
    if not check_staff_permission(request):
        return JsonResponse({'status': 'error', 'message': 'Khong co quyen truy cap'}, status=403)

    try:
        san_pham = SanPham.objects.get(ma_sp=ma_sp)
        body = json.loads(request.body)

        san_pham.ten_sp = body.get('ten_sp', san_pham.ten_sp)
        san_pham.gia = Decimal(str(body.get('gia', san_pham.gia)))
        san_pham.trang_thai = body.get('trang_thai', san_pham.trang_thai)
        if 'ma_loaisp' in body:
            san_pham.ma_loaisp_id = body['ma_loaisp']
        san_pham.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Cap nhat thanh cong',
            'data': {
                'ma_sp': san_pham.ma_sp,
                'ten_sp': san_pham.ten_sp,
                'gia': float(san_pham.gia),
                'trang_thai': san_pham.trang_thai
            }
        })
    except SanPham.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Khong tim thay san pham'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def api_sanpham_delete(request, ma_sp):
    """DELETE mem san pham (doi trang thai thanh Het) - CHI NHAN VIEN"""
    if not check_staff_permission(request):
        return JsonResponse({'status': 'error', 'message': 'Khong co quyen truy cap'}, status=403)

    try:
        san_pham = SanPham.objects.get(ma_sp=ma_sp)
        san_pham.trang_thai = 'Hết'
        san_pham.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Xoa mem thanh cong (doi trang thai thanh Het)'
        })
    except SanPham.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Khong tim thay san pham'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ============= BAN API =============

@csrf_exempt
@require_http_methods(["GET"])
def api_ban_list(request):
    """GET danh sach ban"""
    bans = Ban.objects.all()
    data = [{
        'ma_ban': ban.ma_ban,
        'ten_ban': ban.ten_ban,
        'trang_thai': ban.trang_thai
    } for ban in bans]

    return JsonResponse({
        'status': 'success',
        'data': data,
        'total': len(data)
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_ban_create(request):
    """POST them ban - CHI NHAN VIEN"""
    if not check_staff_permission(request):
        return JsonResponse({'status': 'error', 'message': 'Khong co quyen truy cap'}, status=403)

    try:
        body = json.loads(request.body)
        ten_ban = body.get('ten_ban')
        trang_thai = body.get('trang_thai', 'Trống')

        if not ten_ban:
            return JsonResponse({'status': 'error', 'message': 'Thieu ten_ban'}, status=400)

        ban = Ban.objects.create(ten_ban=ten_ban, trang_thai=trang_thai)

        return JsonResponse({
            'status': 'success',
            'message': 'Them ban thanh cong',
            'data': {
                'ma_ban': ban.ma_ban,
                'ten_ban': ban.ten_ban,
                'trang_thai': ban.trang_thai
            }
        }, status=201)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def api_ban_update(request, ma_ban):
    """PUT cap nhat ban - CHI NHAN VIEN"""
    if not check_staff_permission(request):
        return JsonResponse({'status': 'error', 'message': 'Khong co quyen truy cap'}, status=403)

    try:
        ban = Ban.objects.get(ma_ban=ma_ban)
        body = json.loads(request.body)

        ban.ten_ban = body.get('ten_ban', ban.ten_ban)
        ban.trang_thai = body.get('trang_thai', ban.trang_thai)
        ban.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Cap nhat thanh cong',
            'data': {
                'ma_ban': ban.ma_ban,
                'ten_ban': ban.ten_ban,
                'trang_thai': ban.trang_thai
            }
        })
    except Ban.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Khong tim thay ban'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PATCH"])
def api_ban_update_status(request, ma_ban):
    """PATCH cap nhat trang thai ban - CHI NHAN VIEN"""
    if not check_staff_permission(request):
        return JsonResponse({'status': 'error', 'message': 'Khong co quyen truy cap'}, status=403)

    try:
        ban = Ban.objects.get(ma_ban=ma_ban)
        body = json.loads(request.body)
        trang_thai = body.get('trang_thai')

        if not trang_thai:
            return JsonResponse({'status': 'error', 'message': 'Thieu trang_thai'}, status=400)

        ban.trang_thai = trang_thai
        ban.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Cap nhat trang thai thanh cong',
            'data': {
                'ma_ban': ban.ma_ban,
                'ten_ban': ban.ten_ban,
                'trang_thai': ban.trang_thai
            }
        })
    except Ban.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Khong tim thay ban'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def api_ban_delete(request, ma_ban):
    """DELETE xoa ban - CHI NHAN VIEN"""
    if not check_staff_permission(request):
        return JsonResponse({'status': 'error', 'message': 'Khong co quyen truy cap'}, status=403)

    try:
        ban = Ban.objects.get(ma_ban=ma_ban)
        ban.delete()

        return JsonResponse({
            'status': 'success',
            'message': 'Xoa ban thanh cong'
        })
    except Ban.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Khong tim thay ban'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


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
