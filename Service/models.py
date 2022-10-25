from email.policy import default
from uuid import uuid4
from django.db import models
from django.utils.timezone import now

from Authentication.models import User
from Business.models import Business, BusinessAddress
from Utility.Constants.Data.Durations import DURATION_CHOICES_DATA

class Service(models.Model):
    DURATION_CHOICES=[
        ('30_Min' , '30 Min'),
        ('60_Min' , '60 Min'),
        ('90_Min' , '90 Min'),
        ('120_Min' , '120 Min'),
        ('150_Min' , '150 Min'),
        ('180_Min' , '180 Min'),
        ('210_Min' , '210 Min'),
    ]
    CLIENT_CAN_BOOK_CHOICES = [
        ('Anytime', 'Anytime'),
        ('5_Hours_Before', '5 Hours Before'),
        ('12_Hours_Before', '12 Hours Before'),
        ('24_Hours_Before', '24 Hours Before'),
        ('36_Hours_Before', '36 Hours Before'),
    ]
    
    TIME_SLOT_INTERVAL_CHOICES = [
        ('30_Mins', '30 Mins'),
        ('60_Mins', '60 Mins'),
        ('90_Mins', '90 Mins'),
        ('120_Mins', '120 Mins'),
    ]
    
    CONTROLS_TIME_SLOT_CHOICES = [
        ('Anytime_In_The_Future', 'Anytime In The Future'),
        ('No_More_Than_1_Months_In_The_Future', 'No More Than 1 Months In The Future'),
        ('No_More_Than_2_Months_In_The_Future', 'No More Than 2 Months In The Future'),
        ('No_More_Than_3_Months_In_The_Future', 'No More Than 3 Months In The Future'),
    ]

    TREATMENT_TYPES = [
        ('Waxing' , 'Waxing'),
        ('Tanning' , 'Tanning'),
        ('Massages' , 'Massages'),
        ('Makeup' , 'Makeup'),
        ('Hair_Services' , 'Hair Services'),
        ('Nail_Treatments' , 'Nail Treatments'),
        ('Hand_&_Feet_Treatment' , 'Hand & Feet Treatment'),
        ('Facials_and_Skin_Care_Treatments' , 'Hand & Feet Treatment'),
        
    ]
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_services_or_packages')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_services_or_packages', null=True, blank=True)

    name = models.CharField(max_length=100, default='')

    service_type = models.CharField(choices=TREATMENT_TYPES, max_length=50, null=True, blank=True)
    parrent_service = models.ManyToManyField('Service', null=True, blank=True, related_name='parent_package_services')
    description = models.CharField(max_length=255, default='')
    #employee = models.ManyToManyField('Employee.Employee', related_name='employee_services_or_packages')
    location = models.ManyToManyField(BusinessAddress, null=True, blank=True, related_name='address_services_or_packages')
    #duration = models.PositiveIntegerField(default=0, null=True, blank=True)
    
    duration = models.CharField(max_length=50, null=True, blank=True, choices=DURATION_CHOICES )
    enable_team_comissions = models.BooleanField(default=True, null=True, blank=True, verbose_name='Enable Team Member Comission')
    enable_vouchers = models.BooleanField(default=False, null=True, blank=True)
    
    #New Fields added 
    controls_time_slot = models.CharField(choices=TIME_SLOT_INTERVAL_CHOICES, blank= True, null=True,  max_length=100, default='30_Mins')
    initial_deposit =models.PositiveIntegerField(default=0, blank= True, null=True,)
    client_can_book = models.CharField(choices=CLIENT_CAN_BOOK_CHOICES, blank= True, null=True, max_length=100, default='Anytime')
    slot_availible_for_online = models.CharField(choices=CONTROLS_TIME_SLOT_CHOICES, blank= True, null=True, max_length=100, default='Anytime_In_The_Future')

    price = models.PositiveIntegerField(default=0)
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)
    
    is_package = models.BooleanField(default=False, )


    def __str__(self):
        return str(self.id)