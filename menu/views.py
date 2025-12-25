from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import LoaiSP, SanPham
from decimal import Decimal
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
    return JsonResponse({'status': 'success', 'data': data, 'total': len(data)})

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
            'data': {'ma_loaisp': loai_sp.ma_loaisp, 'ten_loaisp': loai_sp.ten_loaisp}
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
            'data': {'ma_loaisp': loai_sp.ma_loaisp, 'ten_loaisp': loai_sp.ten_loaisp}
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
        return JsonResponse({'status': 'success', 'message': 'Xoa thanh cong'})
    except LoaiSP.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Khong tim thay loai san pham'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# ============= SAN PHAM API =============
@csrf_exempt
@require_http_methods(["GET"])
def api_sanpham_list(request):
    """GET danh sach san pham"""
    san_phams = SanPham.objects.select_related('ma_loaisp').all()
    data = [{
        'ma_sp': sp.ma_sp,
        'ten_sp': sp.ten_sp,
        'gia': float(sp.gia),
        'trang_thai': sp.trang_thai,
        'ma_loaisp': sp.ma_loaisp.ma_loaisp,
        'ten_loaisp': sp.ma_loaisp.ten_loaisp
    } for sp in san_phams]
    return JsonResponse({'status': 'success', 'data': data, 'total': len(data)})

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
        'loai': {'ma_loaisp': sp.ma_loaisp.ma_loaisp, 'ten_loaisp': sp.ma_loaisp.ten_loaisp}
    } for sp in san_phams]
    return JsonResponse({'status': 'success', 'data': data, 'total': len(data)})

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
            'data': {'ma_sp': san_pham.ma_sp, 'ten_sp': san_pham.ten_sp, 'gia': float(san_pham.gia), 'trang_thai': san_pham.trang_thai}
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
            'data': {'ma_sp': san_pham.ma_sp, 'ten_sp': san_pham.ten_sp, 'gia': float(san_pham.gia), 'trang_thai': san_pham.trang_thai}
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
        return JsonResponse({'status': 'success', 'message': 'Xoa mem thanh cong (doi trang thai thanh Het)'})
    except SanPham.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Khong tim thay san pham'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
