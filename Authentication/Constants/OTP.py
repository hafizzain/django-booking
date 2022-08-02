

import random, string
from Authentication.models import VerificationOTP
from twilio.rest import Client

from django.conf import  settings

def send_twillio_to_phone_number(user=None):
    if user is not None:
        try:
            otp_obj = VerificationOTP.objects.get(user=user, code_for='Mobile')
        except Exception as err:
            print(err)
            otp_obj = None

        if otp_obj is not None:
            print(otp_obj)
            text_message = f'{otp_obj.code} is your One Time Password (OTP) for verification on NStyle. Do not share this password with anyone'
            client = Client(settings.TWILLIO_ACCOUNT_SID, settings.TWILLIO_AUTH_TOKEN)
            twilio_message = client.messages.create(
                body=text_message,
                from_=settings.TWILLIO_PHONE_NUMBER,
                to=user.mobile_number
            )
            print('Sent Phone Number OTP')
        else:
            print('OTP not found')

def generate_user_mobile_otp(user=None):
    if user is None:
        return

    random_digits_for_code = ''.join(random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
    otp = VerificationOTP(
        user=user,
        code=random_digits_for_code,
        code_for='Mobile'
    )
    otp.save()
    send_twillio_to_phone_number(user=user)