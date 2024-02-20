from transaction.models import Transaction

def create_transaction(user, delivery, transaction_type):
    transaction = Transaction(
        name=transaction_type,
        user=user,
        delivery=delivery
    )
    transaction.save()
