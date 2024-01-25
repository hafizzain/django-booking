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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True, related_name='sale_records_user') 
    # employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='sale_records_member') 
    business_address = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null = True, related_name='sale_records_business_address') 
    invoice = models.ForeignKey(SaleInvoice, on_delete = models.SET_NULL, null = True) 
    refunds_data = models.ForeignKey(Refund, on_delete = models.SET_NULL, null = True, blank=True, related_name = 'refunds') 
    

    checkout_type = models.CharField(choices = CheckoutType.choices, max_length = 50) 
    
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null = True, related_name='sale_records_client')
    client_type = models.CharField(choices=ClientTypeChoices.choices, max_length=50, blank=False, null=False) 
    
    

    is_promotion = models.BooleanField(null = False, blank = False) 
    selected_promotion_id = models.CharField( max_length=800, blank=False, null=False) 
    selected_promotion_type = models.CharField( max_length=400, blank=False, null=False) 
    status = models.CharField(choices = Status.choices, max_length=50 , default = Status.UN_PAID) 
    
    sub_total = models.FloatField(blank=False, null=False) 

    # is_coupon_redeemed = models.TextField(null=True) 

    class Meta:
        verbose_name_plural = 'Sale Records'


class SaleRecordServices(CommonField):
    sale_record = models.ForeignKey(SaleRecords, on_delete = models.CASCADE, blank=True, null=True, related_name = 'sale_services_records')
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null = True)
    service = models.ForeignKey(Service, on_delete = models.SET_NULL, null = True)
    
    qty = models.PositiveIntegerField(blank=False, null=False)
    price = models.FloatField(blank=False, null=False)
    
    
class SaleRecordsProducts(CommonField):
    sale_record = models.ForeignKey(SaleRecords, on_delete = models.CASCADE, blank=True, null=True, related_name = 'sale_products_records')
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null = True)
    product = models.ForeignKey(Product, on_delete = models.SET_NULL, null = True)
    
    qty = models.PositiveIntegerField(blank=False, null=False)
    price = models.FloatField(blank=False, null=False)
    
    
class SaleRecordsAppointmentServices(CommonField):
    sale_record = models.ForeignKey(SaleRecords, on_delete = models.CASCADE, null =True , blank =True , related_name = 'sale_appointment_services_records')
    appointment = models.ForeignKey(Appointment, on_delete = models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null = True, related_name='sale_appointment_services_employee')
    
    
    service = models.ForeignKey(Service, on_delete = models.SET_NULL, null = True)
    appointment_status = models.CharField(choices = AppointmentStatus.choices,max_length = 50, default = AppointmentStatus.BOOKED, blank=False, null=False)
    reason = models.CharField(max_length = 255, blank=False, null=False)
    qty = models.PositiveIntegerField(blank=False, null=False)
    start_time = models.DateTimeField(blank=False, null=False)
    end_time = models.DateTimeField(blank=False, null=False)
    duration = models.PositiveIntegerField(blank=False, null=False)
    is_favourite = models.BooleanField(blank=False, null=False)
    # appointment_notes = models.CharField(max_length = 255 , null = True , blank = True)
    
    
class SaleRecordVouchers(CommonField):
    sale_record = models.ForeignKey(SaleRecords, on_delete=models.CASCADE, blank=True, null=True, related_name='sale_vouchers_records')
    vouchers = models.ForeignKey(Vouchers, on_delete = models.SET_NULL, null = True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null = True, related_name='sale_vouchers_employee')
    
    price = models.FloatField(blank=False, null=False) 
    qty = models.PositiveSmallIntegerField(blank=False, null=False)


class SaleRecordMembership(CommonField):
    sale_record = models.ForeignKey(SaleRecords, on_delete=models.CASCADE, blank=True, null=True, related_name='sale_membership_records')
    membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, null = True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null = True, related_name='sale_membership_employee')
    
    
    price = models.FloatField(blank=False, null=False) 
    qty = models.PositiveSmallIntegerField(blank=False, null=False)
    
class PaymentMethods(CommonField):
    sale_record = models.ForeignKey(SaleRecords, on_delete = models.SET_NULL, null = True, related_name = 'sale_payment_methods_records')
    
    
    payment_method = models.CharField(choices = PaymentMethods.choices, max_length = 50 , null = True , blank = False)
    amount = models.FloatField(default  = 0 , blank= False)
    
class RedeemedItems(CommonField):
    sale_record = models.ForeignKey(SaleRecords, on_delete=models.CASCADE, related_name='sale_redeemed_items_records') 
    
    item_id  = models.CharField(max_length = 50 , blank=False, null=False)
    redeemed_type = models.CharField(max_length = 50, blank=False, null=False)
    is_redeemed = models.BooleanField(default = False, blank=False, null=False)
    percentage = models.FloatField(default=None, blank=False, null=False) 
    discount = models.FloatField(default=None, blank=False, null=False) 
    redeem_option = models.CharField(max_length=250, default=None, blank=False, null=False)
    
class SaleRecordAppliedCoupons(CommonField):
    
    sale_record = models.ForeignKey(SaleRecords, on_delete = models.CASCADE, null = True, blank = True, related_name = 'sale_applied_coupons_records')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL,null = True)
    
    coupon_type = models.CharField(choices = CouponType.choices,max_length = 50, default = '', blank=False, null=False)
    coupon_discounted_price = models.FloatField(default =0, blank=False, null=False) 
    coupon_discounted_price = models.FloatField(default =0, blank=False, null=False)
    is_coupon_redeemed = models.BooleanField(default = False, blank=False, null=False) 

class SaleTax(CommonField):
    # self.id is a seperate field 
    
    sale_record = models.ForeignKey(SaleRecords, on_delete=models.CASCADE, blank=True, null=True, related_name='sale_tax_records') 

    # Following are the Major Information for Tax Applied
    business_tax_id = models.ForeignKey(BusinessTax, on_delete=models.SET_NULL,  blank=False, null=True) # This will be Tax Instance ID 
    tax_name = models.CharField(max_length=999, blank=False, null=False) 
    # tax_amount = models.FloatField(default=0, null= True, blank = True)  null = True, blank = True
    tax_percentage = models.FloatField(blank=False, null=False) 

    def __str__(self):
        return self.tax_name

    
    

class SaleRecordTip(CommonField):    
    sale_record = models.ForeignKey(SaleRecords, on_delete=models.CASCADE, null=True, blank=True,related_name='sale_tip_records') 
    
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null = True, related_name='sale_record_employee_tips') 
    tip_amount = models.FloatField(blank=False, null=False) 
    
    def __str__(self): 
        return str(self.id) 
    