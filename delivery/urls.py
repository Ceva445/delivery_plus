from django.urls import path, include
from .views import (
    SelectReceptionView,
    DeliveryCreateView,
    DeliveryImageAdd,
    DeleveryDetailView,
    HomeView,
    DeliveryStorageView,
    RelocationView,
    generate_damage_pdf_report,
    admin_panel,
    SupplierListView,
    SupplierUpdateView,
    SupplierCreateView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("reception/", SelectReceptionView.as_view(), name="select_receprion"),
    path("reception/create/", DeliveryCreateView.as_view(), name="delivery_create"),
    path("add-image/", DeliveryImageAdd.as_view(), name="add_image"),
    path("storage/", DeliveryStorageView.as_view(), name="delivery_storage"),
    path("<int:pk>/detail/", DeleveryDetailView.as_view(), name="delivery_detail"),
    path("relocation/", RelocationView.as_view(), name="delivery_relocation"),
    path("print-report/", generate_damage_pdf_report, name="generaport"),
    path("admin-panel/", admin_panel, name="admin_panel"),
    path("supplier-list/", SupplierListView.as_view(), name="supplier_list"),
    path("supplier-create/", SupplierCreateView.as_view(), name="supplier_create"),
    path(
        "<int:pk>/supplier-update/",
        SupplierUpdateView.as_view(),
        name="supplier_update",
    ),
]
app_name = "delivery"
