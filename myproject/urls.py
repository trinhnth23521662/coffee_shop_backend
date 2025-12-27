from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # ===== AUTH =====
    path('api/auth/', include('accounts.urls')),

    # ===== ADMIN =====
    path('api/admin/', include('admin_app.urls')),
    path('api/admin/', include('promotions.urls')),
    path('api/admin/', include('reports.urls')),

    # ===== STAFF =====
    path('api/staff/menu/', include('menu.urls')),
    path('api/staff/orders/', include('orders.urls')),
    path('api/staff/tables/', include('tables.urls')),

    # ===== PUBLIC =====
    path('api/public/menu/', include('menu.urls')),
    path('api/public/tables/', include('tables.urls')),
]
