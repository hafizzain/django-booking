from threading import Thread
from django.core.mail import send_mail
from django.conf import settings
from Utility.models import ExceptionRecord
import json
    
    
def run_campaign(message=None, subject=None, client_email_list=None, campaign_type=None):
    
    if campaign_type == "email" or campaign_type == "Both": 
        send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                client_email_list,
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
    
    th = Thread(target=run_campaign, args=[], kwargs={'message' : message,
                                                      'subject' : subject,
                                                      'client_email_list' : client_email_list,
                                                      'campaign_type' : campaign_type})
    th.start()
    
