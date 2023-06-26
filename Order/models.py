from email.policy import default
from uuid import uuid4
from django.db import models
from Authentication.models import User
from Business.models import BusinessAddress
from Client.models import Client, Membership, Promotion, Rewards, Vouchers
from Promotions.models import PurchaseDiscount, SpendSomeAmount, FixedPriceService, MentionedNumberService, BundleFixed, RetailAndGetService
from django.utils.timezone import now
from Employee.models import Employee
from Product.models import Product, CurrencyRetailPrice
from Service.models import Service, PriceService

# Create your models here.
class Checkout(models.Model):
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_checkout_order', null=True, blank=True)

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_checkout_orders', null=True, blank=True)
    location = models.ForeignKey(BusinessAddress, on_delete=models.CASCADE, related_name='location_checkout_orders', null=True, blank=True)
    member = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='member_checkout_orders', null=True)
    client_type = models.CharField(choices = CLIENT_TYPE, max_length=50 , default = '' )
    payment_type = models.CharField(choices = PAYMENT_TYPE, max_length=50 , default = '' )
    
    tip = models.PositiveBigIntegerField(default = 0)

    tax_applied = models.FloatField(default=0, verbose_name='Tax Applied in Percentage')
    tax_amount = models.FloatField(default=0, verbose_name='Tax total amount')
    
    total_service_price = models.PositiveBigIntegerField(default = 0 , null=True, blank=True)
    total_product_price = models.PositiveBigIntegerField(default = 0 , null=True, blank=True)
    total_voucher_price = models.PositiveBigIntegerField(default = 0 , null=True, blank=True)
    total_membership_price = models.PositiveBigIntegerField(default = 0 , null=True, blank=True)
    
    service_commission = models.PositiveBigIntegerField(default = 0 , null=True, blank=True)
    product_commission = models.PositiveBigIntegerField(default = 0 , null=True, blank=True)
    voucher_commission = models.PositiveBigIntegerField(default = 0 , null=True, blank=True)
    
    service_commission_type = models.CharField( max_length=50 , default = '')
    product_commission_type = models.CharField( max_length=50 , default = '')
    voucher_commission_type = models.CharField( max_length=50 , default = '')
    
    is_promotion = models.BooleanField(default=False)
    selected_promotion_id = models.CharField(default='', max_length=800)
    selected_promotion_type = models.CharField(default='', max_length=400)
    """
        Direct Or Flat
        Specific Group Discount
        Purchase Discount
        Specific Brand Discount
        Spend_Some_Amount
        Fixed_Price_Service
        Mentioned_Number_Service
        Bundle_Fixed_Service
        Retail_and_Get_Service
        User_Restricted_discount
        Complimentary_Discount
        Packages_Discount
    """
    status =  models.CharField(choices=status_choice, max_length=100, default='Active')
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return str(self.id)
    

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
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_orders', null=True, blank=True)
    location = models.ForeignKey(BusinessAddress, on_delete=models.CASCADE, related_name='location_orders', null=True, blank=True)
    member = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='member_orders', null=True, blank=True)
    
    checkout = models.ForeignKey(Checkout, on_delete=models.CASCADE, related_name='checkout_orders', null=True, blank=True)
    
    duration = models.CharField(max_length=50, choices=DURATION_CHOICES , default = '' )
    client_type = models.CharField(choices = CLIENT_TYPE, max_length=50 , default = '' )
    payment_type = models.CharField(choices = PAYMENT_TYPE, max_length=50 , default = '' )
    #sale_type = models.CharField(choices = SALE_CHOICE, max_length=50 , default = '' )
    
    #voucher =models.ForeignKey(Vouchers, on_delete=models.CASCADE, related_name='checkout_voucher_orders', null=True, blank=True) 
    promotion =models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='checkout_promotion_orders', null=True, blank=True) 
    #membership =models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='checkout_membership_orders', null=True, blank=True) 
    rewards =models.ForeignKey(Rewards, on_delete=models.CASCADE, related_name='checkout_reward_orders', null=True, blank=True) 
    
    quantity = models.PositiveBigIntegerField(default= 0)
    
    current_price =models.PositiveBigIntegerField(default = 0)
    tip =models.PositiveBigIntegerField(default = 0)
    gst = models.PositiveBigIntegerField(default = 0)
    total_price = models.DecimalField(default = 0 , max_digits=10, decimal_places=5)
    sold_quantity = models.PositiveBigIntegerField(default = 0)
    
    discount_percentage = models.FloatField(default= 0)
    discount_price = models.FloatField(default= 0)
    price = models.PositiveBigIntegerField(default= 0)

    is_redeemed = models.BooleanField(default=False)
    redeemed_type = models.CharField(default='', max_length=300)
    redeemed_price = models.FloatField(default=0)
    redeemed_instance_id = models.CharField(default='', max_length=800)
    
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

    def save(self, *args, **kwargs):
        if self.checkout and self.checkout.selected_promotion_type:
            promotions_types = {
                'Purchase Discount' : PurchaseDiscount,
                'Spend_Some_Amount' : SpendSomeAmount,
                'Fixed_Price_Service' : FixedPriceService,
                'Mentioned_Number_Service' : MentionedNumberService,
                'Bundle_Fixed_Service' : BundleFixed,
                'Retail_and_Get_Service' : RetailAndGetService,

                # 'directFlat' : None,
                # 'specificCategoryGroup' : None,
                # 'specificBrandServiceGroup' : None,
                # 'userRestricted' : None,
                # 'complimentaryVoucher' : None,
                # 'packages' : None,
            }

            promotion_type = promotions_types.get(self.checkout.selected_promotion_type, None)
            if promotion_type is not None:
                try:
                    selected_location = self.location
                    currency = selected_location.currency
                except:
                    pass
                else:
                    retail_prices = CurrencyRetailPrice.objects.filter(
                        product = self.product,
                        currency = currency
                    )
                    if len(retail_prices) > 0:
                        retail_price = retail_prices[0]
                        original_price = retail_price

                        self.discount_price = self.total_price
                        self.total_price = original_price
                        self.price = self.total_price
                        self.discount_percentage = (self.discount_price / self.total_price) * 100

        super(ProductOrder, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.id)
    

