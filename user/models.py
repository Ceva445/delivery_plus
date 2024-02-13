from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    USER_ROLE_CHOICES = (
        ("admin", "Admin"),
        ("leader", "Leader"),
        ("regular", "Regular User"),
    )

    role = models.CharField(max_length=10, choices=USER_ROLE_CHOICES, default="regular")
    class Meta:
        ordering = ["username"]

    def __str__(self):
        return self.username
    
    def get_absolute_url(self): # new
        return reverse("user:user-list")