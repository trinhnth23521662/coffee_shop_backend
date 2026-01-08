from django.urls import path
from .views import (
    LoaiSPAPIView,
    LoaiSPDetailAPIView,
    SanPhamAPIView,
    SanPhamDetailAPIView,
    PublicMenuAPIView
)

urlpatterns = [
    path('loaisp/', LoaiSPAPIView.as_view()),
    path('loaisp/<int:ma_loaisp>/', LoaiSPDetailAPIView.as_view()),

    path('sanpham/', SanPhamAPIView.as_view()),
    path('sanpham/<int:ma_sp>/', SanPhamDetailAPIView.as_view()),

    path('', PublicMenuAPIView.as_view()),
]
