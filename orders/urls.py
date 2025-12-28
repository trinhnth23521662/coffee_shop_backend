from django.urls import path
from .views import TaoDonHangAPIView, ThemChiTietDonAPIView, XemDonHangAPIView

urlpatterns = [
    path('', TaoDonHangAPIView.as_view()),
    path('<int:ma_dh>/items/', ThemChiTietDonAPIView.as_view()),
    path('<int:ma_dh>/', XemDonHangAPIView.as_view()),
]