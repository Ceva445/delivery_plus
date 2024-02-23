from .utils import create_transaction
from datetime import datetime


def relocate_delivery(user, delivery, to_location):
    transaction_type = "Relocate"
    delivery.transaction += f"\
        {datetime.now().strftime('%m/%d/%Y, %H:%M')} \
            Użytkownik: {user.username} przeniósł produkt z lokalizacji \
                {delivery.location.name} do lokalizacji {to_location.name}\n"
    if to_location.work_zone == 4:
        delivery.complite_status = True
        if to_location.name == "Utulizacja":
            transaction_type = "Utilization"
        else:
            to_location.name == "Shiped"
            transaction_type = "Shiped"
    if to_location.work_zone > delivery.location.work_zone:
        create_transaction(
            user=user, delivery=delivery, transaction_type=transaction_type
        )
    delivery.location = to_location
