from typing import Any
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import random

class Supplier(models.Model):
    name = models.CharField(max_length=70)
    supplier_id = models.CharField(max_length = 40)

    class Meta:
        unique_together = ("name", "supplier_id")
    
    def __str__(self) -> str:
        return f"{self.name} - {self.supplier_id}"
    

class Shop(models.Model):
    name = models.CharField(max_length=140)
    position_nr = models.IntegerField(validators=[
            MinValueValidator(limit_value=1, message='Value must be greater than or equal to 1.'),
            MaxValueValidator(limit_value=140, message='Value must be less than or equal to 140.'),
        ])

    def __str__(self) -> str:
        return f"{self.position_nr} {self.name}"


class Delivery(models.Model):
    supplier_company = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    nr_order = models.IntegerField()# додати валідатор довжина 20 знаків
    ssc_barcode = models.CharField(max_length=18)# !!!! можливо 20 задежить чи сканер читає (00)
    images_url = None
    date_recive = models.DateTimeField(auto_now_add=True)
    user = None
    comment = None # додати генерацію коменту
    recive_location = None # створити модель для локалізацій
    delivery_id = None # стоворити функцію для генерації унікального коду YYYY:MM:DD:NNN
    actual_location = None
    
    def __str__(self):
        return 