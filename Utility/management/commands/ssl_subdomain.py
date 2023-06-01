
from Authentication.Constants.Domain import ssl_sub_domain

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        ssl_sub_domain('hello')
        self.stdout.write(self.style.SUCCESS(
            'Subdomain Secured Successfully!!'
        ))
