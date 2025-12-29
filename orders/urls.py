from django.urls import path
from .views import (
    OrderListAPIView,
    CreateOrderAPIView,
    OrderDetailAPIView,
    AddItemToOrderAPIView,
    UpdateOrderItemAPIView,
    DeleteOrderItemAPIView,
    ProcessPaymentAPIView,
    CancelOrderAPIView,
    OrderHistoryAPIView
)

urlpatterns = [
    # Order list
    path('', OrderListAPIView.as_view()),

    # Create order
    path('create/', CreateOrderAPIView.as_view()),

    # Order detail
    path('<int:ma_dh>/', OrderDetailAPIView.as_view()),

    # Add item to order
    path('<int:ma_dh>/add-item/', AddItemToOrderAPIView.as_view()),

    # Process payment
    path('<int:ma_dh>/process-payment/', ProcessPaymentAPIView.as_view()),

    # Cancel order
    path('<int:ma_dh>/cancel/', CancelOrderAPIView.as_view()),

    # Update order item
    path('items/<int:ma_ctdh>/update/', UpdateOrderItemAPIView.as_view()),

    # Delete order item
    path('items/<int:ma_ctdh>/delete/', DeleteOrderItemAPIView.as_view()),

    # Order history
    path('history/', OrderHistoryAPIView.as_view()),

]
