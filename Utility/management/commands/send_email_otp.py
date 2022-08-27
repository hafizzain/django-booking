from django.core.management.base import BaseCommand, CommandError


from Authentication.models import User
from Authentication.Constants.Email import send_otp_to_email

class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        user = User.objects.get(username='admin')
        send_otp_to_email(user=user)

        self.stdout.write(self.style.SUCCESS(
            'Sent!'
        ))
