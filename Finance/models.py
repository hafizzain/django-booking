from django.db import models
from Authentication.models import User
from Business.models import Business
from Product.models import Product
from Service.models import Service
from Employee.models import Employee

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

class RefundProduct(CommonField):
    
    refund = models.ForeignKey(Refund, on_delete=models.CASCADE, related_name='refunded_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    
    refunded_quantity = models.PositiveIntegerField()
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2)
    in_stock = models.BooleanField(default = False)
    checkouts = models.CharField(null=True, blank=True, max_length=150)
    
class RefundServices(CommonField):
    refund = models.ForeignKey(Refund, on_delete=models.CASCADE, related_name='refunded_services')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    
    quantity = models.PositiveBigIntegerField(default = 0)
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2)
    checkouts = models.CharField(null=True, blank=True, max_length=150)

class RefundCoupon(CommonField):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank= True, null= True)  
    
    refund_coupon_code = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateField()
    is_used = models.BooleanField(default=False)
    
    related_refund = models.ForeignKey(Refund, on_delete=models.CASCADE, null=True,  related_name='related_refund_coupon')



# ==================================================== Permission for refund =====================================================


class AllowRefunds(CommonField):
    location = models.ForeignKey(BusinessAddress, on_delete = models.CASCADE, related_name = 'allowed_refund_locations')
    # sale_invoice = models.ForeignKey(SaleInvoice, on_delete = models.CASCADE, null=True)
    number_of_days = models.PositiveIntegerField(default = 30)
    
class AllowRefundPermissionsEmployees(CommonField):
    allowed_refund = models.ForeignKey(AllowRefunds, on_delete= models.CASCADE, related_name = 'allowed_refund')
    employee = models.ForeignKey(Employee, on_delete = models.CASCADE, related_name = 'employee')
    can_refund = models.BooleanField(default=False)