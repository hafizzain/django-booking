from django.db import models
from django.utils.timezone import now
from Authentication.models import User
from Client.models import Client
from Employee.models import Employee
from Business.models import BusinessAddress
from uuid import uuid4
from Appointment.models import Appointment
import pdfkit
from django.conf import settings
from django.template.loader import get_template
import os
from django.db import connection


class SaleInvoice(models.Model):
    status_choice=[
        ('Completed', 'Completed'),
        ('Incompleted', 'Incompleted'),
        ('Expired', 'Expired'),
        ('Active', 'Active'),        
    ]
    
    CLIENT_TYPE=[
        ('Walk_in', 'Walk-in'),
        ('In_Saloon', 'In-Saloon'),
    ]
    PAYMENT_TYPE=[
        ('Cash', 'Cash'),
        ('Voucher', 'Voucher'),
        ('SplitBill', 'SplitBill'),
        ('MasterCard', 'MasterCard'),
        ('Other', 'Other'),
        
    ]
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    location = models.ForeignKey(BusinessAddress, on_delete=models.CASCADE, null=True, blank=True)
    member = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
    client_type = models.CharField(choices = CLIENT_TYPE, max_length=50 , default = '', null=True, blank=True )
    payment_type = models.CharField(choices = PAYMENT_TYPE, max_length=50 , default = '', null=True, blank=True )
    tip = models.FloatField(default = 0)
    total_service_price = models.FloatField(default = 0 , null=True, blank=True)
    total_product_price = models.FloatField(default = 0 , null=True, blank=True)
    total_voucher_price = models.FloatField(default = 0 , null=True, blank=True)
    total_membership_price = models.FloatField(default = 0 , null=True, blank=True)
    
    service_commission = models.FloatField(default = 0 , null=True, blank=True)
    product_commission = models.FloatField(default = 0 , null=True, blank=True)
    voucher_commission = models.FloatField(default = 0 , null=True, blank=True)
    
    service_commission_type = models.CharField( max_length=50 , default = '', null=True, blank=True)
    product_commission_type = models.CharField( max_length=50 , default = '', null=True, blank=True)
    voucher_commission_type = models.CharField( max_length=50 , default = '', null=True, blank=True)
    
    is_promotion = models.BooleanField(default=False)
    selected_promotion_id = models.CharField(default='', max_length=800, null=True, blank=True)
    selected_promotion_type = models.CharField(default='', max_length=400, null=True, blank=True)
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True)
    appointment_service = models.CharField(max_length=2000, default='', null=True, blank=True)
    service = models.CharField(max_length=2000, default='', null=True, blank=True)
    member = models.CharField(max_length=2000, default='', null=True, blank=True)
    business_address = models.CharField(max_length=2000, default='', null=True, blank=True)

    gst = models.FloatField(default=0, null=True, blank=True)
    gst_price = models.FloatField(default=0, null=True, blank=True)
    
    service_price = models.FloatField(default=0, null=True, blank=True)
    total_price = models.FloatField(default=0, null=True, blank=True)
    checkout = models.CharField(max_length=128, null=True, blank=True)

    file = models.FileField(upload_to='invoicesFiles/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return str(self.id)
    
    @property
    def short_id(self):
        uuid = f'{self.id}'
        uuid = uuid.split('-')[0]
        return uuid
    
    def save(self, *args, **kwargs):
        if not self.file:
            context = {}
            schema_name = connection.schema_name
            output_dir = f'{settings.BASE_DIR}/media/{schema_name}/invoicesFiles'
            is_exist = os.path.isdir(output_dir)
            if not is_exist:
                os.mkdir(output_dir)

            file_name = f'invoice-{self.short_id}.pdf'
            output_path = f'{output_dir}/{file_name}'
            no_media_path = f'{schema_name}/invoicesFiles/{file_name}'
            template = get_template(f'{settings.BASE_DIR}/templates/Sales/invoice.html')
            html_string = template.render(context)
            pdfkit.from_string(html_string, os.path.join(output_path))
            self.file = no_media_path

        super(SaleInvoice, self).save(*args, **kwargs)