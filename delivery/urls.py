from django.urls import path
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
    ReportListView,
    SummaryReportOfGoodsView,
    TotalTransactionReportView,
    IrregularityOfTypeView,
    ReadyToShipView
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
        ReadyToShipView.as_view(),
        name="ready_to_ship"
    )
]
app_name = "delivery"
