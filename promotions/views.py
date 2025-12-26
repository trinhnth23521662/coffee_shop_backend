from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import KhuyenMai
from datetime import datetime
import json


def check_staff_permission(request):
    """Kiểm tra quyền Nhân viên"""
    vai_tro = request.session.get('vai_tro')
    return vai_tro == 'Nhân viên'


# ============= API QUẢN LÝ KHUYẾN MÃI =============
@csrf_exempt
@require_http_methods(["GET"])
def api_khuyenmai_list(request):
    """GET danh sách khuyến mãi với filter"""
    try:
        now = datetime.now()
        trang_thai = request.GET.get('trang_thai', 'Đang áp dụng')

        # Base query
        khuyenmais = KhuyenMai.objects.filter(
            ngay_bd__lte=now,
            ngay_kt__gte=now
        )

        # Filter theo trạng thái
        if trang_thai:
            khuyenmais = khuyenmais.filter(trang_thai=trang_thai)

        data = [{
            'ma_km': km.ma_km,
            'ten_km': km.ten_km,
            'loai_km': km.loai_km,
            'gia_tri': float(km.gia_tri),
            'dieu_kien': float(km.dieu_kien),
            'ngay_bd': km.ngay_bd.strftime('%Y-%m-%d %H:%M:%S'),
            'ngay_kt': km.ngay_kt.strftime('%Y-%m-%d %H:%M:%S'),
            'trang_thai': km.trang_thai
        } for km in khuyenmais]

        return JsonResponse({
            'status': 'success',
            'data': data,
            'total': len(data),
            'now': now.strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_khuyenmai_create(request):
    """POST tạo khuyến mãi mới - CHỈ ADMIN/NHÂN VIÊN"""
    if not check_staff_permission(request):
        return JsonResponse({'status': 'error', 'message': 'Không có quyền truy cập'}, status=403)

    try:
        body = json.loads(request.body)
        khuyenmai = KhuyenMai.objects.create(
            ten_km=body.get('ten_km'),
            loai_km=body.get('loai_km'),  # 'Phần trăm' hoặc 'Tiền mặt'
            gia_tri=body.get('gia_tri'),
            dieu_kien=body.get('dieu_kien', 0),
            ngay_bd=datetime.strptime(body.get('ngay_bd'), '%Y-%m-%d %H:%M:%S'),
            ngay_kt=datetime.strptime(body.get('ngay_kt'), '%Y-%m-%d %H:%M:%S'),
            trang_thai='Đang áp dụng'
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Tạo khuyến mãi thành công',
            'data': {'ma_km': khuyenmai.ma_km, 'ten_km': khuyenmai.ten_km}
        }, status=201)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_tinh_giam_gia(request):
    """GET tính giảm giá tự động cho đơn hàng"""
    try:
        tong_tien = float(request.GET.get('tong_tien', 0))
        ma_km = request.GET.get('ma_km')  # Nếu chọn cụ thể

        giam_gia = 0
        khuyenmai_ap_dung = None

        if ma_km:
            # Nếu chọn cụ thể khuyến mãi
            km = KhuyenMai.objects.get(ma_km=ma_km, trang_thai='Đang áp dụng')
            if tong_tien >= km.dieu_kien:
                khuyenmai_ap_dung = km
        else:
            # Tự động tìm khuyến mãi phù hợp
            now = datetime.now()
            khuyenmais = KhuyenMai.objects.filter(
                trang_thai='Đang áp dụng',
                ngay_bd__lte=now,
                ngay_kt__gte=now,
                dieu_kien__lte=tong_tien
            ).order_by('-gia_tri')

            if khuyenmais.exists():
                khuyenmai_ap_dung = khuyenmais.first()

        # Tính giảm giá
        if khuyenmai_ap_dung:
            if khuyenmai_ap_dung.loai_km == 'Phần trăm':
                giam_gia = tong_tien * (khuyenmai_ap_dung.gia_tri / 100)
            else:  # Tiền mặt
                giam_gia = khuyenmai_ap_dung.gia_tri

            # Không giảm quá tổng tiền
            giam_gia = min(giam_gia, tong_tien)

        return JsonResponse({
            'status': 'success',
            'giam_gia': giam_gia,
            'khuyenmai': {
                'ma_km': khuyenmai_ap_dung.ma_km if khuyenmai_ap_dung else None,
                'ten_km': khuyenmai_ap_dung.ten_km if khuyenmai_ap_dung else None,
                'loai_km': khuyenmai_ap_dung.loai_km if khuyenmai_ap_dung else None
            },
            'tong_tien_sau_giam': tong_tien - giam_gia
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
