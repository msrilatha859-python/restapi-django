from django.contrib import admin
from django.urls import path, include
from products.views import home

urlpatterns = [
    path('',home),
    path('admin/', admin.site.urls),
    path('api/products/', include('products.urls')),
    path('api/orders/', include('products.order_urls')),
]