class ServiceOrder(Order):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='service_orders')

    def save(self, *args, **kwargs):
        if self.checkout and self.checkout.selected_promotion_type:
            promotions_types = {
                'Purchase Discount' : PurchaseDiscount,
                'Spend_Some_Amount' : SpendSomeAmount,
                'Fixed_Price_Service' : FixedPriceService,
                'Mentioned_Number_Service' : MentionedNumberService,
                'Bundle_Fixed_Service' : BundleFixed,
                'Retail_and_Get_Service' : RetailAndGetService,


                # 'directFlat' : None,
                # 'specificCategoryGroup' : None,
                # 'specificBrandServiceGroup' : None,
                # 'userRestricted' : None,
                # 'complimentaryVoucher' : None,
                # 'packages' : None,
            }

            promotion_type = promotions_types.get(self.checkout.selected_promotion_type, None)
            if promotion_type is not None:
                try:
                    selected_location = self.location
                    currency = selected_location.currency
                except:
                    pass
                else:
                    prices = PriceService.objects.filter(
                        service = self.service,
                        currency = currency,
                        duration = self.duration
                    )
                    if len(prices) > 0:
                        retail_price = prices[0]
                        original_price = retail_price

                        self.discount_price = self.total_price
                        self.total_price = original_price
                        self.price = self.total_price
                        self.discount_percentage = (self.discount_price / self.total_price) * 100

        super(ServiceOrder, self).save(*args, **kwargs)
    
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
    

class CheckoutPayment(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True,)
    checkout = models.ForeignKey(Checkout, on_delete=models.CASCADE, related_name='checkout_paymentmethod')
    
    def __str__(self):
        return str(self.id)
    
class RedeemedMemberShip(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True,)

    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, related_name='order_redeemed_memberships')
    checkout = models.ForeignKey(Checkout, on_delete=models.CASCADE, null=True, blank=True, related_name='checkout_redeemed_memberships')

    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='redeemed_memberships')

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    
    def __str__(self):
        return str(self.id)

class RedeemMembershipItem(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True,)

    redeemed_membership = models.ForeignKey(RedeemedMemberShip, on_delete=models.CASCADE, related_name='redeem_items')

    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='redeemed_products')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='redeemed_services')

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    
    def __str__(self):
        return str(self.id)
