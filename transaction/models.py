from django.db import models
from django.conf import settings
from delivery.models import Delivery
from user.models import User

class Transaction(models.Model):
    TRANSACTION_TYPE = (
        ("Recive", "Recive"),
        ("Relocate", "Relocate"),
        ("Optimization", "Optimization"),
        ("Shiped", "Shiped"),
        ("Utilization", "Utilization")
    )
    name = models.CharField(choices=TRANSACTION_TYPE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions"
    )
    delivery = models.ForeignKey(
        Delivery, on_delete=models.CASCADE, related_name="transactions"
    )
    transaction_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.transaction_datetime.strftime('%d-%m-%Y, %H:%M')} - {self.name} {self.delivery.identifier}"
    