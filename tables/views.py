from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdmin, IsStaff
from .models import Ban
from .serializers import BanSerializer


# ================= DANH SACH + TAO BAN =================
@method_decorator(csrf_exempt, name='dispatch')
class BanListCreateAPIView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        bans = Ban.objects.all()
        serializer = BanSerializer(bans, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=400)


# ================= CHI TIET BAN =================
@method_decorator(csrf_exempt, name='dispatch')
class BanDetailAPIView(APIView):
    permission_classes = [IsStaff]

    def get_object(self, ma_ban):
        try:
            return Ban.objects.get(ma_ban=ma_ban)
        except Ban.DoesNotExist:
            return None

    def get(self, request, ma_ban):
        ban = self.get_object(ma_ban)
        if not ban:
            return Response({'error': 'Bàn không tồn tại'}, status=404)
        return Response(BanSerializer(ban).data)

    def put(self, request, ma_ban):
        ban = self.get_object(ma_ban)
        if not ban:
            return Response({'error': 'Bàn không tồn tại'}, status=404)

        serializer = BanSerializer(ban, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, ma_ban):
        ban = self.get_object(ma_ban)
        if not ban:
            return Response({'error': 'Bàn không tồn tại'}, status=404)

        ban.delete()
        return Response(
            {'message': 'Xóa bàn thành công'},
            status=status.HTTP_204_NO_CONTENT
        )


# ================= DOI TRANG THAI BAN =================
@method_decorator(csrf_exempt, name='dispatch')
class BanChangeStatusAPIView(APIView):
    permission_classes = [IsStaff]

    def patch(self, request, ma_ban):
        try:
            ban = Ban.objects.get(ma_ban=ma_ban)
        except Ban.DoesNotExist:
            return Response({'error': 'Bàn không tồn tại'}, status=404)

        trang_thai = request.data.get('trang_thai')
        if not trang_thai:
            return Response(
                {'error': 'Thiếu trạng thái mới'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ban.trang_thai = trang_thai
        ban.save()

        return Response({
            'message': 'Cập nhật trạng thái bàn thành công',
            'ma_ban': ban.ma_ban,
            'ten_ban': ban.ten_ban,
            'trang_thai': ban.trang_thai
        })
