from django.urls import path, include
from .views import (
    SelectReceptionView,
    DeliveryCreateView, 
    HomeView,
    )

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path("reception/", SelectReceptionView.as_view(), name="select_receprion"),
    path("reception/create/", DeliveryCreateView.as_view(), name="delivery_create"),
]
app_name = "delivery"