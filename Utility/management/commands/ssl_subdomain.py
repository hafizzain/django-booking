
from Authentication.Constants.Domain import create_aws_domain_record

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        create_aws_domain_record('elb5.hashedsystem.co.uk')
        self.stdout.write(self.style.SUCCESS(
            'Subdomain Secured Successfully!!'
        ))
