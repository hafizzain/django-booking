

from django.core.management.base import BaseCommand, CommandError

from Utility.Constants.compressImage import upload_to_bucket

class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        upload_to_bucket(
            '/home/ubuntu/backend-nstyle/media/NStyle-Tenancy-74-f7a911b6/business/product_images/WhatsApp_Image_2023-06-21_at_11.15.24_AM.jpeg',
            'business/product_images/WhatsApp_Image_2023-06-21_at_11.15.24_AM.jpeg'
        )
        self.stdout.write(self.style.SUCCESS(
            'Uploaded Successfully!!'
        ))
