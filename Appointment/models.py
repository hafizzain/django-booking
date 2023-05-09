from datetime import datetime, timedelta
import uuid
from xml.parsers.expat import model
from django.db import models

from Authentication.models import User
from Business.models import Business, BusinessAddress
from django.utils.timezone import now
from Service.models import Service
from Client.models import Client, Membership, Promotion, Rewards, Vouchers
from Employee.models import Employee
from Utility.Constants.Data.Durations import DURATION_CHOICES_DATA

class AppointmentLogs(models.Model):
    LOG_TYPE_CHOICES =[
        ('Create' , 'Create'),
        ('Edit', 'Edit'),
        ('Reschedule', 'Reschedule'),
        ('Cancel', 'Cancel'),
    ]

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    member = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name='appointmentlogs_staffname', null=True, blank=True)
    
    location = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointmentlogs_location')

    log_type = models.CharField(choices=LOG_TYPE_CHOICES, max_length=50, null=True, blank=True, )
    customer_type =  models.CharField(max_length=50, null=True, blank=True, default='' )
    # not in use : customer_type

    appointment = models.ForeignKey('Appointment', on_delete=models.SET_NULL, related_name='appointmentlogs_service_type', null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    
    def __str__(self):
        return str(self.id)
    

class LogDetails(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    log = models.ForeignKey(AppointmentLogs, on_delete=models.CASCADE, related_name='appointment_log_details')
    appointment_service = models.ForeignKey('AppointmentService', on_delete=models.CASCADE, related_name='app_service_logs')

    start_time = models.TimeField()
    duration = models.CharField(default='', max_length=400)
    member = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name='member_log_details', null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)


    def __str__(self):
        return str(self.id)


class Appointment(models.Model):
    DISCOUNT_CHOICES =[
        ('Promotions' , 'Promotions'),
        ('Rewards', 'Rewards'),
        ('Vouchers', 'Vouchers'),
        ('Memberships', 'Memberships'),
        ('Subscriptions', 'Subscriptions')
    ]
    TYPE_CHOICES = [
        ('IN HOUSE', 'IN HOUSE'),
        ('SALOON', 'SALOON'),
    ]
    PAYMENT_CHOICES = [
        ('Cash', 'Cash'),
        ('Voucher', 'Voucher'),
        ('SplitBill', 'SplitBill'),
        ('MasterCard', 'MasterCard'),
        ('Visa', 'Visa'),
        ('Paypal', 'Paypal'),
        ('GooglePay', 'Google Pay'),
        ('ApplePay', 'Apple Pay')
    ]
    
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_appointments', verbose_name='Creator ( User )')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_appointments')

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_appointments', null=True, blank=True)
    business_address = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointment_address')
    member = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name='employee_appointments_lg', null=True, blank=True)

    
    client_type= models.CharField(choices=TYPE_CHOICES, max_length=50, null=True, blank=True, )
    discount_type = models.CharField(max_length=50, choices= DISCOUNT_CHOICES, null=True, blank=True)
    payment_method = models.CharField(max_length=100, choices= PAYMENT_CHOICES, default='', null=True, blank=True)  
    
    extra_price  = models.PositiveIntegerField(default=0, null=True, blank=True)
    tip  = models.PositiveIntegerField(default=0, null=True, blank=True)
    
    discount_price  = models.PositiveIntegerField(default=0, null=True, blank=True)
    discount_percentage = models.PositiveBigIntegerField(default = 0 , null=True, blank=True)
    
    service_commission = models.PositiveBigIntegerField(default = 0 , null=True, blank=True)    
    service_commission_type = models.CharField( max_length=50 , default = '')
    
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_checkout = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)


    def business_name(self):
        try:
            return str(self.business.business_name)

        except:
            return ''


    def __str__(self):
        return str(self.id)

    
