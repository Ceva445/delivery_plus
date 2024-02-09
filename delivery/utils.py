import random
from datetime import datetime
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from deliveryplus import settings
from datetime import date


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

    request_body = {
        'values': [row_data]
    }

    # Call the Sheets API to append the data
    request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range='A1', valueInputOption='RAW', body=request_body)
    response = request.execute()

    print('Row appended successfully.')



def get_unique_identifier():
    now = datetime.now()
    unique_identifier = now.strftime("%Y%m%d") + str(random.randrange(1000,9999))
    return int(unique_identifier)


def gen_comment(request):
    index = 0
    reasones = request.POST.get('reasones')
    ean_qty_str = ""
    while request.POST.get(f"qty_{index}"):
        qty = request.POST.get(f"qty_{index}")
        ean = request.POST.get(f"ean_{index}", "")
        ean_qty_str += f"{ean} {qty} szt. "
        index += 1
    comment = f"{reasones}: {ean_qty_str}"
    return comment


if __name__ == "main":
    pass