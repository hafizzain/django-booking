from threading import Thread
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.response import Response


    
def run_campaign(message=None, subject=None, client_email_list=None, campaign_type=None):
    
    if campaign_type == "email" or campaign_type == "Both":
        for client_email in client_email_list:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [client_email], # Send email to each recipient individually
                fail_silently=False,
            )
            
    elif  campaign_type == "AppNotification" or campaign_type == "Both":
        pass
    
def send_campaign_email(new_campaign=None):
    """
    Send email for the given campaign asynchronously in a separate thread.
    """
    campaign_type = "email"
    message = new_campaign.content
    subject = new_campaign.title
    client_email_list = list(new_campaign.segment \
                                .client.all() \
                                .values_list('email', flat=True)
                            )
    if new_campaign.is_appnotifaction():
        campaign_type = "AppNotification"

    if new_campaign.is_both():
        campaign_type = "Both"
    
    thread = Thread(target=run_campaign, args=[], kwargs={'message' : message,
                                                    'subject' : subject,
                                                    'client_email_list' : client_email_list,
                                                    'campaign_type' : campaign_type})
    thread.start()
    
def send_refund_email(client_email):
    subject = 'Refund Invoice Mail'
    message = 'Your Product Refund Successfully'
    client_email = client_email
    
    def send_email_in_thread():
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [client_email],
            fail_silently=False,
        )

    # Create a thread and start it
    email_thread = Thread(target=send_email_in_thread)
    email_thread.start()



def send_reversal_email(client_phone=None,email=None, appointment_id=None, service_id=None,description=None,appointment_date=None ,service_name=None,client_name=None):
    try:
        # context =
        html_file = render_to_string("AppointmentEmail/reversal.html",
                                     {'client':client_name,'mobile':client_phone,'email':email,'appointment_date':appointment_date,'service':service_name,'reason':description})
        text_content = strip_tags(html_file)
        email = EmailMultiAlternatives(
            'Reversal',
            text_content,
            settings.EMAIL_HOST_USER,
            to=[email],
        )
        email.attach_alternative(html_file, "text/html")
        email.send()
    except Exception as ex:
        ex = str(ex)
        return Response({"msg":ex})