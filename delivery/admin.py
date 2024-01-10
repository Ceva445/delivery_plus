from django.contrib import admin
from .models import Location, WorkZone, Shop, Supplier, Delivery



admin.site.register(Location)
admin.site.register(WorkZone)
admin.site.register(Shop)
admin.site.register(Supplier)
admin.site.register(Delivery)