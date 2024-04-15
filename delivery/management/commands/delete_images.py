import json
from django.core.management.base import BaseCommand
from deliveryplus import settings
from google.cloud import storage

class Command(BaseCommand):
    def handle(self, *args, **options):
        help = "Command to create Locations"
        with open('img_to_del.json') as f:
            d = json.load(f)
        images_urls = set([img["image_url"] for img in d])
        
        for _ in images_urls:
            try:
                bucket_name = settings.GS_BUCKET_NAME
                file_path = str(_.replace("https://storage.googleapis.com/delivery_plus_bucket/",""))
                print(file_path)
                credentials = settings.GS_CREDENTIALS
                client = storage.Client(credentials=credentials)
                bucket = client.bucket(bucket_name)
                blob = bucket.blob(file_path)
                blob.delete()
                print(_," !!!!!!!!!!!!!!!!!!! DELETED")
            except:
                print(_)