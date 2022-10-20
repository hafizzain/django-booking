from datetime import datetime, timedelta
import uuid
from xml.parsers.expat import model
from django.db import models

from Authentication.models import User
from Business.models import Business, BusinessAddress
from django.utils.timezone import now
from Service.models import Service
from Client.models import Client
from Employee.models import Employee
from Utility.Constants.Data.Durations import DURATION_CHOICES_DATA


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
    
    client_type= models.CharField(choices=TYPE_CHOICES, max_length=50, null=True, blank=True, )
    discount_type = models.CharField(max_length=50, choices= DISCOUNT_CHOICES, null=True, blank=True)
    payment_method = models.CharField(max_length=100, choices= PAYMENT_CHOICES, default='', null=True, blank=True)  

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
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

    DURATION_CHOICES = [
        ('30 Min', '30 Min'), 
        ('60 Min', '60 Min'),
        ('90 Min', '90 Min'),
        ('120 Min', '120 Min'),
        ('150 Min', '150 Min'),
        ('180 Min', '180 Min'),
        ('210 Min', '210 Min'),
        ('240 Min', '240 Min'),
    ]
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_appointment_services', verbose_name='Creator ( User )')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True, blank=True, related_name='business_appointment_services')
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True, related_name='appointment_services')
    business_address = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='b_address_appointment_services')

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='serivce_appointments', null=True, blank=True)
    member = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name='member_appointments', null=True, blank=True)
    
    appointment_date = models.DateField()
    appointment_time = models.TimeField()

    duration = models.CharField(choices=DURATION_CHOICES, max_length=100, default='')
    appointment_status = models.CharField(choices=BOOKED_CHOICES, max_length=100, default='Appointment Booked')
    tip = models.PositiveIntegerField(default=0, null=True, blank=True)
    
    end_time = models.TimeField(null=True, blank=True)
    destails = models.CharField(max_length=255, null=True, blank=True)

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
    
    tip = models.PositiveIntegerField(default=0, null=True, blank=True)
    gst = models.PositiveIntegerField(default=0, null=True, blank=True)
    
    service_price = models.PositiveIntegerField(default=0, null=True, blank=True, )
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

