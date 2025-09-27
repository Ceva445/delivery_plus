import os
from django.core.management.base import BaseCommand
from django.conf import settings
from google.cloud import storage
from delivery.models import ImageModel, Delivery

class Command(BaseCommand):
    help = "Find images in the bucket that are not present in the database"

    def handle(self, *args, **options):
        bucket_name = settings.GS_BUCKET_NAME
        credentials = settings.GS_CREDENTIALS

        # Initialize the GCS client
        client = storage.Client(credentials=credentials)
        bucket = client.bucket(bucket_name)

        # Get all images from the bucket
        blobs = bucket.list_blobs()
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')
        bucket_images = [blob.name for blob in blobs if blob.name.lower().endswith(image_extensions)]

        # Get all images from the database
        db_images = set(ImageModel.objects.values_list('image_data', flat=True))

        # Find images that are in the bucket but not in the database
        missing_images = [img for img in bucket_images if img not in db_images]

        # Output results
        if missing_images:
            self.stdout.write(self.style.WARNING("Images in the bucket that are not in the database:"))
            for img in missing_images:
                url = f"https://storage.googleapis.com/{bucket_name}/{img}"
                self.stdout.write(url)
            Delivery.delete_images_set(missing_images[:10])#only first 10 images will be deleted
            self.stdout.write(self.style.SUCCESS("Deleted missing images from the bucket."))
        else:
            self.stdout.write(self.style.SUCCESS("All images are present in the database."))
        self.style.SUCCESS("Done")