from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from delivery.models import Delivery, ImageModel
from django.db.models import Count

from deliveryplus.settings import GS_BUCKET_NAME


class TodoList(APIView):
    def get(self, request):
        complited_delivery = Delivery.objects\
            .filter(complite_status=True)\
                .annotate(num_images=Count('images_url'))\
                    .filter(num_images__gt=0)
        not_used_images_info = []
        for delivery in complited_delivery:
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
            complited_delivery.update(download_images_status=True)
        return Response(not_used_images_info)
    
    def post(self, request):
        delivery_with_stored_images = Delivery.objects\
            .filter(complite_status=True).filter(download_images_status=True)\
                .annotate(num_images=Count('images_url'))\
                    .filter(num_images__gt=0)
        images_list = []
        
        for delivery in delivery_with_stored_images:
            for image in  delivery.images_url.all():
                images_list.append(image.image_data)
            delivery.images_url.all().delete()
        print(images_list)
        images_list = list(set(images_list))
        Delivery.delete_images_set(images_list)


        return Response({"ok":"ok"})
