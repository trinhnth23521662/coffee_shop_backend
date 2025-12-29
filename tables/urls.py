from django.urls import path
from .views import (
    TableListAPIView,
    CreateTableAPIView,
    UpdateTableAPIView,
    DeleteTableAPIView,
    TableDetailAPIView,
    UpdateTableStatusAPIView
)

urlpatterns = [
    # Danh sách bàn
    path('', TableListAPIView.as_view()),

    # Tạo bàn
    path('create/', CreateTableAPIView.as_view()),

    # Xem chi tiết bàn
    path('<int:ma_ban>/', TableDetailAPIView.as_view()),

    # Sửa bàn
    path('<int:ma_ban>/update/', UpdateTableAPIView.as_view()),

    # Cập nhật trạng thái bàn
    path('<int:ma_ban>/status/', UpdateTableStatusAPIView.as_view()),

    # Xóa bàn
    path('<int:ma_ban>/delete/', DeleteTableAPIView.as_view()),
]
