import random
from datetime import datetime
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from deliveryplus import settings
from datetime import date
import io
from reportlab.pdfgen import canvas


# open credential file
CREDENTIALS_FILE = "cred.json"
# ID Google Sheets documents
spreadsheet_id = settings.SPREADSHEET_ID

# service — API access instance
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ],
)
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build("sheets", "v4", http=httpAuth)


def write_report_gs(data=None, sheet_name=None):
    row_data = ["Value1", "Value2", "Value3"]

    request_body = {"values": [row_data]}

    # Call the Sheets API to append the data
    request = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=spreadsheet_id,
            range="A1",
            valueInputOption="RAW",
            body=request_body,
        )
    )
    response = request.execute()

    print("Row appended successfully.")


def get_unique_identifier():
    now = datetime.now()
    unique_identifier = now.strftime("%Y%m%d") + str(random.randrange(1000, 9999))
    return int(unique_identifier)


def gen_comment(request):
    index = 0
    reasones = request.POST.get("reasones")
    ean_qty_str = ""
    while request.POST.get(f"qty_{index}"):
        qty = request.POST.get(f"qty_{index}")
        ean = request.POST.get(f"ean_{index}", "")
        ean_qty_str += f"{ean} {qty} szt. "
        index += 1
    comment = f"{reasones}: {ean_qty_str}"
    return comment


def gen_pdf_damage_repor(delivery):
    
    recive_loc = delivery.recive_location.name
    order = delivery.nr_order
    shop = delivery.shop.position_nr
    total_qty = 100 # !!! Add count to total
    supplier = delivery.supplier_company.name
    full_name = "FULL NAME"
    recive_data = "14/02/2024"
    #full_comment = comment + extra_comment
    paragraph_text = "Podczsas kontroli wykryto dekomplet: 9002754329167 34 szt. 64527543294567 64 szt. Product wyjento z palety, nosznik wycofano"
    sscc = delivery.sscc_barcode

    if recive_loc == "1R":
        path_first_page = "static/img/second_rec_first_page.jpg"
        path_second_page = "static/img/second_rec_second_page.jpg"
    else:
        path_first_page = "static/img/first_rec_first_page.jpg"
        path_second_page = "static/img/first_rec_second_page.jpg"

    buffer = io.BytesIO()
    my_canvas = canvas.Canvas(buffer)
    my_canvas.drawImage(path_first_page, -30, -100, width=652, height=960)
    my_canvas.setFont("Helvetica", 12)

    my_canvas.drawString(210, 654, f"{full_name}")
    my_canvas.drawString(435, 654, f"{recive_data}")

    my_canvas.drawString(40, 270, f"{order}")
    my_canvas.drawString(140, 270, f"LM - {shop}")
    my_canvas.drawString(210, 270, f"{total_qty} szt.")
    my_canvas.drawString(290, 270, f"{supplier}")


    my_canvas.showPage()

    my_canvas.drawImage(path_second_page, -30, -100, width=652, height=960)
    my_canvas.setFont("Helvetica", 12)

    left_margin = 30
    bottom_margin = 557

    line_spacing = 25
    number_of_lines = 5

    x_position = left_margin + 5
    y_position = bottom_margin + line_spacing


    my_canvas.drawString(x_position, 607, f"SSCC: {sscc}")
    for line in paragraph_text.split(".")[:number_of_lines]:
        my_canvas.drawString(x_position, y_position, f"{line}.")
        y_position -= line_spacing

    


    my_canvas.showPage()
    my_canvas.save()
    buffer.seek(0)
    return buffer




if __name__ == "main":
    pass

