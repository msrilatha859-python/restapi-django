from django.urls import path
from .views import create_order, simulate_payment

urlpatterns = [
    path('', create_order),
    path('<int:order_id>/simulate-payment/', simulate_payment),
]
