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

    # ===== BAN =====
    path('ban/', views.api_ban_list, name='api_ban_list'),
    path('ban/create/', views.api_ban_create, name='api_ban_create'),
    path('ban/<int:ma_ban>/update/', views.api_ban_update, name='api_ban_update'),
    path('ban/<int:ma_ban>/status/', views.api_ban_update_status, name='api_ban_update_status'),
    path('ban/<int:ma_ban>/delete/', views.api_ban_delete, name='api_ban_delete'),

    # ===== DON HANG (CASHIER) =====
    path('don/tao/', views.api_tao_don, name='api_tao_don'),
    path('don/them-mon/', views.api_them_mon, name='api_them_mon'),
    path('don/sua-mon/<int:ma_ctdh>/', views.api_sua_mon, name='api_sua_mon'),
    path('don/xoa-mon/<int:ma_ctdh>/', views.api_xoa_mon, name='api_xoa_mon'),
    path('don/thanh-toan/', views.api_thanh_toan, name='api_thanh_toan'),
    path('don/<int:ma_dh>/', views.api_xem_don, name='api_xem_don'),
    path('don/', views.api_danh_sach_don, name='api_danh_sach_don'),
]
