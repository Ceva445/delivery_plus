from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from delivery.models import Delivery, ImageModel
from django.db.models import Count

from deliveryplus.settings import GS_BUCKET_NAME


class TodoList(APIView):
    def get(self, request):
        not_used_images = Delivery.objects\
            .filter(complite_status=True)\
                .annotate(num_images=Count('images_url'))\
                    .filter(num_images__gt=0)
        not_used_images_info = []
        for delivery in not_used_images:
            images = delivery.images_url.all()
            i = 1
            for image in images:
                not_used_images_info.append(
                    {
                        "path": "/".join(str(image.image_data).split("/")[:3]),
                        "file_name": f"{delivery.identifier}_{i}",
                        "image_url":f"https://storage.googleapis.com/{GS_BUCKET_NAME}/{image.image_data}"
                    }
                )
                i+=1
        return Response(not_used_images_info)
