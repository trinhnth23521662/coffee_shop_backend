from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_khuyenmai_list, name='api_khuyenmai_list'),
    path('create/', views.api_khuyenmai_create, name='api_khuyenmai_create'),
    path('tinh-giam-gia/', views.api_tinh_giam_gia, name='api_tinh_giam_gia'),
]
