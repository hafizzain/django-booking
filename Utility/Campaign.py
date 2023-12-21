from threading import Thread
from django.core.mail import send_mail
from django.conf import settings
from Utility.models import ExceptionRecord
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
    ExceptionRecord.objects.create(text=str('calling send_campaign_email function '),
                                        status_code=str(500),
                                        method=str('send_campaign_email'),
                                        path=str('send_campaign_email')
                                    )
    thread = Thread(target=run_campaign, args=(campaign,))
    thread.start()

def run_campaign(campaign=None):
    ExceptionRecord.objects.create(text=str('calling run_campaign function '),
                                            status_code=str(500),
                                            method=str('run_campaign'),
                                            path=str('run_campaign')
                                        )
    try:
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
    except Exception as err:
        ExceptionRecord.objects.create(text=str(err),
                                            status_code=str(500),
                                            method=str('send_mail'),
                                            path=str('send_mail')
                                        )
        