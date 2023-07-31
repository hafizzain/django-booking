

from Authentication.models import VerificationOTP, User

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

from django.conf import settings

from Utility.models import ExceptionRecord

def send_otp_to_email(user=None, ):
    if user is None:
        return

    try:
        user_otp = VerificationOTP.objects.get(user=user, code_for='Email')
    except Exception as err:
        ExceptionRecord.objects.create(
                    text = f"VerificationOTP user for otp{user} {str(err)}"
                )
    
    user_name = f'{user_otp.user.first_name}'
    if user_otp.user.last_name:
        user_name += f' {user_otp.user.last_name}'
    html_file = render_to_string("otp_email.html", {
        # 'user_name': user_otp.user.username,
        'user_name': user_name,
        'otp': user_otp.code, 
        'email': user_otp.user.email
    })
    text_content = strip_tags(html_file)
    
    email = EmailMultiAlternatives(
        'Email Verification OTP',
        text_content,
        settings.EMAIL_HOST_USER,
        to = [user_otp.user.email,]
    )
    
    email.attach_alternative(html_file, "text/html")
    email.send()
    
    # send_mail(
    #     subject='Verification OTP',
    #     #message=f'{user_otp.code} is your new One Time Password (OTP) for verification on NStyle. Do not share this password with anyone',
    #     html_message = html_file,
    #     from_email=settings.EMAIL_HOST_USER,
    #     recipient_list=[user_otp.user.email],
    #     fail_silently=False,
        
    # )
def send_welcome_email(user=None, ):
    if user is None:
        return

    # try:
    #     user_otp = VerificationOTP.objects.get(user=user, code_for='Email')
    # except Exception as err:
    #     print(err)
    #     return

    html_file = render_to_string("welcome-email.html", {'user_name': user.username})
    text_content = strip_tags(html_file)
    
    email = EmailMultiAlternatives(
        'Welcome to NStyle',
        text_content,
        settings.EMAIL_HOST_USER,
        to = [user.email]
    )
    
    email.attach_alternative(html_file, "text/html")
    email.send()