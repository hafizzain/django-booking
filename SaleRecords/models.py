from django.db import models
from uuid import uuid4
from Authentication.models import User
from Utility.models import CommonField
from SaleRecords.choices import *
from dateutil.relativedelta import relativedelta
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
# from datetime import datetime

from Appointment.models import  Appointment, AppointmentGroup
from Business.models import BusinessAddress,  BusinessTax
from Promotions.models import Coupon
from Product.models import Product
from Service.models import Service
from Employee.models import Employee, GiftCards
from Client.models import Client, Membership, Promotion, Rewards, Vouchers, LoyaltyPointLogs, LoyaltyPoints, ClientLoyaltyPoint
from Finance.models import Refund, RefundCoupon
from Client.helpers import calculate_validity
from Client.models import CurrencyPriceMembership

# from Invoices.models import SaleInvoice

# from Business.models import


class SaleRecords(CommonField):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True, related_name='sale_records_user') 
    # employee = models.ForeignKey(Employee, on_delete=models.SET_NULL,blank=True, null=True, related_name='sale_records_member') 
    location = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null = True, related_name='sale_records_business_address') 
    # invoice = models.ForeignKey(SaleInvoice, on_delete = models.SET_NULL, null = True, related_name = 'sale_record_invoice') 
    
    
    # refunds_data = models.ForeignKey(Refund, on_delete = models.SET_NULL, null = True, blank=True, related_name = 'sale_record_refunds') 
    
    checkout_type = models.CharField(choices = CheckoutType.choices, max_length = 50) 
    is_refund = models.BooleanField(default = False)
    
    
    # Client info
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null = True, blank=True, related_name='sale_records_client')
    client_type = models.CharField(choices=ClientTypeChoices.choices, max_length=50, blank=False, null=False) 
    
    status = models.CharField(choices = Status.choices, max_length=50 , default = Status.PAID) 
    
    
    total_tip = models.FloatField(blank=False, null=False)
    total_tax = models.FloatField(blank=False, null=False)
    total_price = models.FloatField(blank=False, null=False) # with tax amount
    sub_total = models.FloatField(blank=False, null=False)  # without tax amount
    change = models.FloatField(blank=True, null=True)
    discount_value = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Sale Records'


class SaleRecordServices(CommonField):
    sale_record = models.ForeignKey(SaleRecords, on_delete = models.CASCADE, blank=True, null=True, related_name = 'services_records')
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null = True)
    service = models.ForeignKey(Service, on_delete = models.SET_NULL, null = True, related_name = 'service_sale_record')
    
    quantity = models.PositiveIntegerField(blank=True, null=True)
    price = models.FloatField(default = 0, blank=True, null=True)
    discounted_price = models.FloatField(default = 0, blank=True, null=True)
    discount_percentage = models.FloatField(blank=True, null=True)
    
    
class SaleRecordsProducts(CommonField):
    sale_record = models.ForeignKey(SaleRecords, on_delete = models.CASCADE, blank=True, null=True, related_name = 'products_records')
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null = True)
    product = models.ForeignKey(Product, on_delete = models.SET_NULL, null = True, related_name = 'product_sale_records')
    
    quantity = models.PositiveIntegerField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    discounted_price = models.FloatField(default = 0, blank=True, null=True)
    discount_percentage = models.FloatField(blank=True, null=True)
    
    
class SaleRecordsAppointmentServices(CommonField):
    
    sale_record = models.ForeignKey(SaleRecords, on_delete = models.CASCADE, null =True , blank =True , related_name = 'appointment_services')
    
    client = models.ForeignKey(Client, on_delete = models.SET_NULL, blank = True,null=True, related_name = 'appointment_client')
    appointment = models.ForeignKey(Appointment, on_delete = models.SET_NULL, null = True, related_name = 'sale_appointments_records')
    group = models.ForeignKey(AppointmentGroup, on_delete = models.SET_NULL, blank=True, null=True, related_name = 'appointment_group')
    
    service = models.ForeignKey(Service, on_delete = models.SET_NULL, null = True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null = True, related_name='sale_appointment_services_employee')
    
    
    service_status = models.CharField(choices = AppointmentStatus.choices,max_length = 50, default = AppointmentStatus.BOOKED, blank=False, null=False)
    # quantity = models.PositiveIntegerField(blank=True, null=True)
    service_start_time = models.DateTimeField(blank=True, null=True)
    service_end_time = models.DateTimeField(blank=True, null=True)
    duration = models.CharField(max_length= 50,blank=True, null=True)
    price = models.FloatField(default = 0, blank=True, null=True)
    discounted_price = models.FloatField(default = 0, blank=True, null=True)
    is_favourite = models.BooleanField(blank=True, null=True , default = False)
    discount_percentage = models.FloatField(blank=True, null=True)
    # reason = models.CharField(max_length = 255, blank=True, null=True)
    # appointment_notes = models.CharField(max_length = 255 , null = True , blank = True)
    
    
