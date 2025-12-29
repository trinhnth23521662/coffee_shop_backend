from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework import status

from .models import User, NhanVien, KhachHang
from .permissions import IsLoggedIn, IsAdmin, IsStaff, IsCustomer


# ================= AUTH =================
@method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        ten_dang_nhap = request.data.get('username')
        mat_khau = request.data.get('password')

        if not ten_dang_nhap or not mat_khau:
            return Response(
                {'error': 'Thiếu username hoặc password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(
            ten_dang_nhap=ten_dang_nhap,
            mat_khau=mat_khau
        ).first()

        if not user:
            return Response(
                {'error': 'Sai tài khoản hoặc mật khẩu'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # ===== LƯU SESSION =====
        request.session['user_id'] = user.ma_nd
        request.session['role'] = user.vai_tro

        # ===== ĐIỀU HƯỚNG DASHBOARD =====
        if user.vai_tro == 'Admin':
            redirect_to = '/api/auth/admin/dashboard/'
        elif user.vai_tro == 'Nhân viên':
            redirect_to = '/api/auth/staff/dashboard/'
        elif user.vai_tro == 'Khách hàng':
            redirect_to = '/api/auth/customer/dashboard/'
        else:
            redirect_to = None

        return Response({
            'message': 'Đăng nhập thành công',
            'ma_nd': user.ma_nd,
            'ten_dang_nhap': user.ten_dang_nhap,
            'vai_tro': user.vai_tro,
            'redirect_to': '/api/auth/dashboard/'
        })


@method_decorator(csrf_exempt, name='dispatch')
class RegisterAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        ten_dang_nhap = request.data.get('username')
        mat_khau = request.data.get('password')
        ho_ten = request.data.get('ho_ten')
        sdt = request.data.get('sdt')
        dia_chi = request.data.get('dia_chi')

        if not ten_dang_nhap or not mat_khau or not ho_ten:
            return Response(
                {'error': 'Thiếu thông tin bắt buộc'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(ten_dang_nhap=ten_dang_nhap).exists():
            return Response(
                {'error': 'Username đã tồn tại'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create(
            ten_dang_nhap=ten_dang_nhap,
            mat_khau=mat_khau,
            vai_tro='Khách hàng'
        )

        KhachHang.objects.create(
            ma_nd=user,
            ho_ten=ho_ten,
            sdt=sdt,
            dia_chi=dia_chi,
            loai_khach='online'
        )

        return Response(
            {'message': 'Đăng ký thành công'},
            status=status.HTTP_201_CREATED
        )


# ================= DASHBOARD =================
@method_decorator(csrf_exempt, name='dispatch')
class DashboardAPIView(APIView):
    def get(self, request):
        role = request.session.get('role')

        if not role:
            return Response(
                {'error': 'Chưa đăng nhập'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if role == 'Admin':
            data = {
                'role': role,
                'features': {
                    'employees': {
                        'list': 'GET /api/admin/employees/',
                        'create': 'POST /api/admin/employees/',
                        'detail': 'GET /api/admin/employees/{id}/',
                        'update': 'PUT /api/admin/employees/{id}/',
                        'delete': 'DELETE /api/admin/employees/{id}/',
                    },
                    'reports': {
                        'overview': 'GET /api/admin/reports/',
                    },
                    'promotions': {
                        'list': 'GET /api/admin/promotions/',
                        'create': 'POST /api/admin/promotions/',
                        'detail': 'GET /api/admin/promotions/{id}/',
                        'update': 'PUT /api/admin/promotions/{id}/',
                        'delete': 'DELETE /api/admin/promotions/{id}/',
                    }
                }
            }
        elif role == 'Nhân viên':
            data = {
                'role': role,
                'features': {
                    'products': {
                        'list': 'GET /api/staff/menu/products/',
                        'create': 'POST /api/staff/menu/products/',
                        'detail': 'GET /api/staff/menu/products/{id}/',
                        'update': 'PUT /api/staff/menu/products/{id}/',
                        'delete': 'DELETE /api/staff/menu/products/{id}/',
                    },
                    'categories': {
                        'list': 'GET /api/staff/menu/categories/',
                        'create': 'POST /api/staff/menu/categories/',
                        'update': 'PUT /api/staff/menu/categories/{id}/',
                        'delete': 'DELETE /api/staff/menu/categories/{id}/',
                    },
                    'tables': {
                        'list': 'GET /api/staff/tables/',
                        'create': 'POST /api/staff/tables/',
                        'detail': 'GET /api/staff/tables/{id}/',
                        'update': 'PUT /api/staff/tables/{id}/',
                        'change_status': 'PATCH /api/staff/tables/{id}/status/',
                        'delete': 'DELETE /api/staff/tables/{id}/',
                    },
                    'orders': {
                        'create': 'POST /api/staff/orders/',
                        'detail': 'GET /api/staff/orders/{id}/',
                        'add_item': 'POST /api/staff/orders/{id}/items/',
                        'list': 'GET /api/staff/orders/',
                        'create_full': 'POST /api/staff/orders/create/',
                        'add_order_item': 'POST /api/staff/orders/add-item/',
                        'update_order_item': 'PUT /api/staff/orders/update-item/{id}/',
                        'delete_order_item': 'DELETE /api/staff/orders/delete-item/{id}/',
                        'process_payment': 'POST /api/staff/orders/payment/',
                        'online_orders': {
                            'create': 'POST /api/staff/orders/online-orders/create/',
                            'add_item': 'POST /api/staff/orders/online-orders/add-item/',
                            'view': 'GET /api/staff/orders/online-orders/view/',
                            'history': 'GET /api/staff/orders/online-orders/history/'
                        }
                }
            }
        elif role == 'Khách hàng':
            data = {
                'role': role,
                'features': {
                    'menu': {
                        'view': 'GET /api/public/menu/',
                    },
                    'tables': {
                        'view': 'GET /api/public/tables/',
                    },
                    'promotions': {
                        'list': 'GET /api/admin/promotions/',
                    }
                }
            }

        else:
            data = {
                'role': role,
                'features': {}
            }

        return Response(data)


