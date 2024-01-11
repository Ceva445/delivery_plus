from django.urls import path, include
from .views import (
    home, create_delivery,
    SecondRecivCreateView,
    FirstRecivCreateView
    )

urlpatterns = [
    path("", home, name="home"),
    path("create/second-reciv/", SecondRecivCreateView.as_view(), name="second_delivery_create"),
    path("create/first-reciv/",FirstRecivCreateView.as_view(), name="first_delivery_create"),
    path("create/", create_delivery, name="delivery_create")
]
app_name = "delivery"