from django.contrib import admin
from .models import Location, Shop, Supplier, Delivery, ReasoneComment, ImageModel


class ShopAdmin(admin.ModelAdmin):
    list_display = (
        "position_nr",
        "name",
    )  # Fields to display in the admin panel
    ordering = ("position_nr",)  # Default sorting order
    list_display_links = ("position_nr", "name")


class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "supplier_wms_id")
    search_fields = ["supplier_wms_id"]


admin.site.register(Location)
admin.site.register(Shop, ShopAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Delivery)
admin.site.register(ReasoneComment)
admin.site.register(ImageModel)
