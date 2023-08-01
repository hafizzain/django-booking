

import random, string
from Authentication.models import VerificationOTP
from twilio.rest import Client
from .Email import send_otp_to_email
from django.conf import  settings

from Utility.models import ExceptionRecord

def send_twillio_to_phone_number(user=None):
    if user is not None:
        try:
            otp_obj = VerificationOTP.objects.get(user=user, code_for='Mobile')
        except Exception as err:
            print(err)
            otp_obj = None

        if otp_obj is not None:
            text_message = f'{otp_obj.code} is your new One Time Password (OTP) for verification on NStyle. Do not share this password with anyone'
            client = Client(settings.TWILLIO_ACCOUNT_SID, settings.TWILLIO_AUTH_TOKEN)
            twilio_message = client.messages.create(
                body=text_message,
                from_=settings.TWILLIO_PHONE_NUMBER,
                to=user.mobile_number
            )
            print('Sent Phone Number OTP')
        else:
            print('OTP not found')

def generate_user_otp(user=None, code_for='Mobile'):
    if user is None:
        return

    random_digits_for_code = ''.join(random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
    try:
        get_otp = VerificationOTP.objects.get(
            user=user,
            code_for=code_for
        )
        get_otp.delete()
    except:
        pass

    otp = VerificationOTP(
        user=user,
        code=random_digits_for_code,
        code_for=code_for
    )
    otp.save()
    try:
        # send_twillio_to_phone_number(user=user)
        send_otp_to_email(user=user)
    except Exception as err:
        ExceptionRecord.objects.create(text = f'OTP :: {str(err)}')