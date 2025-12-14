from calculator.infrastructure.api.recruitment_order_views import create_order
from django.urls import path

urlpatterns = [
    path('recruitment/orders/create/', create_order),
]
