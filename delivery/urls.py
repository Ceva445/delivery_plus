from django.urls import path, include
from .views import (
    SelectReceptionView,
    DeliveryCreateView,
    DeliveryImageAdd,
    DeleveryDetailView, 
    HomeView, DeliveryStorageView,
    RlocationView

    )

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path("reception/", SelectReceptionView.as_view(), name="select_receprion"),
    path("reception/create/", DeliveryCreateView.as_view(), name="delivery_create"),
    path("add-image/", DeliveryImageAdd.as_view(), name="add_image"),
    path("storage/", DeliveryStorageView.as_view(), name="delivery_storage"),
    path("<int:pk>/detail/", DeleveryDetailView.as_view(), name="delivery_detail"),
    path("relocation/", RlocationView.as_view(), name="delivery_relocation"),
]
app_name = "delivery"
