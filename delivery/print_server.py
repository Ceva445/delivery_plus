import requests
from deliveryplus.settings import CUPS_POST_URL


def send_label_to_cups(delivery, comment, reprint_status=False):
    cups_url = CUPS_POST_URL
    if reprint_status:
        cups_url +="reprint/"
    if comment:
        if "Podczas kontroli wykryto " in comment:
            comment = comment.replace("Podczas kontroli wykryto ", "")
    else:
        comment = ""
    rec_data = delivery.date_recive.strftime("%Y/%m/%d")
    data_to_send = {
        "supplier_company": f"{delivery.supplier_company.name}",
        "shop": f"{delivery.shop.position_nr if delivery.shop is not None else 'Brak'}",
        "user": f"{delivery.user.username}",
        "data": f"{rec_data}",
        "order": f"{delivery.nr_order}",
        "identifier": f"{delivery.identifier}",
        "comment": f"{comment[:39]}",
        "print_status": True
    }
    #print(data_to_send)
    try:
        requests.post(cups_url, json=data_to_send)
    except TimeoutError:
        pass
