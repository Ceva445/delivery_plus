from django.contrib import admin
from .models import (
    Location, WorkZone, 
    Shop, Supplier, 
    Delivery, ReasoneComment,
    ImageModel
    )


class ShopAdmin(admin.ModelAdmin):
    list_display = ("position_nr", "name",)  # Fields to display in the admin panel
    ordering = ("position_nr",)  # Default sorting order
    list_display_links = ("position_nr", "name")


admin.site.register(Location)
admin.site.register(WorkZone)
admin.site.register(Shop, ShopAdmin)
admin.site.register(Supplier)
admin.site.register(Delivery)
admin.site.register(ReasoneComment)
admin.site.register(ImageModel)
