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
        transact_names = {
            "Utulizacja": "Utulizacja",
            "Shiped": "Shiped",
            "ANULACJA": "Anulacja"
            }

    if to_location.work_zone > delivery.location.work_zone:
        create_transaction(
            user=user, delivery=delivery, transaction_type=transact_names[to_location.name]
        )
    elif to_location.work_zone == delivery.location.work_zone:
         create_transaction(
            user=user, delivery=delivery, transaction_type="Optimization"
        )
    delivery.location = to_location
