from django.urls import path, include
from .views import (
    home, select_reception,
    DeliveryCreateView
    )

urlpatterns = [
    path("", home, name="home"),
    path("reception/", select_reception, name="select_receprion"),
    path("reception/create/", DeliveryCreateView.as_view(), name="delivery_create")
]
app_name = "delivery"