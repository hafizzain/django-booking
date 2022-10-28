from email.policy import default
from uuid import uuid4
from django.db import models
from Authentication.models import User
from Business.models import BusinessAddress
from Client.models import Client, Membership, Promotion, Rewards, Vouchers
from django.utils.timezone import now
from Employee.models import Employee
from Product.models import Product
from Service.models import Service

# Create your models here.


class Order(models.Model):    
    DURATION_CHOICES=[
        ('30_Min' , '30 Min'),
        ('60_Min' , '60 Min'),
        ('90_Min' , '90 Min'),
        ('120_Min' , '120 Min'),
        ('150_Min' , '150 Min'),
        ('180_Min' , '180 Min'),
        ('210_Min' , '210 Min'),
    ]
    status_choice=[
        ('Completed', 'Completed'),
        ('Incompleted', 'Incompleted'),
        ('Expired', 'Expired'),
        ('Active', 'Active'),        
    ]
    # SALE_CHOICE=[
    #     ('Product', 'Product'),
    #     ('Service', 'Incompleted'),
    #     ('Expired', 'Expired'),
    #     ('Active', 'Active'),        
    # ]
    
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

    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True,)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_sale_order', null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_orders')
    location = models.ForeignKey(BusinessAddress, on_delete=models.CASCADE, related_name='location_orders', null=True, blank=True)
    member = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='member_orders')
    
    duration = models.CharField(max_length=50, choices=DURATION_CHOICES , default = '' )
    client_type = models.CharField(choices = CLIENT_TYPE, max_length=50 , default = '' )
    payment_type = models.CharField(choices = PAYMENT_TYPE, max_length=50 , default = '' )
    #sale_type = models.CharField(choices = SALE_CHOICE, max_length=50 , default = '' )
    
    #voucher =models.ForeignKey(Vouchers, on_delete=models.CASCADE, related_name='checkout_voucher_orders', null=True, blank=True) 
    promotion =models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='checkout_promotion_orders', null=True, blank=True) 
    #membership =models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='checkout_membership_orders', null=True, blank=True) 
    rewards =models.ForeignKey(Rewards, on_delete=models.CASCADE, related_name='checkout_reward_orders', null=True, blank=True) 
    
    current_price =models.PositiveBigIntegerField(default = 0)
    tip =models.PositiveBigIntegerField(default = 0)
    gst = models.PositiveBigIntegerField(default = 0)
    total_price = models.PositiveBigIntegerField(default = 0)
    
    
    status =  models.CharField(choices=status_choice, max_length=100, default='Active')
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return str(self.id)
    

class ProductOrder(Order):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_orders')
    
    def __str__(self):
        return str(self.id)
    

class ServiceOrder(Order):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='service_orders')
    
    def __str__(self):
        return str(self.id)

class MemberShipOrder(Order):
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='membership_orders')

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    
    def __str__(self):
        return str(self.id)
    

class VoucherOrder(Order):
    voucher = models.ForeignKey(Vouchers, on_delete=models.CASCADE, related_name='voucher_orders')
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    
    def __str__(self):
        return str(self.id)
    