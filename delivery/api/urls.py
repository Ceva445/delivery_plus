from django.urls import path, include
from .views import RemoveMismachImagesFromDB, RemoveMismachImagesFromGBucket, TodoList

urlpatterns = [
    path("unused-images/", TodoList.as_view(), name="unused_image"),
    path("remove-mismach-images-from-db/", RemoveMismachImagesFromDB.as_view(), name="remove_mismach_images_from_db"),
    path("remove-mismach-images-from-gbucket/", RemoveMismachImagesFromGBucket.as_view(), name="remove_mismach_images_from_gbucket"),
]
