from django.core.management.base import BaseCommand
from delivery.models import Supplier
import xlrd

class Command(BaseCommand):
    help = 'Description of my custom command'

    def handle(self, *args, **options):
        workbook = xlrd.open_workbook("suppliers.xls")

        # Select the first sheet (you may need to adjust this based on your Excel file)
        sheet = workbook.sheet_by_index(0)

        # for row_index in range(sheet.nrows):
        #     row_data = sheet.row_values(row_index)
        #     print(row_data)

        supp_inst = [
            Supplier(name=sheet.row_values(row)[1], supplier_id=sheet.row_values(row)[0]) 
            for row in range(1,sheet.nrows)
        ]
        Supplier.objects.bulk_create(supp_inst)


        self.stdout.write("Suppliers create successful")