from threading import Thread
from django.core.mail import send_mail
from django.conf import settings

class CampaignUtility:

    @staticmethod
    def run_campaign(campaign=None):
        message = campaign.content
        subject = campaign.title
            
        if campaign.is_email():
            client_email_list = campaign.segment.client.all().values_list('email', flat=True)
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                client_email_list,
                fail_silently=False,
            )
        elif campaign.is_appnotifaction():
            pass
    
   
    def campaign_async(campaign=None):
        """
        Send email for the given campaign asynchronously in a separate thread.
        """
        thread = Thread(target=CampaignUtility.run_campaign, args=(campaign,))
        thread.start()
        
def send_campaign_email(campaign=None):
        """
        Send email for the given campaign asynchronously in a separate thread.
        """
        thread = Thread(target=run_campaign, args=(campaign,))
        thread.start()

def run_campaign(campaign=None):
        message = campaign.content
        subject = campaign.title
            
        if campaign.is_email():
            client_email_list = list(campaign.segment.client.all().values_list('email', flat=True))
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                client_email_list,
                fail_silently=False,
            )
        elif campaign.is_appnotifaction():
            pass