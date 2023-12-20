import threading
from django.core.mail import send_mail
from django.conf import settings

class CampaignUtility:
    def campaign_async(self, campaign=None):
            """
            Send email for the given campaign asynchronously in a separate thread.
            """
            thread = threading.Thread(target=self.run_campaign, args=(campaign,))
            thread.start()

    def run_campaign(self, campaign=None):
            """
            Send email for the given campaign.
            """
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
            elif campaign.is_both():
                client_email_list = campaign.segment.client.all().values_list('email', flat=True)
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    client_email_list,
                    fail_silently=False,
                )