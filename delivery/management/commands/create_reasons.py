from django.core.management.base import BaseCommand
from delivery.models import ReasoneComment
import xlrd


class Command(BaseCommand):
    help = "Auto create Reasone code"

    def handle(self, *args, **options):
        workbook = xlrd.open_workbook("reasons.xls")
        sheet = workbook.sheet_by_index(0)

        supp_inst = [
            ReasoneComment(name=sheet.row_values(row)[0]) for row in range(sheet.nrows)
        ]
        ReasoneComment.objects.bulk_create(supp_inst)

        self.stdout.write("Reasons create successful")
