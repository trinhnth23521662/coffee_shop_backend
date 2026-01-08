from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from decimal import Decimal

from accounts.permissions import IsStaff
from .models import LoaiSP, SanPham


# ================= LOAI SAN PHAM =================
@method_decorator(csrf_exempt, name='dispatch')
class LoaiSPAPIView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        loaisp = LoaiSP.objects.all()
        return Response([
            {
                "ma_loaisp": l.ma_loaisp,
                "ten_loaisp": l.ten_loaisp
            } for l in loaisp
        ])

    def post(self, request):
        ten_loaisp = request.data.get("ten_loaisp")
        if not ten_loaisp:
            return Response(
                {"error": "Thiếu tên loại sản phẩm"},
                status=status.HTTP_400_BAD_REQUEST
            )

        loai = LoaiSP.objects.create(ten_loaisp=ten_loaisp)
        return Response(
            {
                "message": "Tạo loại sản phẩm thành công",
                "ma_loaisp": loai.ma_loaisp
            },
            status=status.HTTP_201_CREATED
        )


@method_decorator(csrf_exempt, name='dispatch')
class LoaiSPDetailAPIView(APIView):
    permission_classes = [IsStaff]

    def put(self, request, ma_loaisp):
        try:
            loai = LoaiSP.objects.get(ma_loaisp=ma_loaisp)
        except LoaiSP.DoesNotExist:
            return Response(
                {"error": "Không tìm thấy loại"},
                status=status.HTTP_404_NOT_FOUND
            )

        loai.ten_loaisp = request.data.get("ten_loaisp", loai.ten_loaisp)
        loai.save()

        return Response({
            "message": "Cập nhật loại sản phẩm thành công",
            "data": {
                "ma_loaisp": loai.ma_loaisp,
                "ten_loaisp": loai.ten_loaisp
            }
        })

    def delete(self, request, ma_loaisp):
        try:
            loai = LoaiSP.objects.get(ma_loaisp=ma_loaisp)
            LoaiSP.objects.get(ma_loaisp=ma_loaisp).delete()
            return Response({"message": "Xóa loại sản phẩm thành công",
                             "data": {
                                 "ma_loaisp": loai.ma_loaisp,
                                 "ten_loaisp": loai.ten_loaisp
                             }
                             })
        except LoaiSP.DoesNotExist:
            return Response({"error": "Không tìm thấy loại"}, status=404)


# ================= SAN PHAM =================
@method_decorator(csrf_exempt, name='dispatch')
class SanPhamAPIView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        san_pham = SanPham.objects.select_related("ma_loaisp").all()
        return Response([
            {
                "ma_sp": sp.ma_sp,
                "ten_sp": sp.ten_sp,
                "gia": float(sp.gia),
                "trang_thai": sp.trang_thai,
                "loai": sp.ma_loaisp.ten_loaisp
            } for sp in san_pham
        ])

    def post(self, request):
        try:
            sp = SanPham.objects.create(
                ten_sp=request.data["ten_sp"],
                gia=Decimal(str(request.data["gia"])),
                ma_loaisp_id=request.data["ma_loaisp"],
                trang_thai=request.data.get("trang_thai", "Còn")
            )
            return Response(
                {
                    "message": "Tạo sản phẩm thành công",
                    "ma_sp": sp.ma_sp,
                    "ten_sp": sp.ten_sp
                },
                status=status.HTTP_201_CREATED
            )
        except Exception:
            return Response({"error": "Dữ liệu không hợp lệ"}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class SanPhamDetailAPIView(APIView):
    permission_classes = [IsStaff]

    def get(self, request, ma_sp):
        try:
            sp = SanPham.objects.select_related("ma_loaisp").get(ma_sp=ma_sp)
        except SanPham.DoesNotExist:
            return Response(
                {"error": "Không tìm thấy sản phẩm"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            "ma_sp": sp.ma_sp,
            "ten_sp": sp.ten_sp,
            "gia": float(sp.gia),
            "trang_thai": sp.trang_thai,
            "loai": {
                "ma_loaisp": sp.ma_loaisp.ma_loaisp,
                "ten_loaisp": sp.ma_loaisp.ten_loaisp
            }
        })

    def put(self, request, ma_sp):
        try:
            sp = SanPham.objects.get(ma_sp=ma_sp)
        except SanPham.DoesNotExist:
            return Response({"error": "Không tìm thấy sản phẩm"}, status=404)

        sp.ten_sp = request.data.get("ten_sp", sp.ten_sp)
        sp.gia = Decimal(str(request.data.get("gia", sp.gia)))
        sp.trang_thai = request.data.get("trang_thai", sp.trang_thai)

        if "ma_loaisp" in request.data:
            sp.ma_loaisp_id = request.data["ma_loaisp"]

        sp.save()
        return Response({"message": "Cập nhật sản phẩm thành công",
                         "ma_sp": sp.ma_sp,
                         "ten_sp": sp.ten_sp,
                         "gia": float(sp.gia),
                         "trang_thai": sp.trang_thai,
                         "loai": {
                             "ma_loaisp": sp.ma_loaisp.ma_loaisp,
                             "ten_loaisp": sp.ma_loaisp.ten_loaisp }
                         })

    def delete(self, request, ma_sp):
        try:
            sp = SanPham.objects.get(ma_sp=ma_sp)
            sp.trang_thai = "Hết"
            sp.save()
            return Response({"message": "Xóa sản phẩm (Hết hàng)"})
        except SanPham.DoesNotExist:
            return Response({"error": "Không tìm thấy sản phẩm"}, status=404)


# ================= PUBLIC MENU =================
class PublicMenuAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        san_pham = SanPham.objects.select_related("ma_loaisp").filter(trang_thai="Còn")
        return Response([
            {
                "ma_sp": sp.ma_sp,
                "ten_sp": sp.ten_sp,
                "gia": float(sp.gia),
                "loai": sp.ma_loaisp.ten_loaisp
            } for sp in san_pham
        ])
