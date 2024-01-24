import threading
from threading import Thread
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.response import Response


def send_reversal_emails(client_phone=None,email=None, appointment_id=None, service_id=None,description=None,appointment_date=None ,service_name=None,client_name=None, url=None):

    try:
        phone = client_phone
        client_email = email
        appointment = appointment_id
        service = service_id
        desc = description
        date = appointment_date
        name = client_name
        s_name = service_name
        url=url
        
        # context =
        html_file = render_to_string("AppointmentEmail/reversal.html",
                                    {'url':url,'client':name,'mobile':phone,'email':client_email,'appointment_date':date,'service':s_name,'reason':desc})
        text_content = strip_tags(html_file)
        def send_email():
            email = EmailMultiAlternatives(
                'Reversal',
                text_content,
                settings.EMAIL_HOST_USER,
                to=[client_email],
            )
            email.attach_alternative(html_file, "text/html")
            email.send()
        # return Response({"msg": "Email sent successfully"})
        email_thread = Thread(target=send_email)
        email_thread.start()

    except Exception as ex:
        ex = str(ex)
        return Response({"msg":ex})