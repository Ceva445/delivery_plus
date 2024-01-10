from django.urls import path, include
from .views import delivery_create, DeliveryCreateView

urlpatterns = [
    path("create/", DeliveryCreateView.as_view(), name="delivery_create")
]
app_name = "delivery"