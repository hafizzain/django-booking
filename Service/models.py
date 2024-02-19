from uuid import uuid4
from datetime import datetime, timedelta
from django.db import models
from django.utils.timezone import now
from django.db.models.functions import Coalesce
from django.db.models import Count, IntegerField, Q, Sum, F, ExpressionWrapper

from Authentication.models import User
from Business.models import Business, BusinessAddress
from Utility.Constants.Data.Durations import DURATION_CHOICES_DATA
from Utility.models import Currency
from googletrans import Translator
from Utility.models import Language
from Appointment import choices

class ServiceManager(models.QuerySet):

    def with_total_orders(self):
        return self.annotate(
            total_orders = Coalesce(
                Count('service_orders'),
                0,
                output_field=IntegerField()
            )
        )

    def with_total_appointment_count(self, location=None, duration=None):
        """
        This function returns the Count of appointments (AppointmentService)
        related to a particular service

        Parameters:
        - location (BusinessAddress)
        - duration (int)
        """
        query = Q(serivce_appointments__status=choices.AppointmentServiceStatus.FINISHED)
        if location:
            query &= Q(serivce_appointments__business_address=location)
        if duration:
            today = datetime.today()
            date = today - timedelta(days=duration)
            query &= Q(serivce_appointments__created_at__gte=date)


        return self.annotate(
            appointment_count=Coalesce(
                Count('serivce_appointments', filter=query, distinct=True),
                0,
                output_field=IntegerField()
            )
        )

    def with_total_orders_quantity(self, location=None, duration=None):
        """
        This function returns the sum of sales quantity (ServiceOrder)
        related to a particular service

        Parameters:
        - location (BusinessAddress)
        - duration (int)
        """
        query = Q()
        if location:
            query &= Q(service_orders__location=location)
        if duration:
            today = datetime.today()
            date = today - timedelta(days=duration)
            query &= Q(service_orders__created_at__gte=date)

        return self.annotate(
            total_orders_quantity = Coalesce(
                Sum('service_orders__quantity', filter=query, distinct=True),
                0,
                output_field=IntegerField()
            )
        )

    def with_total_sale_count(self, location=None, duration=None):
        """
        This function returns the sum of appointments count (AppointmentService) and 
        sales quantity (ServiceOrder) related to a particular service

        Parameters:
        - location (BusinessAddress)
        - duration (int)
        """
        service_orders_filter = Q()
        appointment_service_filter = Q(serivce_appointments__status=choices.AppointmentServiceStatus.FINISHED)
        if location:
            service_orders_filter &= Q(service_orders__location=location)
            appointment_service_filter &= Q(serivce_appointments__business_address=location)
        if duration:
            today = datetime.today()
            date = today - timedelta(days=duration)
            service_orders_filter &= Q(service_orders__created_at__gte=date)
            appointment_service_filter &= Q(serivce_appointments__created_at__gte=date)


        return self.annotate(
            appointment_count=Coalesce(
                Count('serivce_appointments', filter=appointment_service_filter, distinct=True),
                0,
                output_field=IntegerField()
            ),
            total_orders_quantity = Coalesce(
                Sum('service_orders__quantity', filter=service_orders_filter, distinct=True),
                0,
                output_field=IntegerField()
            )
        ).annotate(
            total_count=ExpressionWrapper(F('appointment_count') + F('total_orders_quantity'),
                                        output_field=IntegerField())
        )

class Service(models.Model):
    SERVICE_CHOICE = [
        ('Everyone' , 'Everyone'),
        ('Male' , 'Male'),
        ('Female' , 'Female'),

    ]
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
    arabic_id = models.CharField(default='', max_length=999, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_services_or_packages')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_services_or_packages', null=True, blank=True)

    name = models.CharField(max_length=255, default='')
    arabic_name = models.CharField(max_length=999, default='')

    #service_type = models.CharField(choices=TREATMENT_TYPES, max_length=50, null=True, blank=True)
    service_availible = models.CharField(choices=SERVICE_CHOICE, max_length=50, default ='Everyone'  ,null=True, blank=True)
    
    #servicegroup = models.ForeignKey("ServiceGroup", on_delete=models.SET_NULL, related_name='service_servicegroup', null=True, blank=True)
    parrent_service = models.ManyToManyField('Service', null=True, blank=True, related_name='parent_package_services')
    description = models.CharField(max_length=255, default='')
    #employee = models.ManyToManyField('Employee.Employee', related_name='employee_services_or_packages')
    location = models.ManyToManyField(BusinessAddress, null=True, blank=True, related_name='address_services_or_packages')  
    
    #duration = models.CharField(max_length=50, null=True, blank=True, choices=DURATION_CHOICES )
    
    enable_team_comissions = models.BooleanField(default=True, null=True, blank=True, verbose_name='Enable Team Member Comission')
    enable_vouchers = models.BooleanField(default=False, null=True, blank=True)
    
    #New Fields added 
    controls_time_slot = models.CharField(choices=TIME_SLOT_INTERVAL_CHOICES, blank= True, null=True,  max_length=255, default='30_Mins')
    initial_deposit =models.FloatField(default=0, blank= True, null=True,)
    client_can_book = models.CharField(choices=CLIENT_CAN_BOOK_CHOICES, blank= True, null=True, max_length=255, default='Anytime')
    slot_availible_for_online = models.CharField(choices=CONTROLS_TIME_SLOT_CHOICES, blank= True, null=True, max_length=255, default='Anytime_In_The_Future')

    price = models.FloatField(default=0)
    
    is_default = models.BooleanField(default=False)
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)
    
    is_package = models.BooleanField(default=False)
    image = models.ImageField(upload_to='service/service_images/', null=True, blank=True)
    is_image_uploaded_s3 = models.BooleanField(default=False)
    objects = ServiceManager.as_manager()

    def save(self, *args, **kwargs):
        if self.image:
            self.is_image_uploaded_s3 = True
            
        translator = Translator()

        arabic_text = translator.translate(f'{self.name}'.title(), dest='ar')
        text = arabic_text.text
        self.arabic_name = text

        if not self.arabic_id:
            arabic_id_ = translator.translate(self.id, dest='ar')
            self.arabic_id = arabic_id_.text
        super(Service, self).save(*args, **kwargs)


    def __str__(self):
        return str(self.id)
    
class ServiceGroup(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_servicesgroup')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_servicesgroup', null=True, blank=True)
    
    name = models.CharField(max_length=100, default='')
    services = models.ManyToManyField(Service, null=True, blank=True, related_name='servicegroup_services')
    
    allow_client_to_select_team_member = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    image = models.ImageField(upload_to='servicegroup/service_group_images/', null=True, blank=True)
    is_image_uploaded_s3 = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)
    
    def save(self, *args, **kwargs):
        if self.image:
            self.is_image_uploaded_s3 = True
        super(ServiceGroup, self).save(*args, **kwargs)
    
class PriceService(models.Model):
    DURATION_CHOICES = [
        ('30_Min' , '30 Min'),
        ('60_Min' , '60 Min'),
        ('90_Min' , '90 Min'),
        ('120_Min' , '120 Min'),
        ('150_Min' , '150 Min'),
        ('180_Min' , '180 Min'),
        ('210_Min' , '210 Min'),
    ]
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='service_priceservice')
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True, related_name='priceservice_currency')

    duration = models.CharField(max_length=50, null=True, blank=True, choices=DURATION_CHOICES )
    price = models.FloatField(default=0)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return str(self.id)
    

class ServiceTranlations(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, null=True, blank=True)
    service_name = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.service_name

    
    
