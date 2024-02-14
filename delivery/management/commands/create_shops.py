from typing import Any
from django.core.management.base import BaseCommand
from delivery.models import Shop
import xlrd


class Command(BaseCommand):
    help = "Auto create Shops"

    def handle(self, *args: Any, **options):
        workbook = xlrd.open_workbook("shops.xls")
        sheet = workbook.sheet_by_index(0)

        shop_inst = [
            Shop(
                position_nr=int(sheet.row_values(row)[0].split("-")[0]),
                name="-".join(sheet.row_values(row)[0].split("-")[1:]),
            )
            for row in range(0, sheet.nrows)
        ]
        Shop.objects.bulk_create(shop_inst)

        self.stdout.write("Shops create successful")
