from django.db import models
from Authentication.models import User
from Business.models import Business
from Product.models import Product
from Service.models import Service

from Business.models import BusinessAddress
from Client.models import Client
from Invoices.models import SaleInvoice
from Finance.choices import *
from Utility.models import CommonField


# Create your models here.

class Refund(CommonField):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name = 'User id') 
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name = 'Client id', blank=True, null=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, verbose_name ='Business id')
    location = models.ForeignKey(BusinessAddress, on_delete=models.CASCADE, verbose_name = 'location id')
    refund_invoice_id = models.ForeignKey(SaleInvoice, on_delete=models.CASCADE, verbose_name = 'Invoice id')

    refund_type = models.CharField(choices=RefundChoices.choices, max_length=20)
    # reason = models.TextField()
    total_refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  

class RefundProduct(models.Model):
    refund = models.ForeignKey(Refund, on_delete=models.CASCADE, verbose_name = 'Refund id')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Product id')
    
    refunded_quantity = models.PositiveIntegerField()
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
class RefundServices(models.Model):
    refund = models.ForeignKey(Refund, on_delete=models.CASCADE, verbose_name = 'Refund id')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name='Service id')
    
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2)

class Coupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank= True, null= True)  
    
    refund_coupon_code = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateField()
    is_used = models.BooleanField(default=False)
    related_refund = models.ForeignKey(Refund, on_delete=models.CASCADE, )


