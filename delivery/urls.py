from django.urls import path, include
from .views import (
    SelectReceptionView,
    DeliveryCreateView,
    DeliveryImageAdd,
    DeleveryDetailView,
    HomeView,
    DeliveryStorageView,
    RelocationView,
    UncompliteView,
    generate_damage_pdf_report,
    admin_panel,
    not_used_image_menager,
    SupplierListView,
    SupplierUpdateView,
    SupplierCreateView,
    ReportListView,
    SummaryReportOfGoodsView,
    TotalTransactionReportView,
    IrregularityOfTypeView,
    ReadyToShipReportView,
    LocationListView,
    LocationUpdateView,
    LocationCreateView,
    DeliveryFirsrRecCreateView,
    DeliverySecondRecCreateView,
    DeliveryArchivatorView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("api/", include("delivery.api.urls")),
    path("reception/", SelectReceptionView.as_view(), name="select_receprion"),
    path("reception/create/", DeliveryCreateView.as_view(), name="delivery_create"),
    path("first-rec/create/", DeliveryFirsrRecCreateView.as_view(), name="first_rec_del_create"),
    path("second-rec/create/", DeliverySecondRecCreateView.as_view(), name="second_rec_del_create"),
    path("add-image/", DeliveryImageAdd.as_view(), name="add_image"),
    path("storage/", DeliveryStorageView.as_view(), name="delivery_storage"),
    path("archivator/", DeliveryArchivatorView.as_view(), name="delivery_archivator"),
    path("<int:pk>/detail/", DeleveryDetailView.as_view(), name="delivery_detail"),
    path("relocation/", RelocationView.as_view(), name="delivery_relocation"),
    path("uncomplit/", UncompliteView.as_view(), name="delivery_uncomplit"),
    path("print-report/", generate_damage_pdf_report, name="generaport"),
    path("admin-panel/", admin_panel, name="admin_panel"),
    path("image/menager", not_used_image_menager, name="not_used_image_menager"),
    path("supplier-list/", SupplierListView.as_view(), name="supplier_list"),
    path("supplier-create/", SupplierCreateView.as_view(), name="supplier_create"),
    path(
        "<int:pk>/supplier-update/",
        SupplierUpdateView.as_view(),
        name="supplier_update",
    ),
    path("report-list", ReportListView.as_view(), name="report_list"),
    path(
        "summary-of-goods", 
        SummaryReportOfGoodsView.as_view(), 
        name="sum_of_goods"
        ),
    path(
        "type-of-irregularity",
        IrregularityOfTypeView.as_view(),
        name="type_of_irregularity"
        ),
    path(
        "total-transactin-cont",
        TotalTransactionReportView.as_view(),
        name="total_transaction",
    ),
    path(
        "ready_to_ship",
        ReadyToShipReportView.as_view(),
        name="ready_to_ship"
    ),
    path("location-list/", LocationListView.as_view(), name="location_list"),
    path("location-create/", LocationCreateView.as_view(), name="location_create"),
    path(
        "<int:pk>/location-update/",
        LocationUpdateView.as_view(),
        name="location_update"
        ),
]
app_name = "delivery"
