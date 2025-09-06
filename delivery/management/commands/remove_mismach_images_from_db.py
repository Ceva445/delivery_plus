from django.core.management.base import BaseCommand
from delivery.models import ImageModel

class Command(BaseCommand):
    help = "Finds all ImageModel instances that are not linked to any Delivery"

    def handle(self, *args, **options):
        # Get all images that are not linked to any Delivery
        unused_images = ImageModel.objects.filter(delivery__isnull=True)

        if not unused_images.exists():
            self.stdout.write(self.style.SUCCESS("✅ No unused images found."))
            return

        self.stdout.write(self.style.WARNING(f"🔍 Found {unused_images.count()} unused images:"))
        # Delete the unused images from the database
        unused_images.delete()
        # Call another management command to remove mismatched images from the bucket
