import requests
from deliveryplus.settings import CUPS_POST_URL

def send_label_to_cups(delivery, comment):
    comment = comment.replace("Podczas kontroli wykryto ", "")
    rec_data = delivery.date_recive.strftime("%Y/%m/%d")
    data_to_send = {
    "supplier_company": f"{delivery.supplier_company.name}",
    "shop": f"{delivery.shop.position_nr}",
    "user": f"{delivery.user.username}",
    "data": f"{rec_data}",
    "order": f"{delivery.nr_order}",
    "identifier": f"{delivery.identifier}",
    "comment":f"{comment}"
}
    #print(data_to_send)
    try:
        esponse = requests.post(CUPS_POST_URL, json=data_to_send)
    except TimeoutError:
        pass