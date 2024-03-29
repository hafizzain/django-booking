

from django.core.management.base import BaseCommand, CommandError

import random
import string
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings

class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):

        html_file = render_to_string("otp_email.html", {
            # 'user_name': user_otp.user.username,
            'user_name': 'Huzaifa',
            'otp': '6596', 
            'email': 'huzaifa.officialmail@gmail.com'
        })
        text_content = strip_tags(html_file)
        
        email = EmailMultiAlternatives(
            'Email Verification OTP',
            text_content,
            settings.EMAIL_HOST_USER,
            to = ['huzaifa.officialmail@gmail.com',]
        )
        
        email.attach_alternative(html_file, "text/html")
        email.send()
        self.stdout.write(self.style.SUCCESS(
            'Subdomain Secured Successfully!!'
        ))
