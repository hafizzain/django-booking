import datetime
from django.db import models
from uuid import uuid4
from Authentication.models import User
from Business.models import Business
from django.utils.timezone import now
from Client.models import Client
from Utility.models import CommonField
from .choices import *



class Segment(CommonField):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='segment')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_segment')
    client = models.ManyToManyField(Client, related_name='segment_clients')
    name = models.CharField(max_length=300, unique=True)
    segemnt_type =  models.CharField(choices=SegmentChoice.choices, max_length=30)
    description =  models.CharField(max_length=300, null=True, blank=True)
    
    # Add the default manager
    objects = models.Manager()
    
    def __str__(self):
        return str(self.name)
    
    def is_static(self):
        return self.segemnt_type == SegmentChoice.STATIC
    
    def is_dynamic(self):
        return self.segemnt_type == SegmentChoice.DYNAMIC
    
class Campaign(CommonField):
    title = models.CharField(max_length=300, unique=True)
    content = models.TextField(default='')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    compingn_type = models.CharField(choices = CampaignChoices.choices, max_length=20)
    segment = models.ForeignKey(Segment, on_delete = models.CASCADE)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    
    REQUIRED_FIELDS = ['start_date', 'end_date']
    
    # Add the default manager
    objects = models.Manager()
    
    def __str__(self):
        return str(self.title)
    
    def is_email(self):
        return self.compingn_type == CampaignChoices.EMAIL
    
    def is_appnotifaction(self):
        return self.compingn_type == CampaignChoices.APPNOTIFACTION
    
    def is_both(self):
        return self.compingn_type == CampaignChoices.BOTH
    
    def is_start_date(self):
        return self.start_date >= datetime.now().date()
    
    def end_date(self):
        return self.end_date <= datetime.now().date()