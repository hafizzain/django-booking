from django.db import models

from Authentication.models import User
from Utility.models import CommonField
from SaleRecords.choices import *

from Business.models import BusinessAddress
from Promotions.models import Coupon
from Product.models import Product
from Service.models import Service
from Employee.models import Employee
from Promotions.models import Coupon
from Client.models import Client, Membership, Promotion, Rewards, Vouchers, LoyaltyPointLogs
from Finance.models import Refund

class Tax(models.Model):
    tax_name = models.CharField(max_length = 50, null= True)
    tax_amount = models.DecimalField(max_digit = 10 , decimal_places = 2)



class SaleRecords(CommonField):
    coupon_discounted_price = models.FloatField(null=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True, blank=True)
    is_coupon_redeemed = models.TextField(null=True)
    tip = models.FloatField(default=0, null=True, blank=True)
    is_refund = models.CharField(max_length=50, null=True, blank=True)
    checkout_type = models.CharField(choices = CheckoutType.choices, max_length = 50, null=True)
    previous_checkout = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='refunded_checkout')
    tax = models.ForeignKey(Tax, on_delete= models.CASCADE, related_name = 'sale_taxs')
    refunds_data = models.ForeignKey(Refund, on_delete = models.CASCADE, null= True, blank= True, related_name = 'refunds')
    
    

    total_discount = models.FloatField(default=None, null=True, blank=True)
    voucher_redeem_percentage = models.FloatField(default=None, null=True, blank=True)
    redeem_option = models.CharField(max_length=250, default=None, null=True, blank=True)

    is_promotion = models.BooleanField(default=False)
    selected_promotion_id = models.CharField(default='', max_length=800)
    selected_promotion_type = models.CharField(default='', max_length=400)
    status = models.CharField(max_length=100, default='Active')
    sub_total = models.DecimalField(max_digit = 10, decimal_places = 2)

    # Fields specific to AppointmentCheckout
    payment_method = models.CharField(max_length=100, null=True, blank=True)
    # payment_methods = models.
    
    
    service_price = models.FloatField(default=0, null=True, blank=True)
    total_price = models.FloatField(default=0, null=True, blank=True)

    # Fields specific to Checkout
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_checkout_order', null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_checkout_orders', null=True, blank=True)
    location = models.ForeignKey(BusinessAddress, on_delete=models.CASCADE, related_name='location_checkout_orders', null=True, blank=True)
    member = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='member_checkout_orders', null=True, blank=True)
    client_type = models.CharField(choices=ClientTypeChoices.choices, max_length=50, default='')
    payment_type = models.CharField(choices=PaymentMethods.choices, max_length=50, default='')

    class Meta:
        verbose_name_plural = 'Sale Records'


    
class CheckoutServices(CommonField):
    sale_records = models.ForeignKey(SaleRecords, on_delete = models.CASCADE, null= True, blank = True)
    services = models.ForeignKey(Service, on_delete = models.CASCADE, null = True, blank = True)
    
    
class CheckoutProducts(CommonField):
    sale_records = models.ForeignKey(SaleRecords, on_delete = models.CASCADE, null = True, blank = True)
    products = models.ForeignKey(Product, on_delete= models.CASCADE, null= True, blank=True)
    
    