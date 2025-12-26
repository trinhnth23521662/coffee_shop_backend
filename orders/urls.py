from django.urls import path
from . import views

urlpatterns = [
    # ===== DON HANG (CASHIER) =====
    path('tao/', views.api_tao_don, name='api_tao_don'),
    path('them-mon/', views.api_them_mon, name='api_them_mon'),
    path('sua-mon/<int:ma_ctdh>/', views.api_sua_mon, name='api_sua_mon'),
    path('xoa-mon/<int:ma_ctdh>/', views.api_xoa_mon, name='api_xoa_mon'),
    path('thanh-toan/', views.api_thanh_toan, name='api_thanh_toan'),
    path('<int:ma_dh>/', views.api_xem_don, name='api_xem_don'),
    path('', views.api_danh_sach_don, name='api_danh_sach_don'),
    path("tao_don_online/", views.api_tao_don_online),
    path("them_mon_online/", views.api_them_chi_tiet_online),
    path("xem_don_online/", views.api_xem_don_online),
    path("lich_su_don/", views.api_lich_su_don_online),
]
