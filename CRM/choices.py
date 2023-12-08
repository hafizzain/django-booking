from django.db import models

class CampaignChoices(models.TextChoices):
        EMAIL = 'email', 'Email'
        APPNOTIFACTION = 'appnotifaction', 'AppNotifaction'
        BOTH = 'both', 'Both'
        

class SegmentChoice(models.TextChoices):
        STATIC = 'static', 'Static'
        DYNAMIC = 'dynamic', 'Dynamic'
   