class SaleRecordVouchers(CommonField):
    sale_record = models.ForeignKey(SaleRecords, on_delete=models.CASCADE, blank=True, null=True, related_name='vouchers_records')
    voucher = models.ForeignKey(Vouchers, on_delete = models.SET_NULL, null = True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    expiry = models.DateTimeField(blank=True, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null = True, related_name='sale_vouchers_employee')
    
    price = models.FloatField(blank=True, null=True) 
    quantity = models.PositiveSmallIntegerField(blank=True, null=True)


class SaleRecordMembership(CommonField):
    sale_record = models.ForeignKey(SaleRecords, on_delete=models.CASCADE, blank=True, null=True, related_name='membership_records')
    membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, null = True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    expiry = models.DateTimeField(blank=True, null=True)
    installment_months = models.SmallIntegerField(blank=True, null=True)
    remaining_installments = models.SmallIntegerField(blank=True, null=True)
    installment_price = models.FloatField(blank=True, null=True)
    is_installment = models.BooleanField(default = False)
    payable_amount = models.FloatField(blank=True, null=True)
    next_installment_date =  models.DateTimeField(blank=True, null=True)
    
    # employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null = True, related_name='sale_membership_employee')
    
    price = models.FloatField(blank=True, null=True) 
    quantity = models.PositiveSmallIntegerField(blank=True, null=True) 

class MembershipInstallments(CommonField):
    membership = models.ForeignKey(SaleRecordMembership, on_delete = models.SET_NULL, blank=True, null=True, related_name = 'installment_memberships')
    paid_installment = models.FloatField(blank=True, null=True)
    
    
# @receiver(post_save, sender = SaleRecordMembership)
# def installment_instance_create(sender, instance, created, **kwargs):
#     if instance.installment_months is not None:
#         # raise ValueError(f"installment_instance_create function is triggered for SaleRecordMembership instance with ID")
#         MembershipInstallments.objects.create(
#             membership=instance.id,
#             paid_installment=instance.price
#         )

# @receiver(post_save, sender=SaleRecordMembership)
# def create_membership_installments(sender, instance, created, **kwargs):
#     if created and instance.installment_months is not None:
#         # Create MembershipInstallments for each installment month
#         for _ in range(instance.installment_months):
#             MembershipInstallments.objects.create(
#                 membership=instance,
#                 paid_installment=0  # Or any default value you prefer
#             )

    
class PurchasedGiftCards(CommonField):
    sale_record = models.ForeignKey(SaleRecords, on_delete = models.SET_NULL, null = True, related_name = 'gift_cards_records')
    gift_card = models.ForeignKey(GiftCards, on_delete = models.SET_NULL, blank=True, null=True, related_name = 'sale_gift_cards_records')
    
    price = models.FloatField(default = 0)
    sale_code  = models.CharField(max_length = 150,blank=False, null=True)
    spend_amount = models.FloatField(default = 0)
    quantity = models.SmallIntegerField(default = 0)
    expiry = models.DateTimeField(blank=True, null=True)
    
class PaymentMethods(CommonField):
    sale_record = models.ForeignKey(SaleRecords, on_delete = models.SET_NULL, null = True, related_name = 'payment_methods_records')
    
    
    payment_method = models.CharField(max_length = 100 , null = True , blank = False)
    amount = models.FloatField(default  = 0 , blank= False)
    
    
    
class SaleTax(CommonField):
    
    sale_record = models.ForeignKey(SaleRecords, on_delete=models.CASCADE, blank=True, null=True, related_name='tax_records') 
    # Following are the Major Information for Tax Applied
    business_tax_id = models.ForeignKey(BusinessTax, on_delete=models.SET_NULL,  blank=False, null=True) # This will be Tax Instance ID 
    name = models.CharField(max_length=999, blank=False, null=False) 
    # tax_amount = models.FloatField(default=0, null= True, blank = True)  null = True, blank = True
    tax_rate = models.PositiveIntegerField(default = 0,blank=False, null=False) 
    value = models.FloatField(default = 0,blank=False, null=False)


    
class SaleRecordTip(CommonField):    
    sale_record = models.ForeignKey(SaleRecords, on_delete=models.CASCADE, null=True, blank=True,related_name='tip_records') 
    
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null = True, related_name='sale_record_employee_tips') 
    tip = models.FloatField(blank=False, null=False) 
    
