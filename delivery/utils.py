import random
from datetime import datetime

def get_unique_identifier():
    now = datetime.now()
    unique_identifier = now.strftime("%Y%m%d") + str(random.randrange(100,999))
    return int(unique_identifier)


def gen_comment(request):
    return "Test"


if __name__ == "main":
    pass