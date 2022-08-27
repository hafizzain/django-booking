

from Authentication.models import VerificationOTP




def send_otp_to_email(user=None, ):
    if user is None:
        return

    try:
        user_otp = VerificationOTP.objects.get(user=user, code_for='Email')
    except Exception as err:
        print(err)
        return

