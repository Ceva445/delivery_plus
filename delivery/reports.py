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
