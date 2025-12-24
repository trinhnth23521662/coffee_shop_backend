from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, NhanVien, KhachHang

# ================= LOGIN =================
@method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Thiếu thông tin'}, status=400)

        user = User.objects.filter(ten_dang_nhap=username, mat_khau=password).first()

        request.session['user_id'] = user.ma_nd
        request.session['vai_tro'] = user.vai_tro

        if not user:
            return Response({'error': 'Sai tài khoản hoặc mật khẩu'}, status=401)

        # menu theo vai trò
        if user.vai_tro == 'Admin':
            menu = [{'name': 'Quản lý nhân viên', 'url': request.build_absolute_uri('/api/auth/admin/employees/')},
                    {'name': 'Báo cáo', 'url': request.build_absolute_uri('/api/auth/admin/reports/')},
                    {'name': 'Quản lý bàn', 'url': request.build_absolute_uri('/api/tables/')},]
        elif user.vai_tro == 'Nhân viên':
            menu = [{'name': 'Đơn hàng', 'url': request.build_absolute_uri('/api/auth/staff/orders/')}]
        else:
            menu = [{'name': 'Sản phẩm', 'url': request.build_absolute_uri('/api/auth/customer/products/')}]

        return Response({
            'message': 'Đăng nhập thành công',
            'user_id': user.ma_nd,
            'username': user.ten_dang_nhap,
            'role': user.vai_tro,
            'menu': menu
        })


# ================= REGISTER =================
@method_decorator(csrf_exempt, name='dispatch')
class RegisterAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        ho_ten = request.data.get('ho_ten')
        sdt = request.data.get('sdt')
        dia_chi = request.data.get('dia_chi')

        if not username or not password or not ho_ten:
            return Response({'error': 'Thiếu thông tin'}, status=400)

        if User.objects.filter(ten_dang_nhap=username).exists():
            return Response({'error': 'Username đã tồn tại'}, status=400)

        user = User.objects.create(
            ten_dang_nhap=username,
            mat_khau=password,
            vai_tro='Khách hàng'
        )

        KhachHang.objects.create(
            ho_ten=ho_ten,
            sdt=sdt,
            dia_chi=dia_chi,
            loai_khach='online',
            ma_nd=user
        )

        return Response({
            'message': 'Đăng ký thành công',
            'username': user.ten_dang_nhap,
            'role': user.vai_tro
        }, status=201)


# ================= ADMIN =================
@method_decorator(csrf_exempt, name='dispatch')
class AdminDashboardAPIView(APIView):
    def get(self, request):
        return Response({'message': 'Admin Dashboard'})

@method_decorator(csrf_exempt, name='dispatch')
class EmployeeAPIView(APIView):
    def get(self, request, id=None):
        if id:
            # Lấy chi tiết nhân viên theo ID
            try:
                u = User.objects.get(ma_nd=id, vai_tro='Nhân viên')
                nhanvien = NhanVien.objects.get(ma_nd=u)
                data = {
                    'id': u.ma_nd,
                    'username': u.ten_dang_nhap,
                    'ho_ten': nhanvien.ho_ten,
                    'sdt': nhanvien.sdt,
                    'dia_chi': nhanvien.dia_chi,
                }
                return Response(data)
            except User.DoesNotExist:
                return Response({'error': 'Nhân viên không tồn tại'}, status=404)
            except NhanVien.DoesNotExist:
                return Response({'error': 'Thông tin nhân viên không tồn tại'}, status=404)
        else:
            # Lấy danh sách tất cả nhân viên
            staffs = User.objects.filter(vai_tro='Nhân viên')
            data = []
            for u in staffs:
                try:
                    nhanvien = NhanVien.objects.get(ma_nd=u)
                    data.append({
                        'id': u.ma_nd,
                        'username': u.ten_dang_nhap,
                        'ho_ten': nhanvien.ho_ten,
                        'sdt': nhanvien.sdt,
                        'dia_chi': nhanvien.dia_chi,
                    })
                except NhanVien.DoesNotExist:
                    data.append({
                        'id': u.ma_nd,
                        'username': u.ten_dang_nhap,
                        'ho_ten': '',
                        'sdt': '',
                        'dia_chi': '',
                    })
            return Response(data)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        ho_ten = request.data.get('ho_ten')
        sdt = request.data.get('sdt')
        dia_chi = request.data.get('dia_chi')

        if not username or not password or not ho_ten:
            return Response({'error': 'Thiếu thông tin'}, status=400)

        if User.objects.filter(ten_dang_nhap=username).exists():
            return Response({'error': 'Username đã tồn tại'}, status=400)

        user = User.objects.create(
            ten_dang_nhap=username,
            mat_khau=password,
            vai_tro='Nhân viên'
        )

        NhanVien.objects.create(
            ho_ten=ho_ten,
            sdt=sdt,
            dia_chi=dia_chi,
            ma_nd=user
        )

        return Response({'message': 'Tạo nhân viên thành công'}, status=201)

    def delete(self, request, id=None):
        if not id:
            return Response({'error': 'ID nhân viên bắt buộc'}, status=400)
        try:
            user = User.objects.get(ma_nd=id, vai_tro='Nhân viên')
            # Xóa thông tin nhân viên trước
            try:
                nhanvien = NhanVien.objects.get(ma_nd=user)
                nhanvien.delete()
            except NhanVien.DoesNotExist:
                pass
            # Xóa user
            user.delete()
            return Response({'message': 'Xóa nhân viên thành công'})
        except User.DoesNotExist:
            return Response({'error': 'Nhân viên không tồn tại'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class ReportAPIView(APIView):
    def get(self, request):
        return Response({
            'total_users': User.objects.count(),
            'staff': User.objects.filter(vai_tro='Nhân viên').count(),
            'customers': User.objects.filter(vai_tro='Khách hàng').count()
        })


# ================= STAFF =================
@method_decorator(csrf_exempt, name='dispatch')
class StaffDashboardAPIView(APIView):
    def get(self, request):
        return Response({'message': 'Staff Dashboard'})


# ================= CUSTOMER =================
@method_decorator(csrf_exempt, name='dispatch')
class CustomerDashboardAPIView(APIView):
    def get(self, request):
        return Response({'message': 'Customer Dashboard'})
