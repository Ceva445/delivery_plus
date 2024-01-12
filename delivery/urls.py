from django.urls import path, include
from .views import (
    home, select_reception,
    SecondRecivCreateView
    )

urlpatterns = [
    path("", home, name="home"),
    path("reception/", select_reception, name="select_receprion"),
    path("reception/create/", SecondRecivCreateView.as_view(), name="delivery_create")
]
app_name = "delivery"