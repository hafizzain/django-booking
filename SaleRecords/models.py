# from django.db import models
# from uuid import uuid4
# from Authentication.models import User
# from Utility.models import CommonField
# from SaleRecords.choices import *

# from Business.models import BusinessAddress
# from Promotions.models import Coupon
# from Product.models import Product
# from Service.models import Service
# from Employee.models import Employee
# from Promotions.models import Coupon
# from Client.models import Client, Membership, Promotion, Rewards, Vouchers, LoyaltyPointLogs
# from Finance.models import Refund
# from Order.models import Checkout
# from Appointment.models import AppointmentCheckout, AppointmentEmployeeTip
# from Invoices.models import SaleInvoice

# from Business.models import BusinessTax




# class SaleRecords(CommonField):
    
#     coupon_discounted_price = models.FloatField(null=True) 
#     coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True, blank=True) 
#     is_coupon_redeemed = models.TextField(null=True) 
#     tip = models.FloatField(default=0, null=True, blank=True) 
#     is_refund = models.CharField(max_length=50, null=True, blank=True) 

#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_checkout_order', null=True, blank=True) 
#     member = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='member_checkout_orders', null=True, blank=True) 
#     business_address = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointment_address_tips') 

#     checkout_type = models.CharField(choices = CheckoutType.choices, max_length = 50, null=True) 
#     checkout = models.ForeignKey(Checkout, on_delete=models.CASCADE, related_name='sale_orders_checkout', null=True, blank=True) 
#     appointment_checkout = models.ForeignKey(AppointmentCheckout, on_delete=models.CASCADE, related_name='appointment_orders_checkout', null=True, blank=True) 

#     client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_checkout_orders', null=True, blank=True) 
#     client_type = models.CharField(choices=ClientTypeChoices.choices, max_length=50, default='')
#     payment_method = models.CharField(choices=PaymentMethods.choices, max_length=50, default='')
    
#     invoice = models.ForeignKey(SaleInvoice, on_delete = models.SET_NULL, null= True)

#     refunds_data = models.ForeignKey(Refund, on_delete = models.CASCADE, null= True, blank= True, related_name = 'refunds')
#     coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True, blank=True) 
    

#     total_discount = models.FloatField(default=None, null=True, blank=True) 
#     voucher_redeem_percentage = models.FloatField(default=None, null=True, blank=True) 
#     redeem_option = models.CharField(max_length=250, default=None, null=True, blank=True)

#     is_promotion = models.BooleanField(default=False) 
#     selected_promotion_id = models.CharField(default='', max_length=800) 
#     selected_promotion_type = models.CharField(default='', max_length=400) 
#     status = models.CharField(max_length=100, default='Active') 
#     sub_total = models.DecimalField(max_digit = 10, decimal_places = 2) 

#     coupon_discounted_price = models.FloatField(null=True)  
#     is_coupon_redeemed = models.TextField(null=True) 
#     tip = models.FloatField(default=0, null=True, blank=True) 
#     is_refund = models.CharField(max_length=50, null=True, blank=True) 
#     checkout_type = models.CharField(choices = CheckoutType.choices, max_length = 50, null=True) 
#     # Fields specific to AppointmentCheckout
#     payment_method = models.CharField(max_length=100, null=True, blank=True) 
#     # payment_methods = models.
    
    
#     service_price = models.FloatField(default=0, null=True, blank=True) 
#     total_price = models.FloatField(default=0, null=True, blank=True) 


#     # Fields specific to Checkout
#     client_type = models.CharField(choices=ClientTypeChoices.choices, max_length=50, default='') 
#     payment_type = models.CharField(choices=PaymentMethods.choices, max_length=50, default='') 

#     class Meta:
#         verbose_name_plural = 'Sale Records'


# class SaleTax(models.Model):
#     # self.id is a seperate field 
    
#     sale_order = models.ForeignKey(SaleRecords, on_delete=models.CASCADE, related_name='sale_taxs') 

#     # Following are the Major Information for Tax Applied
#     tax_id = models.ForeignKey(BusinessTax, on_delete=models.SET_NULL, null=True) # This will be Tax Instance ID 
#     tax_name = models.CharField(max_length=999, default='') 
#     tax_amount = models.FloatField(default=0) 
#     tax_percentage = models.FloatField(default=0) 

#     def __str__(self):
#         return self.tax_name

# class SaleOrderTip(models.Model):    

#     id = models.UUIDField(default=uuid4, unique=True, primary_key=True, editable=False) 
#     member = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_checkout_tips', null=True, blank=True) 
#     sale_order = models.ForeignKey(SaleRecords, on_delete=models.CASCADE, related_name='sale_order_tips') 
#     tip = models.FloatField(default=0, null=True, blank=True) 

#     created_at = models.DateTimeField(auto_now_add=True) 
    
#     def __str__(self): 
#         return str(self.id) 



# class SaleOrderItem(models.Model): 

#     ITEM_TYPE_CHOICES = ( 
#         ('Product', 'Product'), 
#         ('Service', 'Service'), 
#     ) 

#     id = models.UUIDField(default=uuid4, unique=True, primary_key=True, editable=False) 
#     sale_order = models.ForeignKey(SaleRecords, on_delete=models.CASCADE, related_name='sale_order_items') 

#     checkout_type = models.CharField(choices = CheckoutType.choices, max_length = 50, null=True) 
#     item_type = models.CharField(max_length=100, choices=ITEM_TYPE_CHOICES, default='Product') 
#     item_id = models.CharField(max_length=999, default='') # This will be either Product Id, Service Id, Appointment Id 

#     item_primary_name = models.CharField(max_length=999, default='') 
#     item_secondary_name = models.CharField(max_length=999, default='') 

#     quantity = models.IntegerField(default=0) 
#     price = models.FloatField(default=0) 
#     discount = models.FloatField(default=0) 

#     total = models.FloatField(default=0) 