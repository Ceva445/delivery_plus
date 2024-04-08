import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from deliveryplus import settings
from datetime import date
import io
from reportlab.pdfgen import canvas
from transaction.models import Transaction

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


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
    request_body = {"values": data}

    clear_request = (
        service.spreadsheets()
        .values()
        .clear(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A1:Z",  # Adjust range as needed
            body={},
        )
    )
    clear_response = clear_request.execute()

    # Call the Sheets API to append the data
    request = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A1",
            valueInputOption="RAW",
            body=request_body,
        )
    )
    response = request.execute()


def create_transaction(user, delivery, transaction_type):
    transaction = Transaction(name=transaction_type, user=user, delivery=delivery)
    transaction.save()

def gen_comment(request):
    index = 0
    reasones = request.POST.get("reasones")
    rec_loc = request.POST.get("recive_location")
    if rec_loc == "second":
        ean_qty_str = ""
        while request.POST.get(f"qty_{index}"):
            qty = request.POST.get(f"qty_{index}")
            ean = request.POST.get(f"ean_{index}", "")
            ean_qty_str += f"{ean} {qty} szt. "
            index += 1
        comment = f"{reasones}: {ean_qty_str}"
    else:
        qty_unit = request.POST.get("qty_unit")
        tape_of_delivery = request.POST.get("tape_of_delivery")
        comment = f"{reasones}: {qty_unit} szt. {tape_of_delivery}"
    print(comment)
    return comment

def get_smart_split_comment(comment):
    smart_split_text = []
    line = ""
    for word in comment.split(" "):
        if len(line) + len(word) >= 100:
            smart_split_text.append(line)
            line = f"{word}"
        else:
            line += " " + word
    if line:
        smart_split_text.append(line)
    return smart_split_text

def get_total_products_count(comment):
    count = 0
    split_comment = comment.split(" ")[::-1]
    for indx, word in enumerate(split_comment):
        if "szt" in word.lower():
            try:
                count += int(split_comment[indx + 1])
            except:
                pass
    return count


def gen_pdf_damage_repor(delivery):
    recive_loc = delivery.recive_location.name
    order = delivery.nr_order
    shop = delivery.shop
    supplier = delivery.supplier_company.name
    full_name = delivery.user.full_name
    recive_data = delivery.date_recive.strftime("%Y-%m-%d")
    # full_comment = comment + extra_comment
    comment = delivery.comment
    total_qty = get_total_products_count(comment)
    extra_commrnt = delivery.extra_comment
    sscc = delivery.sscc_barcode

    if shop is not None:
        shop = shop.position_nr
    else:
        shop = ""

    if recive_loc == "1R":
        damage_protocol_path = "static/img/first_rec.jpg"
    else:
        damage_protocol_path = "static/img/second_rec.jpg"

    buffer = io.BytesIO()
    pdfmetrics.registerFont(TTFont("FreeSans", "freesans/FreeSans.ttf"))
    my_canvas = canvas.Canvas(buffer)
    my_canvas.drawImage(damage_protocol_path, 0, 0, width=602, height=840)
    my_canvas.setFont("FreeSans", 10)

    if recive_loc == "1R":
        my_canvas.drawString(170, 674, f"{full_name}")
        my_canvas.drawString(342, 674, f"{recive_data}")
        my_canvas.drawString(50, 517, f"{order}")
        if shop:
            my_canvas.drawString(140, 517, f"LM - {shop}")
        my_canvas.drawString(210, 517, f"{total_qty} szt.")
        my_canvas.drawString(320, 517, f"{supplier}")
        my_canvas.drawString(320, 440, f"{'Paczka' if 'pacz' in comment else 'Paleta'}")

        line_spacing = 20

        x_position = 40
        y_position = 237

        my_canvas.drawString(x_position, 255, f"SSCC/Supplier: {sscc}")
        for line in get_smart_split_comment(comment=comment.replace("pacz.", "").replace("pall.", "")):
            my_canvas.drawString(x_position, y_position, f"{line}")
            y_position -= line_spacing
        if extra_commrnt:
            my_canvas.drawString(x_position, y_position, f"{extra_commrnt}.")
    else:
        my_canvas.drawString(170, 676, f"{full_name}")
        my_canvas.drawString(342, 676, f"{recive_data}")
        my_canvas.drawString(50, 517, f"{order}")
        my_canvas.drawString(140, 517, f"LM - {shop}")
        my_canvas.drawString(210, 517, f"{total_qty} szt.")
        my_canvas.drawString(300, 517, f"{supplier[:16]}")

        line_spacing = 20
        x_position = 40
        y_position = 242

        my_canvas.drawString(x_position, 260, f"SSCC: {sscc}")
        for line in get_smart_split_comment(comment=comment):
            my_canvas.drawString(x_position, y_position, f"{line}")
            y_position -= line_spacing
        if extra_commrnt:
            my_canvas.drawString(x_position, y_position, f"{extra_commrnt}.")

    my_canvas.showPage()
    my_canvas.save()
    buffer.seek(0)
    return buffer


if __name__ == "main":
    pass