class AppointmentService(models.Model):
    
    BOOKED_CHOICES = [
        ('Appointment_Booked',  'Appointment Booked'),
        ('Arrived', 'Arrived'),
        ('In Progress', 'In Progress'),
        ('Done', 'Done'),
        ('Paid', 'Paid'),
        ('Cancel', 'Cancel'),
    ]

    
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_appointment_services', verbose_name='Creator ( User )')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True, blank=True, related_name='business_appointment_services')
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True, related_name='appointment_services')
    business_address = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='b_address_appointment_services')

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='serivce_appointments', null=True, blank=True)
    member = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name='member_appointments', null=True, blank=True)
    is_favourite = models.BooleanField(default = False)
        
    appointment_date = models.DateField()
    appointment_time = models.TimeField(verbose_name='Appointment Start Time')

    duration = models.CharField(max_length=100, default='')
    
    client_can_book = models.CharField(max_length=100, default='', null=True, blank=True)
    slot_availible_for_online = models.CharField(max_length=100, default='', null=True, blank=True,)
    
    appointment_status = models.CharField(choices=BOOKED_CHOICES, max_length=100, default='Appointment Booked')
    tip = models.PositiveIntegerField(default=0, null=True, blank=True)
    
    price = models.PositiveIntegerField(default=0, null=True, blank=True)
    
    service_commission = models.PositiveBigIntegerField(default = 0 , null=True, blank=True)    
    service_commission_type = models.CharField( max_length=50 , default = '')
    
    discount_price = models.PositiveBigIntegerField(default = 0 , null=True, blank=True)    
    discount_percentage = models.PositiveBigIntegerField(default = 0 , null=True, blank=True)
        
    total_price = models.PositiveBigIntegerField(default = 0 , null=True, blank=True)    
    
    end_time = models.TimeField(null=True, blank=True)
    details = models.CharField(max_length=255, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    
    def member_name(self):
        try:
            return str(self.member.full_name)
        except:
            return None

    def appointment_end_time(self):
        app_date_time = f'2000-01-01 {self.appointment_time}'

        try:
            duration = DURATION_CHOICES_DATA[self.duration]
            app_date_time = datetime.fromisoformat(app_date_time)
            datetime_duration = app_date_time + timedelta(minutes=duration)
            datetime_duration = datetime_duration.strftime('%H:%M:%S')
            return datetime_duration
        except Exception as err:
            return str(err)
    

    def __str__(self):
        return str(self.id)


class AppointmentCheckout(models.Model):
    PAYMENT_CHOICES = [
        ('Cash', 'Cash'),
        ('Voucher', 'Voucher'),
        ('SplitBill', 'SplitBill'),
        ('MasterCard', 'MasterCard'),
        ('Visa', 'Visa'),
        ('Paypal', 'Paypal'),
        ('GooglePay', 'Google Pay'),
        ('ApplePay', 'Apple Pay')
    ]    
    
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True , related_name='appointment_checkout')
    appointment_service = models.ForeignKey(AppointmentService, on_delete=models.CASCADE, null=True, blank=True ,related_name='appointment_service_checkout')
    
    payment_method = models.CharField(max_length=100, choices= PAYMENT_CHOICES, default='', null=True, blank=True)  
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='checkout_service_appointments', null=True, blank=True)
    member = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='checkout_member_appointments', null=True, blank=True)
    business_address = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointment_address_checkout')

    voucher =models.ForeignKey(Vouchers, on_delete=models.CASCADE, related_name='checkout_voucher_appointments', null=True, blank=True) 
    promotion =models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='checkout_promotion_appointments', null=True, blank=True) 
    membership =models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='checkout_membership_appointments', null=True, blank=True) 
    rewards =models.ForeignKey(Rewards, on_delete=models.CASCADE, related_name='checkout_reward_appointments', null=True, blank=True) 
    
    tip = models.PositiveIntegerField(default=0, null=True, blank=True)
    gst = models.PositiveIntegerField(default=0, null=True, blank=True)
    gst_price = models.FloatField(default=0, null=True, blank=True)
    
    service_price = models.PositiveIntegerField(default=0, null=True, blank=True)
    total_price = models.PositiveIntegerField(default=0, null=True, blank=True)
    
    service_commission = models.PositiveBigIntegerField(default = 0 , null=True, blank=True)    
    service_commission_type = models.CharField( max_length=50 , default = '')


    is_promotion = models.BooleanField(default=False)
    selected_promotion_id = models.CharField(default='', max_length=800)
    selected_promotion_type = models.CharField(default='', max_length=400)
    """
        Direct Or Flat
        Specific Group Discount
        Purchase Discount
        Specific Brand Discount
        Spend_Some_Amount
        Fixed_Price_Service
        Mentioned_Number_Service
        Bundle_Fixed_Service
        Retail_and_Get_Service
        User_Restricted_discount
        Complimentary_Discount
        Packages_Discount
    """
    
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    
    def __str__(self):
        return str(self.id)
    
    @property
    def fun():
        return 'rewards'

class AppointmentEmployeeTip(models.Model):    
    
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True , related_name='tips_checkout')    
    member = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='checkout_member_tips', null=True, blank=True)
    
    business_address = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointment_address_tips')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True, blank=True, related_name='business_appointment_tips') 

    tip = models.PositiveIntegerField(default=0, null=True, blank=True)
    gst = models.PositiveIntegerField(default=0, null=True, blank=True)
    gst_price = models.FloatField(default=0, null=True, blank=True)
    
    service_price = models.PositiveIntegerField(default=0, null=True, blank=True)
    total_price = models.PositiveIntegerField(default=0, null=True, blank=True)
    
    
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    
    def __str__(self):
        return str(self.id)



class AppointmentNotes(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='appointment_notes')
    
    text = models.TextField(default='', null=True, blank=True)
    
    def __str__(self):
        return str(self.id)

