from django.urls import path
from . import views

urlpatterns = [
    # ===== LOAI SAN PHAM =====
    path('loaisp/', views.api_loaisp_list, name='api_loaisp_list'),
    path('loaisp/create/', views.api_loaisp_create, name='api_loaisp_create'),
    path('loaisp/<int:ma_loaisp>/update/', views.api_loaisp_update, name='api_loaisp_update'),
    path('loaisp/<int:ma_loaisp>/delete/', views.api_loaisp_delete, name='api_loaisp_delete'),

    # ===== SAN PHAM =====
    path('sanpham/', views.api_sanpham_list, name='api_sanpham_list'),
    path('menu/', views.api_menu, name='api_menu'),
    path('sanpham/create/', views.api_sanpham_create, name='api_sanpham_create'),
    path('sanpham/<int:ma_sp>/update/', views.api_sanpham_update, name='api_sanpham_update'),
    path('sanpham/<int:ma_sp>/delete/', views.api_sanpham_delete, name='api_sanpham_delete'),
]
