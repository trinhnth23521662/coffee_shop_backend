from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from decimal import Decimal

from accounts.permissions import IsStaff, IsAdmin
from .models import LoaiSP, SanPham


# ================= LOAI SAN PHAM =================
@method_decorator(csrf_exempt, name='dispatch')
class CategoryListAPIView(APIView):
    permission_classes = [IsAdmin | IsStaff]

    def get(self, request):
        try:
            categories = LoaiSP.objects.all()
            data = [{
                "ma_loaisp": category.ma_loaisp,
                "ten_loaisp": category.ten_loaisp
            } for category in categories]

            return Response({
                'status': 'success',
                'data': data,
                'total': len(data)
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def post(self, request):
        try:
            ten_loaisp = request.data.get("ten_loaisp")
            if not ten_loaisp:
                return Response(
                    {"error": "Thiếu tên loại sản phẩm"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Kiểm tra tên loại đã tồn tại chưa
            if LoaiSP.objects.filter(ten_loaisp=ten_loaisp).exists():
                return Response(
                    {"error": "Tên loại sản phẩm đã tồn tại"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            category = LoaiSP.objects.create(ten_loaisp=ten_loaisp)
            return Response(
                {
                    "status": "success",
                    "message": "Tạo loại sản phẩm thành công",
                    "data": {
                        "ma_loaisp": category.ma_loaisp,
                        "ten_loaisp": category.ten_loaisp
                    }
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CategoryDetailAPIView(APIView):
    permission_classes = [IsAdmin | IsStaff]

    def get(self, request, ma_loaisp):
        try:
            category = LoaiSP.objects.get(ma_loaisp=ma_loaisp)

            # Đếm số sản phẩm thuộc loại này
            product_count = SanPham.objects.filter(ma_loaisp=category).count()

            return Response({
                'status': 'success',
                'data': {
                    "ma_loaisp": category.ma_loaisp,
                    "ten_loaisp": category.ten_loaisp,
                    "so_san_pham": product_count
                }
            })
        except LoaiSP.DoesNotExist:
            return Response(
                {"error": "Không tìm thấy loại sản phẩm"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def put(self, request, ma_loaisp):
        try:
            category = LoaiSP.objects.get(ma_loaisp=ma_loaisp)
        except LoaiSP.DoesNotExist:
            return Response(
                {"error": "Không tìm thấy loại sản phẩm"},
                status=status.HTTP_404_NOT_FOUND
            )

        ten_loaisp = request.data.get("ten_loaisp")
        if ten_loaisp:
            # Kiểm tra tên loại đã tồn tại chưa (trừ loại hiện tại)
            if LoaiSP.objects.filter(ten_loaisp=ten_loaisp).exclude(ma_loaisp=ma_loaisp).exists():
                return Response(
                    {"error": "Tên loại sản phẩm đã tồn tại"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            category.ten_loaisp = ten_loaisp

        category.save()

        return Response({
            "status": "success",
            "message": "Cập nhật loại sản phẩm thành công",
            "data": {
                "ma_loaisp": category.ma_loaisp,
                "ten_loaisp": category.ten_loaisp
            }
        })

    def delete(self, request, ma_loaisp):
        try:
            category = LoaiSP.objects.get(ma_loaisp=ma_loaisp)

            # Kiểm tra xem loại có sản phẩm không
            product_count = SanPham.objects.filter(ma_loaisp=category).count()
            if product_count > 0:
                return Response({
                    "error": f"Không thể xóa loại sản phẩm. Có {product_count} sản phẩm thuộc loại này."
                }, status=400)

            category.delete()

            return Response({
                "status": "success",
                "message": "Xóa loại sản phẩm thành công",
                "data": {
                    "ma_loaisp": category.ma_loaisp,
                    "ten_loaisp": category.ten_loaisp
                }
            })
        except LoaiSP.DoesNotExist:
            return Response(
                {"error": "Không tìm thấy loại sản phẩm"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({'error': str(e)}, status=500)


# ================= SAN PHAM =================
@method_decorator(csrf_exempt, name='dispatch')
class ProductListAPIView(APIView):
    permission_classes = [IsAdmin | IsStaff]

    def get(self, request):
        try:
            # Lấy tham số filter từ query string
            ma_loaisp = request.GET.get('ma_loaisp')
            trang_thai = request.GET.get('trang_thai')

            products = SanPham.objects.select_related("ma_loaisp").all()

            # Áp dụng filter
            if ma_loaisp:
                products = products.filter(ma_loaisp_id=ma_loaisp)
            if trang_thai:
                products = products.filter(trang_thai=trang_thai)

            data = [{
                "ma_sp": product.ma_sp,
                "ten_sp": product.ten_sp,
                "gia": float(product.gia),
                "trang_thai": product.trang_thai,
                "loai": {
                    "ma_loaisp": product.ma_loaisp.ma_loaisp,
                    "ten_loaisp": product.ma_loaisp.ten_loaisp
                }
            } for product in products]

            return Response({
                'status': 'success',
                'data': data,
                'total': len(data),
                'filters': {
                    'ma_loaisp': ma_loaisp,
                    'trang_thai': trang_thai
                }
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def post(self, request):
        try:
            ten_sp = request.data.get("ten_sp")
            gia = request.data.get("gia")
            ma_loaisp = request.data.get("ma_loaisp")
            trang_thai = request.data.get("trang_thai", "Còn")

            # Validate dữ liệu
            if not ten_sp:
                return Response({"error": "Thiếu tên sản phẩm"}, status=400)
            if not gia or float(gia) <= 0:
                return Response({"error": "Giá sản phẩm không hợp lệ"}, status=400)
            if not ma_loaisp:
                return Response({"error": "Thiếu loại sản phẩm"}, status=400)

            # Kiểm tra loại sản phẩm tồn tại
            try:
                category = LoaiSP.objects.get(ma_loaisp=ma_loaisp)
            except LoaiSP.DoesNotExist:
                return Response({"error": "Loại sản phẩm không tồn tại"}, status=404)

            # Kiểm tra tên sản phẩm đã tồn tại chưa
            if SanPham.objects.filter(ten_sp=ten_sp).exists():
                return Response({"error": "Tên sản phẩm đã tồn tại"}, status=400)

            product = SanPham.objects.create(
                ten_sp=ten_sp,
                gia=Decimal(str(gia)),
                ma_loaisp=category,
                trang_thai=trang_thai
            )

            return Response(
                {
                    "status": "success",
                    "message": "Tạo sản phẩm thành công",
                    "data": {
                        "ma_sp": product.ma_sp,
                        "ten_sp": product.ten_sp,
                        "gia": float(product.gia),
                        "trang_thai": product.trang_thai,
                        "loai": {
                            "ma_loaisp": category.ma_loaisp,
                            "ten_loaisp": category.ten_loaisp
                        }
                    }
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ProductDetailAPIView(APIView):
    permission_classes = [IsAdmin | IsStaff]

    def get(self, request, ma_sp):
        try:
            product = SanPham.objects.select_related("ma_loaisp").get(ma_sp=ma_sp)

            return Response({
                "status": "success",
                "data": {
                    "ma_sp": product.ma_sp,
                    "ten_sp": product.ten_sp,
                    "gia": float(product.gia),
                    "trang_thai": product.trang_thai,
                    "loai": {
                        "ma_loaisp": product.ma_loaisp.ma_loaisp,
                        "ten_loaisp": product.ma_loaisp.ten_loaisp
                    }
                }
            })
        except SanPham.DoesNotExist:
            return Response(
                {"error": "Không tìm thấy sản phẩm"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def put(self, request, ma_sp):
        try:
            product = SanPham.objects.get(ma_sp=ma_sp)
        except SanPham.DoesNotExist:
            return Response({"error": "Không tìm thấy sản phẩm"}, status=404)

        try:
            # Cập nhật thông tin sản phẩm
            ten_sp = request.data.get("ten_sp")
            if ten_sp is not None:
                # Kiểm tra tên sản phẩm đã tồn tại chưa (trừ sản phẩm hiện tại)
                if SanPham.objects.filter(ten_sp=ten_sp).exclude(ma_sp=ma_sp).exists():
                    return Response({"error": "Tên sản phẩm đã tồn tại"}, status=400)
                product.ten_sp = ten_sp

            gia = request.data.get("gia")
            if gia is not None:
                if float(gia) <= 0:
                    return Response({"error": "Giá sản phẩm không hợp lệ"}, status=400)
                product.gia = Decimal(str(gia))

            trang_thai = request.data.get("trang_thai")
            if trang_thai is not None:
                product.trang_thai = trang_thai

            ma_loaisp = request.data.get("ma_loaisp")
            if ma_loaisp is not None:
                try:
                    category = LoaiSP.objects.get(ma_loaisp=ma_loaisp)
                    product.ma_loaisp = category
                except LoaiSP.DoesNotExist:
                    return Response({"error": "Loại sản phẩm không tồn tại"}, status=404)

            product.save()

            return Response({
                "status": "success",
                "message": "Cập nhật sản phẩm thành công",
                "data": {
                    "ma_sp": product.ma_sp,
                    "ten_sp": product.ten_sp,
                    "gia": float(product.gia),
                    "trang_thai": product.trang_thai,
                    "loai": {
                        "ma_loaisp": product.ma_loaisp.ma_loaisp,
                        "ten_loaisp": product.ma_loaisp.ten_loaisp
                    }
                }
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def delete(self, request, ma_sp):
        try:
            product = SanPham.objects.get(ma_sp=ma_sp)

            # THỬ XÓA TRỰC TIẾP (giống như xóa LoaiSP)
            try:
                product.delete()
                return Response({
                    "status": "success",
                    "message": "Xóa sản phẩm thành công",
                    "data": {
                        "ma_sp": ma_sp,
                        "ten_sp": product.ten_sp
                    }
                })
            except Exception as delete_error:
                # Nếu lỗi khi xóa (do có ràng buộc khóa ngoại), thì đổi trạng thái
                product.trang_thai = "Hết"
                product.save()
                return Response({
                    "status": "success",
                    "message": "Sản phẩm đã được sử dụng trong đơn hàng. Đã chuyển trạng thái thành 'Hết'",
                    "data": {
                        "ma_sp": product.ma_sp,
                        "ten_sp": product.ten_sp,
                        "trang_thai": product.trang_thai
                    }
                })

        except SanPham.DoesNotExist:
            return Response({"error": "Không tìm thấy sản phẩm"}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


# ================= PUBLIC MENU =================
class PublicMenuAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:
            # Lấy tham số filter từ query string
            ma_loaisp = request.GET.get('ma_loaisp')

            products = SanPham.objects.select_related("ma_loaisp").filter(trang_thai="Còn")

            # Áp dụng filter theo loại (nếu có)
            if ma_loaisp:
                products = products.filter(ma_loaisp_id=ma_loaisp)

            # Nhóm sản phẩm theo loại
            categories = {}
            for product in products:
                category_name = product.ma_loaisp.ten_loaisp
                if category_name not in categories:
                    categories[category_name] = {
                        "ma_loaisp": product.ma_loaisp.ma_loaisp,
                        "ten_loaisp": category_name,
                        "san_pham": []
                    }

                categories[category_name]["san_pham"].append({
                    "ma_sp": product.ma_sp,
                    "ten_sp": product.ten_sp,
                    "gia": float(product.gia)
                })

            # Chuyển từ dict sang list
            menu_data = list(categories.values())

            return Response({
                "status": "success",
                "data": menu_data,
                "total_categories": len(menu_data),
                "total_products": sum(len(cat["san_pham"]) for cat in menu_data),
                "filters": {
                    "ma_loaisp": ma_loaisp
                }
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)

