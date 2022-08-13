from django.core.management.base import BaseCommand
from Utility.Constants.add_data_db import add_languages

class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        add_languages(tenant=None)
        self.stdout.write(self.style.SUCCESS(
            'Languages Added Successfully !!'
        ))
