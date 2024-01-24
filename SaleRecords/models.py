from django.db import models
from uuid import uuid4
from Authentication.models import User
from Utility.models import CommonField
from SaleRecords.choices import *

from Business.models import BusinessAddress,  BusinessTax
from Promotions.models import Coupon
from Product.models import Product
from Service.models import Service
from Employee.models import Employee
from Promotions.models import Coupon
from Client.models import Client, Membership, Promotion, Rewards, Vouchers, LoyaltyPointLogs
from Finance.models import Refund
from Order.models import Checkout
from Appointment.models import AppointmentCheckout, AppointmentEmployeeTip , Appointment
from Invoices.models import SaleInvoice

# from Business.models import


class SaleRecords(CommonField):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sale_records_user', null=True, blank=True) 
    member = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='sale_records_member', null=True, blank=True) 
    
    
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True, blank=True) 
    coupon_discounted_price = models.FloatField(null=True) 
    coupon_discounted_price = models.FloatField(null=True)  
    is_coupon_redeemed = models.TextField(null=True) 
    
    business_address = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='sale_records_business_address') 

    checkout_type = models.CharField(choices = CheckoutType.choices, max_length = 50, null=True) 
    # checkout = models.ForeignKey(Checkout, on_delete=models.CASCADE, related_name='sale_orders_checkout', null=True, blank=True) 
    # appointment_checkout = models.ForeignKey(AppointmentCheckout, on_delete=models.CASCADE, related_name='appointment_orders_checkout', null=True, blank=True) 

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='sale_records_client', null=True, blank=True) 
    employee = models.ForeignKey(Employee, on_delete = models.CASCADE)
    client_type = models.CharField(choices=ClientTypeChoices.choices, max_length=50, default='') 
    
    invoice = models.ForeignKey(SaleInvoice, on_delete = models.SET_NULL, null= True) 
    
    # is_refund = models.CharField(max_length=50, null=True, blank=True) 
    refunds_data = models.ForeignKey(Refund, on_delete = models.CASCADE, null= True, blank= True, related_name = 'refunds') 
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True, blank=True)  
    

    total_discount = models.FloatField(default=None, null=True, blank=True) 
    voucher_redeem_percentage = models.FloatField(default=None, null=True, blank=True) 
    redeem_option = models.CharField(max_length=250, default=None, null=True, blank=True)
    # tip = models.FloatField(default=0, null=True, blank=True) 

    is_promotion = models.BooleanField(default=False) 
    selected_promotion_id = models.CharField(default='', max_length=800) 
    # selected_promotion_type = models.CharField(default='', max_length=400) 
    status = models.CharField(choices = Status.choices, max_length=50 , default = Status.UN_PAID) 
    
    sub_total = models.FloatField(default =0 , null = True, blank = True) 

    # is_coupon_redeemed = models.TextField(null=True) 

    class Meta:
        verbose_name_plural = 'Sale Records'


class SaleRecordServices(CommonField):
    sale_record = models.ForeignKey(SaleRecords, on_delete = models.CASCADE, related_name = 'sale_services_records')
    service = models.ForeignKey(Service, on_delete = models.CASCADE)
    qty = models.PositiveIntegerField(default = 0)
    price = models.FloatField(default =0 , null = True, blank = True)
    
    
class SaleRecordsProducts(CommonField):
    sale_record = models.ForeignKey(SaleRecords, on_delete = models.CASCADE, related_name = 'sale_products_records')
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    qty = models.PositiveIntegerField(default = 0)
    price = models.FloatField(default =0 , null = True, blank = True)
    
    
class SaleRecordsAppointmentServices(CommonField):
    sale_record = models.ForeignKey(SaleRecords, on_delete = models.CASCADE, null =True , blank =True , related_name = 'appointment_services')
    appointment = models.ForeignKey(Appointment, on_delete = models.CASCADE ,null = True, blank= True, related_name = 'related_appointment')
    
    
    service = models.ForeignKey(Service, on_delete = models.CASCADE)
    appointment_status = models.CharField(choices = AppointmentStatus.choices,max_length = 50, default = AppointmentStatus.BOOKED)
    reason = models.CharField(max_length = 255, null = True, blank = True)
    qty = models.PositiveIntegerField(default = 0)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration = models.PositiveIntegerField(default = 0)
    is_favourite = models.BooleanField(default = False)
    # appointment_notes = models.CharField(max_length = 255 , null = True , blank = True)
    
    
class PaymentMethods(CommonField):
    sale_records = models.ForeignKey(SaleRecords, on_delete = models.CASCADE, related_name = 'sale_payment_methods_records')
    
    payment_method = models.CharField(choices = PaymentMethods.choices, max_length = 50 , default = '')
    amount = models.FloatField(default  = 0 , null = True, blank = True)
class RedeemedItems(CommonField):
    sale_order = models.ForeignKey(SaleRecords, on_delete=models.CASCADE, related_name='sale_redeemed_items_records') 
    
    item_id  = models.CharField(max_length = 50)
    redeemed_type = models.CharField(max_length = 50, null = True, blank = True)
    is_redeemed = models.BooleanField(default = False , null = True, blank = True)

class SaleRecordAppliedCoupons(CommonField):
    sale_records = models.ForeignKey(SaleRecords, on_delete = models.CASCADE, null = True, blank = True, related_name = 'sale_applied_coupons_records')
    
    coupon_type = models.CharField(choices = CouponType.choices,max_length = 50, default = '')
    is_coupon_redeemed = models.BooleanField(default = False,null=True , blank = True) 

class SaleTax(CommonField):
    # self.id is a seperate field 
    
    sale_order = models.ForeignKey(SaleRecords, on_delete=models.CASCADE, related_name='sale_tax_records') 

    # Following are the Major Information for Tax Applied
    business_tax_id = models.ForeignKey(BusinessTax, on_delete=models.SET_NULL, null=True) # This will be Tax Instance ID 
    tax_name = models.CharField(max_length=999, default='') 
    # tax_amount = models.FloatField(default=0, null= True, blank = True)  null = True, blank = True
    tax_percentage = models.FloatField(default=0, null = True, blank = True ) 

    def __str__(self):
        return self.tax_name

class SaleRecordTip(CommonField):    
    sale_record = models.ForeignKey(SaleRecords, on_delete=models.CASCADE, null=True, blank=True,related_name='sale_tip_records') 
    
    member = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='sale_record_employee_tips', null=True, blank=True) 
    tip_amount = models.FloatField(default=0, null=True, blank=True) 
    
    def __str__(self): 
        return str(self.id) 
    