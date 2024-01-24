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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sale_records_user') 
    member = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='sale_records_member') 
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='sale_records_client')
    business_address = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, related_name='sale_records_business_address') 
    invoice = models.ForeignKey(SaleInvoice, on_delete = models.SET_NULL) 
    refunds_data = models.ForeignKey(Refund, on_delete = models.CASCADE, related_name = 'refunds') 
    

    checkout_type = models.CharField(choices = CheckoutType.choices, max_length = 50) 
    client_type = models.CharField(choices=ClientTypeChoices.choices, max_length=50, default='') 
    
    

    is_promotion = models.BooleanField(default=False) 
    selected_promotion_id = models.CharField(default='', max_length=800) 
    selected_promotion_type = models.CharField(default='', max_length=400) 
    status = models.CharField(choices = Status.choices, max_length=50 , default = Status.UN_PAID) 
    
    sub_total = models.FloatField(default =0 ) 

    # is_coupon_redeemed = models.TextField(null=True) 

    class Meta:
        verbose_name_plural = 'Sale Records'


class SaleRecordServices(CommonField):
    sale_record = models.ForeignKey(SaleRecords, on_delete = models.CASCADE, blank=True, null=True, related_name = 'sale_services_records')
    service = models.ForeignKey(Service, on_delete = models.CASCADE)
    qty = models.PositiveIntegerField(default = 0)
    price = models.FloatField(default =0)
    
    
class SaleRecordsProducts(CommonField):
    sale_record = models.ForeignKey(SaleRecords, on_delete = models.CASCADE, blank=True, null=True, related_name = 'sale_products_records')
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    qty = models.PositiveIntegerField(default = 0)
    price = models.FloatField(default =0)
    
    
class SaleRecordsAppointmentServices(CommonField):
    sale_record = models.ForeignKey(SaleRecords, on_delete = models.CASCADE, null =True , blank =True , related_name = 'appointment_services')
    appointment = models.ForeignKey(Appointment, on_delete = models.CASCADE, related_name = 'related_appointment')
    
    
    service = models.ForeignKey(Service, on_delete = models.CASCADE)
    appointment_status = models.CharField(choices = AppointmentStatus.choices,max_length = 50, default = AppointmentStatus.BOOKED)
    reason = models.CharField(max_length = 255)
    qty = models.PositiveIntegerField(default = 0)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration = models.PositiveIntegerField(default = 0)
    is_favourite = models.BooleanField(default = False)
    # appointment_notes = models.CharField(max_length = 255 , null = True , blank = True)
    
    
class PaymentMethods(CommonField):
    sale_records = models.ForeignKey(SaleRecords, on_delete = models.CASCADE, related_name = 'sale_payment_methods_records')
    
    payment_method = models.CharField(choices = PaymentMethods.choices, max_length = 50 , default = '')
    amount = models.FloatField(default  = 0)
    
class RedeemedItems(CommonField):
    sale_order = models.ForeignKey(SaleRecords, on_delete=models.CASCADE, related_name='sale_redeemed_items_records') 
    
    item_id  = models.CharField(max_length = 50)
    redeemed_type = models.CharField(max_length = 50)
    is_redeemed = models.BooleanField(default = False)
    percentage = models.FloatField(default=None) 
    discount = models.FloatField(default=None) 
    redeem_option = models.CharField(max_length=250, default=None)
    
class SaleRecordAppliedCoupons(CommonField):
    
    sale_records = models.ForeignKey(SaleRecords, on_delete = models.CASCADE, null = True, blank = True, related_name = 'sale_applied_coupons_records')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL)
    
    coupon_type = models.CharField(choices = CouponType.choices,max_length = 50, default = '')
    coupon_discounted_price = models.FloatField(default =0) 
    coupon_discounted_price = models.FloatField(default =0)
    is_coupon_redeemed = models.BooleanField(default = False) 

class SaleTax(CommonField):
    # self.id is a seperate field 
    
    sale_order = models.ForeignKey(SaleRecords, on_delete=models.CASCADE, blank=True, null=True, related_name='sale_tax_records') 

    # Following are the Major Information for Tax Applied
    business_tax_id = models.ForeignKey(BusinessTax, on_delete=models.SET_NULL) # This will be Tax Instance ID 
    tax_name = models.CharField(max_length=999, default='') 
    # tax_amount = models.FloatField(default=0, null= True, blank = True)  null = True, blank = True
    tax_percentage = models.FloatField(default=0) 

    def __str__(self):
        return self.tax_name

class SaleRecordTip(CommonField):    
    sale_record = models.ForeignKey(SaleRecords, on_delete=models.CASCADE, null=True, blank=True,related_name='sale_tip_records') 
    
    member = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name='sale_record_employee_tips') 
    tip_amount = models.FloatField(default=0) 
    
    def __str__(self): 
        return str(self.id) 
    