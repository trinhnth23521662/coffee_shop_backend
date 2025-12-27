from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.permissions import IsAdmin
from accounts.models import User, NhanVien
from orders.models import DonHang

@method_decorator(csrf_exempt, name='dispatch')
class EmployeeAPIView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, id=None):
        if id:
            try:
                user = User.objects.get(ma_nd=id, vai_tro='Nhân viên')
                nv = NhanVien.objects.get(ma_nd=user)
                return Response({
                    'id': user.ma_nd,
                    'username': user.ten_dang_nhap,
                    'ho_ten': nv.ho_ten,
                    'sdt': nv.sdt,
                    'dia_chi': nv.dia_chi,
                })
            except User.DoesNotExist:
                return Response({'error': 'Nhân viên không tồn tại'}, status=404)
            except NhanVien.DoesNotExist:
                return Response({'error': 'Thiếu thông tin nhân viên'}, status=404)

        staffs = User.objects.filter(vai_tro='Nhân viên')
        data = []
        for u in staffs:
            nv = NhanVien.objects.filter(ma_nd=u).first()
            data.append({
                'id': u.ma_nd,
                'username': u.ten_dang_nhap,
                'ho_ten': nv.ho_ten if nv else '',
                'sdt': nv.sdt if nv else '',
                'dia_chi': nv.dia_chi if nv else '',
            })
        return Response(data)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        ho_ten = request.data.get('ho_ten')

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
            ma_nd=user,
            ho_ten=ho_ten,
            sdt=request.data.get('sdt'),
            dia_chi=request.data.get('dia_chi')
        )

        return Response({'message': 'Tạo nhân viên thành công'}, status=201)
    def put(self, request, id=None):
        if not id:
            return Response({'error': 'Thiếu ID'}, status=400)

        try:
            user = User.objects.get(ma_nd=id, vai_tro='Nhân viên')
        except User.DoesNotExist:
            return Response({'error': 'Nhân viên không tồn tại'}, status=404)

        if 'username' in request.data:
            if User.objects.filter(ten_dang_nhap=request.data['username']).exclude(ma_nd=id).exists():
                return Response({'error': 'Username đã tồn tại'}, status=400)
            user.ten_dang_nhap = request.data['username']

        if 'password' in request.data:
            user.mat_khau = request.data['password']

        user.save()

        nv, _ = NhanVien.objects.get_or_create(ma_nd=user)
        for field in ['ho_ten', 'sdt', 'dia_chi']:
            if field in request.data:
                setattr(nv, field, request.data[field])
        nv.save()

        return Response({'message': 'Cập nhật nhân viên thành công'})
    def delete(self, request, id=None):
        if not id:
            return Response({'error': 'Thiếu ID'}, status=400)

        try:
            user = User.objects.get(ma_nd=id, vai_tro='Nhân viên')
            NhanVien.objects.filter(ma_nd=user).delete()
            user.delete()
            return Response({'message': 'Xóa nhân viên thành công'})
        except User.DoesNotExist:
            return Response({'error': 'Nhân viên không tồn tại'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class AdminReportAPIView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response({
            'total_users': User.objects.count(),
            'total_staff': User.objects.filter(vai_tro='Nhân viên').count(),
            'total_customers': User.objects.filter(vai_tro='Khách hàng').count(),
            'total_orders': DonHang.objects.count(),
        })
