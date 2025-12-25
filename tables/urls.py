from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_ban_list, name='api_ban_list'),
    path('create/', views.api_ban_create, name='api_ban_create'),
    path('<int:ma_ban>/update/', views.api_ban_update, name='api_ban_update'),
    path('<int:ma_ban>/status/', views.api_ban_update_status, name='api_ban_update_status'),
    path('<int:ma_ban>/delete/', views.api_ban_delete, name='api_ban_delete'),
]
