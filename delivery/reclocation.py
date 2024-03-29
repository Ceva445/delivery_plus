from .utils import create_transaction
from datetime import datetime


def relocate_delivery(user, delivery, to_location):
    transact_names = {
            "Utulizacja": "Utulizacja",
            "Shiped": "Shiped",
            "ANULACJA": "Anulacja"
            }
    delivery.transaction += f"\
        {datetime.now().strftime('%m/%d/%Y, %H:%M')} \
            Użytkownik: {user.username} przeniósł produkt z lokalizacji \
                {delivery.location.name} do lokalizacji {to_location.name}\n"
    if to_location.work_zone == 4:
        delivery.complite_status = True
        

    if to_location.work_zone > delivery.location.work_zone:
        if to_location.name in transact_names:
            create_transaction(
                user=user, delivery=delivery, transaction_type= transact_names[to_location.name]
            )
        else:
            create_transaction(
                user=user, delivery=delivery, transaction_type= "Relocate"
            )
    elif to_location.work_zone == delivery.location.work_zone:
         create_transaction(
            user=user, delivery=delivery, transaction_type="Optimization"
        )
    delivery.location = to_location
