from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

from django.conf import settings


def Add_appointment(**kwargs):
    # if user is None:
    #     return

    # try:
    #     user_otp = VerificationOTP.objects.get(user=user, code_for='Email')
    # except Exception as err:
    #     print(err)
    #     return
    for key, value in kwargs.items():
        print( key, value)
        if key == 'email':
            send = value
            
    
    email_host = 'developeracount211@gmail.com'
    print(send)
    
    html_file = render_to_string("AppointmentEmail/add_appointment.html") #{'user_name': user_otp.user.username,'otp': user_otp.code, 'email':user_otp.user.email})
    text_content = strip_tags(html_file)
    
    email = EmailMultiAlternatives(
        'Email Verification OTP',
        text_content,
        settings.EMAIL_HOST_USER,
        to = [send],
       
    )
    print('***')
    email.attach_alternative(html_file, "text/html")
    email.send()