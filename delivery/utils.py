import random
from datetime import datetime

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