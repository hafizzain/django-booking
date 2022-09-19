from django.core.management.base import BaseCommand, CommandError

from Utility.Constants.add_data_db import add_software_types

class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        add_software_types()
        self.stdout.write(self.style.SUCCESS(
            'Software Types added Successfully!!'
        ))
