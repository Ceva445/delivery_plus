from datetime import datetime
from .utils import write_report_gs
from django.db.models import Count
from django.db.models.functions import TruncDate


def write_total_action_count(transaction) -> None:
    # Calculate the number of transactions for each day divided by transaction types
    transactions_by_day_and_type = (
        transaction.annotate(
            transaction_date=TruncDate("transaction_datetime")
        )  # Extract date from datetime
        .values("transaction_date", "name")  # Group by date and transaction type
        .annotate(transaction_count=Count("id"))  # Count number of transactions
        .order_by("transaction_date", "name")  # Order by date and type
    )

    # Extract unique transaction names and dates
    transaction_dates = sorted(
        set(entry["transaction_date"] for entry in transactions_by_day_and_type),
        reverse=True,
    )
    transaction_names = sorted(
        set(entry["name"] for entry in transactions_by_day_and_type)
    )

    # Create a 2D array with dimensions based on unique transaction names and dates
    array = [
        [0 for _ in range(len(transaction_names) + 1)]
        for _ in range(len(transaction_dates) + 1)
    ]

    # Fill in the array with transaction counts
    for idx, date in enumerate(transaction_dates):
        array[idx + 1][0] = date.strftime("%Y-%m-%d")
        for jdx, name in enumerate(transaction_names):
            array[0][jdx + 1] = name
            for entry in transactions_by_day_and_type:
                if entry["name"] == name and entry["transaction_date"] == date:
                    array[idx + 1][jdx + 1] = entry["transaction_count"]
    array[0][0] = ""

    write_report_gs(data=array, sheet_name="Total Transaction")
    # Print the array

def convert_waiting_time(days_and_hours_since_received):
    
    days = days_and_hours_since_received.days
    hours = days_and_hours_since_received.seconds // 3600

    if days<=0 and int(hours)<=0:
        print(days_and_hours_since_received)
        return "less one hour"
    if days:
        days_str = f"{days} days"
    else:
        days_str = ""
    return f"{days_str} {hours} hours"

def write_summary_report_of_goods(deliverys):
    summary_report = []
    title_list = [
        "Identyfikator", "Data Przyjęcia", 
        "Recepcja", "Obecna lokalizacja",
        "Dostawca", "Zamówienie",
        "Powód", "Czas od dnia przyjęcia"
        ]
    summary_report.append(title_list)
    for delivery in deliverys:
        row = [
            delivery.identifier,
            datetime.strftime(delivery.date_recive, "%Y-%m-%d"),
            delivery.recive_location.name,
            delivery.location.name,
            delivery.supplier_company.name,
            delivery.nr_order,
            delivery.return_reasone_or_comment(),
            convert_waiting_time(delivery.days_since_received),
        ]
        summary_report.append(row)
    
    write_report_gs(
        data=summary_report, 
        sheet_name="raport zbiorczy towarów "
        )


def write_irregularity_of_type(deliverys):
    row = ()
    irregularity_dict = {}
    title_list = ["Data Przyjęcia", "Zamówienie", "Powód", "Dostawca", "Suma"]
    sorted_count_delivery = [title_list]
    for delivery in deliverys:
        row = (
            datetime.strftime(delivery.date_recive, "%Y-%m-%d"),
            delivery.nr_order,
            delivery.return_reasone_or_comment(),
            delivery.supplier_company.name,
            )
        if row not in irregularity_dict:
            irregularity_dict[row] = 0
        irregularity_dict[row] += 1
    #print(irregularity_dict)

    for report_row, count in irregularity_dict.items():
        sorted_count_delivery.append(list(report_row) + [count])
    
    write_report_gs(
        data=sorted_count_delivery, 
        sheet_name="rodzaj nieprawidłowości"
        )
    
def write_ready_to_ship(transactions):
    sorted_ready_to_ship = []
    title_list = [
        "Identyfikator", "Data Przyjęcia", "Data przygotowania",
        "Recepcja", "Obecna lokalizacja",
        "Dostawca", "Zamówienie",
        "Powód", "Czas od dnia przyjęcia"
        ]  
    filterd_transaction_list = []
    for action in transactions:
        delivery = action.delivery
        if delivery.identifier not in filterd_transaction_list:
            row = [
                delivery.identifier,
                datetime.strftime(delivery.date_recive, "%Y-%m-%d"),
                datetime.strftime(action.transaction_datetime, "%Y-%m-%d"),
                delivery.recive_location.name,
                delivery.location.name,
                delivery.supplier_company.name,
                delivery.nr_order,
                delivery.return_reasone_or_comment(),
                convert_waiting_time(action.days_since_received),
                action.days_since_received
            ]
            filterd_transaction_list.append(delivery.identifier)
            sorted_ready_to_ship.append(row)
    sorted_ready_to_ship = sorted(sorted_ready_to_ship, key=lambda x: x[-1], reverse=True)
    sorted_ready_to_ship = [inner_list[:-1] for inner_list in sorted_ready_to_ship]
    sorted_ready_to_ship.insert(0, title_list)
    write_report_gs(
        data=sorted_ready_to_ship,
        sheet_name="gotowy do wysyłki"
    )
    
