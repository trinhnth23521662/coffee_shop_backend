from django.urls import path
from .views import (
    CategoryListAPIView,
    CategoryDetailAPIView,
    ProductListAPIView,
    ProductDetailAPIView,
    PublicMenuAPIView
)

urlpatterns = [
    # Loại sản phẩm
    path('categories/', CategoryListAPIView.as_view()),
    path('categories/<int:ma_loaisp>/', CategoryDetailAPIView.as_view()),

    # Sản phẩm (quản lý)
    path('products/', ProductListAPIView.as_view()),
    path('products/<int:ma_sp>/', ProductDetailAPIView.as_view()),

    # Menu công khai (cho khách hàng)
    path('menu/', PublicMenuAPIView.as_view()),
]
