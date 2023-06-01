from django.core.management.base import BaseCommand, CommandError

from Utility.Constants.add_data_db import add_business_types

class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        add_business_types()
        self.stdout.write(self.style.SUCCESS(
            'Business Types added Successfully!!'
        ))
