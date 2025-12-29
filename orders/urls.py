# orders/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.OrderListAPIView.as_view(), name='order-list'),
    path('create/', views.CreateOrderAPIView.as_view(), name='create-order'),
    path('<int:ma_dh>/', views.OrderDetailAPIView.as_view(), name='order-detail'),
    path('add-item/', views.AddItemToOrderAPIView.as_view(), name='add-order-item'),
    path('update-item/<int:ma_ctdh>/', views.UpdateOrderItemAPIView.as_view(), name='update-order-item'),
    path('delete-item/<int:ma_ctdh>/', views.DeleteOrderItemAPIView.as_view(), name='delete-order-item'),
    path('payment/', views.ProcessPaymentAPIView.as_view(), name='process-payment'),

    # Online orders
    path('online-orders/create/', views.CreateOnlineOrderAPIView.as_view(), name='create-online-order'),
    path('online-orders/add-item/', views.AddOnlineOrderItemAPIView.as_view(), name='add-online-item'),
    path('online-orders/view/', views.ViewOnlineOrderAPIView.as_view(), name='view-online-order'),
    path('online-orders/history/', views.OnlineOrderHistoryAPIView.as_view(), name='online-order-history'),
]
