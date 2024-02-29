from delivery.models import Delivery, Location
from delivery.reclocation import relocate_delivery


def relocate_or_get_error(identifier, to_location, request, uncomplit=False):
        error_message = ""
        status = True
        auto_in_val = {"identifier": identifier, "to_location": to_location}
        try:
            to_location = Location.objects.get(name__iexact=to_location)
        except Location.DoesNotExist:
            error_message = "Nieprawidłowa lokalizacja"
            del auto_in_val["to_location"]
            status = False
        try:
            delivery = Delivery.objects.get(identifier=identifier)
        except Delivery.DoesNotExist:
            if error_message:
                error_message += "i identyfikator."
            else:
                error_message = "Nieprawidłowy identyfikator."
            del auto_in_val["identifier"]
            status = False

        if status:
            #if uncomplit action check delivery complit status if true made uncomplit
            if uncomplit:
                if not delivery.complite_status:
                    del auto_in_val["to_location"]
                    del auto_in_val["identifier"]
                    error_message = "Ta dostawa nie ma statusu complete"
                    return {"status": False, "error_message": error_message} | auto_in_val
                delivery.complite_status = False
            if delivery.complite_status:
                del auto_in_val["to_location"]
                del auto_in_val["identifier"]
                error_message = "Zamówienie ma status complete"
                return {"status": False, "error_message": error_message} | auto_in_val
            
            if to_location == delivery.location:
                del auto_in_val["to_location"]
                error_message = "Ta dostawa już jest w tej lokalizacji wybierz inną lokalizację"
                return {"status": False, "error_message": error_message} | auto_in_val
            relocate_delivery(
                user=request.user, delivery=delivery, to_location=to_location
            )
            delivery.save()
            return {"status": status}
        return {"status": status, "error_message": error_message} | auto_in_val
