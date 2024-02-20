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
    total_qty = 100  # !!! Add count to total
    supplier = delivery.supplier_company.name
    full_name = delivery.user.full_name
    recive_data = delivery.date_recive.strftime("%Y-%m-%d")
    # full_comment = comment + extra_comment
    comment = "Podczsas kontroli wykryto dekomplet: 9002754329167 34 szt. 64527543294567 64 szt."
    extra_commrnt = "Product wyjento z palety, nosznik wycofano"
    sscc = delivery.sscc_barcode

    if recive_loc == "1R":
        damage_protocol_path = "static/img/first_rec.jpg"
    else:
        damage_protocol_path = "static/img/second_rec.jpg"

    buffer = io.BytesIO()
    my_canvas = canvas.Canvas(buffer)
    my_canvas.drawImage(damage_protocol_path, 0, 0, width=602, height=840)
    my_canvas.setFont("Helvetica", 10)

    if recive_loc == "1R":
        my_canvas.drawString(170, 661, f"{full_name}")
        my_canvas.drawString(342, 661, f"{recive_data}")
        my_canvas.drawString(50, 505, f"{order}")
        my_canvas.drawString(140, 505, f"LM - {shop}")
        my_canvas.drawString(210, 505, f"{total_qty} szt.")
        my_canvas.drawString(320, 505, f"{supplier}")

        line_spacing = 20
        number_of_lines = 5

        x_position = 40
        y_position = 222

        my_canvas.drawString(x_position, 240, f"SSCC: {sscc}")
        for line in comment.split("szt.")[:-1]:
            my_canvas.drawString(x_position, y_position, f"{line}szt.")
            y_position -= line_spacing
        if extra_commrnt:
            my_canvas.drawString(x_position, y_position, f"{extra_commrnt}.")
    else:
        my_canvas.drawString(170, 663, f"{full_name}")
        my_canvas.drawString(342, 663, f"{recive_data}")
        my_canvas.drawString(50, 505, f"{order}")
        my_canvas.drawString(140, 505, f"LM - {shop}")
        my_canvas.drawString(210, 505, f"{total_qty} szt.")
        my_canvas.drawString(300, 505, f"{supplier[:16]}")

        line_spacing = 20
        number_of_lines = 5
        x_position = 40
        y_position = 232

        my_canvas.drawString(x_position, 250, f"SSCC: {sscc}")
        for line in comment.split("szt.")[:-1]:
            my_canvas.drawString(x_position, y_position, f"{line}szt.")
            y_position -= line_spacing
        if extra_commrnt:
            my_canvas.drawString(x_position, y_position, f"{extra_commrnt}.")

    my_canvas.showPage()
    my_canvas.save()
    buffer.seek(0)
    return buffer


if __name__ == "main":
    pass
