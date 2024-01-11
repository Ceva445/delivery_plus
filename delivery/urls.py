from django.urls import path, include
from .views import DeliveryCreateView

urlpatterns = [
    path("create/", DeliveryCreateView.as_view(), name="delivery_create")
]
app_name = "delivery"