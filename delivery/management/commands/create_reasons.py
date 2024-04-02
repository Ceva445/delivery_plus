from django.core.management.base import BaseCommand
from delivery.models import ReasoneComment
import xlrd


class Command(BaseCommand):
    help = "Auto create Reason code"

    def handle(self, *args, **options):
        workbook = xlrd.open_workbook("reasons.xls")
        sheet = workbook.sheet_by_index(0)
        existing_reasons = set(ReasoneComment.objects.values_list("name", flat=True))

        new_reasons = [
            ReasoneComment(name=sheet.row_values(row)[0])
            for row in range(sheet.nrows)
            if sheet.row_values(row)[0] not in existing_reasons
        ]
        ReasoneComment.objects.bulk_create(new_reasons)

        self.stdout.write("Reasons created successfully")
