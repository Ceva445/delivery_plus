from django.urls import path, include
from .views import TodoList

urlpatterns = [
    path("unused-images/", TodoList.as_view(), name="unused_image"),
]
