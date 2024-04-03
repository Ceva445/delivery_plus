from django.urls import path, include
from .views import TodoList

urlpatterns = [
    path('todos/', TodoList.as_view()),
]