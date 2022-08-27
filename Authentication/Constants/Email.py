

from Authentication.models import VerificationOTP, User

from django.core.mail import send_mail
from django.conf import settings

def send_otp_to_email(user=None, ):
    if user is None:
        return

    try:
        user_otp = VerificationOTP.objects.get(user=user, code_for='Email')
    except Exception as err:
        print(err)
        return

    send_mail(
        subject='Verification OTP',
        message=f'{user_otp.code} is your new One Time Password (OTP) for verification on NStyle. Do not share this password with anyone',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user_otp.user.email],
        fail_silently=False,
    )