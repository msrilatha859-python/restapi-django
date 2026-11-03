from django_urls import path
from .views import create_order

urlpatterns = [
    path('', create_order),
]