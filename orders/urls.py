from django.urls import path
from .views import TaoDonHangAPIView, ThemChiTietDonAPIView, XemDonHangAPIView, CustomerCreateOrderAPIView, AddOnlineOrderItemAPIView, ThanhToanTienMatAPIView

urlpatterns = [
    path('', TaoDonHangAPIView.as_view()),
    path('<int:ma_dh>/items/', ThemChiTietDonAPIView.as_view()),
    path('<int:ma_dh>/', XemDonHangAPIView.as_view()),
    path('orders/', CustomerCreateOrderAPIView.as_view()),
    path('orders/<int:ma_dh>/items/', AddOnlineOrderItemAPIView.as_view()),
    path('<int:ma_dh>/cash-pay/', ThanhToanTienMatAPIView.as_view()),

]