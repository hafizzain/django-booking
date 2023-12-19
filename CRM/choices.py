from django.db import models

class CampaignChoices(models.TextChoices):
        EMAIL = 'email', 'Email'
        APPNOTIFACTION = 'App Notification', 'AppNotification'
        BOTH = 'both', 'Both'
        

class SegmentChoice(models.TextChoices):
        STATIC = 'static', 'Static'
        DYNAMIC = 'dynamic', 'Dynamic'
   