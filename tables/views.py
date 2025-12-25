from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Ban
import json

# ============= HELPER FUNCTION =============
def check_staff_permission(request):
    """Kiem tra quyen Nhan vien"""
    vai_tro = request.session.get('vai_tro')
    if vai_tro != 'Nhân viên':
        return False
    return True

# ============= BAN API =============
@csrf_exempt
@require_http_methods(["GET"])
def api_ban_list(request):
    """GET danh sach ban"""
    bans = Ban.objects.all()
    data = [{'ma_ban': ban.ma_ban, 'ten_ban': ban.ten_ban, 'trang_thai': ban.trang_thai} for ban in bans]
    return JsonResponse({'status': 'success', 'data': data, 'total': len(data)})

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
            'data': {'ma_ban': ban.ma_ban, 'ten_ban': ban.ten_ban, 'trang_thai': ban.trang_thai}
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
            'data': {'ma_ban': ban.ma_ban, 'ten_ban': ban.ten_ban, 'trang_thai': ban.trang_thai}
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
            'data': {'ma_ban': ban.ma_ban, 'ten_ban': ban.ten_ban, 'trang_thai': ban.trang_thai}
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
        return JsonResponse({'status': 'success', 'message': 'Xoa ban thanh cong'})
    except Ban.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Khong tim thay ban'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
