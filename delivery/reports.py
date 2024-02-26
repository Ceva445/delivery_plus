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

def count_waiting_time(days_and_hours_since_received):
    
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
        "Recepcija", "Obecna lokalizacja",
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
            count_waiting_time(delivery.days_since_received),
        ]
        summary_report.append(row)
    
    write_report_gs(data=summary_report, sheet_name="raport zbiorczy towarów ")