from django.urls import path
from .views import PromotionAPIView, PromotionDetailAPIView

urlpatterns = [
    # API cho chức năng: Xem danh sách và Tạo khuyến mãi
    path('promotions/', PromotionAPIView.as_view(), name='promotion-list-create'),

    # API cho chức năng: Xem chi tiết, Sửa, Xóa khuyến mãi
    path('promotions/<int:ma_km>/', PromotionDetailAPIView.as_view(), name='promotion-detail'),
]
