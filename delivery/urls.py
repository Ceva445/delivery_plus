from django.urls import path, include
from .views import (
    SelectReceptionView,
    DeliveryCreateView, 
    HomeView, DeliveryStorageView
    )

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path("reception/", SelectReceptionView.as_view(), name="select_receprion"),
    path("reception/create/", DeliveryCreateView.as_view(), name="delivery_create"),
    path("storage/", DeliveryStorageView.as_view(), name="delivery_storage"),
]
app_name = "delivery"