from django.contrib import admin
from .models import Transaction

class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "format_transaction_datetime",
        "name",
        "delivery"
    )
    search_fields = ["delivery"]

    def format_transaction_datetime(self, obj):
        return obj.transaction_datetime.strftime('%d-%m-%Y, %H:%M')

admin.site.register(Transaction, TransactionAdmin)