

import random, string
from Authentication.models import VerificationOTP


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
    send_new_user_otp_to_mobile_number(obj=otp)

def send_new_user_otp_to_mobile_number(obj=None):
    print('sending number.....')