# ====================================================== Appllied on checkout data ===========================================
    
class SaleRecordAppliedCoupons(CommonField):
    sale_record = models.ForeignKey(SaleRecords, on_delete = models.CASCADE, null = True, blank = True, related_name = 'applied_coupons_records')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL,null = True)
    refund_coupon = models.ForeignKey(RefundCoupon, on_delete=models.SET_NULL,null = True)
    client = models.ForeignKey(Client, on_delete = models.SET_NULL, blank=True, null=True, related_name = 'applied_coupons_client')
    
    coupon_type = models.CharField(max_length = 100, default = '', blank=False, null=False)
    coupon_discounted_price = models.FloatField(default =0, blank=False, null=False) 
    discount_percentage = models.FloatField(blank=True, null=True)
    # is_redeemed = models.BooleanField(default = False)
    
class AppliedMemberships(CommonField):
    sale_record = models.ForeignKey(SaleRecords, on_delete = models.CASCADE, null = True, blank = True, related_name = 'applied_memberships_records')
    membership = models.ForeignKey(SaleRecordMembership, on_delete = models.SET_NULL, blank=True, null=True)
    is_redeemed = models.BooleanField(default = False)
    price = models.FloatField(blank=True, null=True)
    discount_percentage = models.FloatField(blank=True, null=True)
    client = models.ForeignKey(Client, on_delete = models.SET_NULL, blank=True, null=True, related_name = 'applied_memberships_client')
    
    
class AppliedVouchers(CommonField):
    sale_record = models.ForeignKey(SaleRecords, on_delete = models.CASCADE, null = True, blank = True, related_name = 'applied_vouchers_records')
    # voucher = models.ForeignKey(Vouchers, on_delete = models.SET_NULL, blank=False, null=True)
    voucher = models.ForeignKey(SaleRecordVouchers, on_delete = models.SET_NULL , blank=False, null=True)
    is_redeemed = models.BooleanField(default = False)
    price = models.FloatField(blank=True, null=True)
    discount_percentage = models.FloatField(blank=True, null=True)
    client = models.ForeignKey(Client, on_delete = models.SET_NULL, blank=True, null=True, related_name = 'applied_vouchers_client')
    
class RedeemedLoyaltyPoints(CommonField):
    sale_record = models.ForeignKey(SaleRecords,  on_delete = models.CASCADE, null = True, blank = True, related_name = 'applied_loyalty_points_records')
    client_loyalty_point = models.ForeignKey(ClientLoyaltyPoint, on_delete = models.SET_NULL, blank=True, null=True, related_name = 'loyalty_points_records')
    redeemed_points = models.FloatField(default = 0.0 , blank=True, null=True)
    client = models.ForeignKey(Client, on_delete = models.SET_NULL, blank=True, null=True, related_name = 'applied_loyalty_points_client')
    
class AppliedGiftCards(CommonField):
    sale_record = models.ForeignKey(SaleRecords,  on_delete = models.CASCADE, null = True, blank = True, related_name = 'applied_gift_cards_records')
    # gift_card = models.ForeignKey(GiftCards, on_delete = models.SET_NULL, blank=True, null=True, related_name = 'sale_applied_gift_cards_records' )
    purchased_gift_card_id = models.ForeignKey(PurchasedGiftCards, on_delete = models.SET_NULL, blank=True, null=True, related_name = 'puchased_gift_card')
    partial_price = models.FloatField(blank=True, null=True)
    client = models.ForeignKey(Client, on_delete = models.SET_NULL, blank=True, null=True, related_name = 'applied_gift_cards_client')
    # discount_percentage = models.FloatField(blank=True, null=True)
    # is_redeemed = models.BooleanField(default = False)
    
    
    
class AppliedPromotion(CommonField):
    sale_record = models.ForeignKey(SaleRecords,  on_delete = models.CASCADE, null = True, blank = True, related_name = 'applied_promotions_records')
    # promotion = models.ForeignKey(Promotion, on_delete = models.SET_NULL,blank=True, null=True, related_name = "sale_record_promotions")
    promotion = models.CharField(max_length = 150 , blank=True, null=True)
    promotion_type = models.CharField(max_length = 255 , blank=True, null=True)
    # client = models.ForeignKey(Client, on_delete = models.SET_NULL, blank=True, null=True, related_name = 'applied_promotion_client')
    
    