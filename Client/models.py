from datetime import timezone
from datetime import datetime

from itertools import count
from django.db import models

from uuid import uuid4
from Authentication.models import User
from Business.models import Business, BusinessAddress
#from Promotions.models import ComplimentaryDiscount

from Utility.models import Country, Currency, Language, State, City
from django.utils.timezone import now
from Product.models import Product
from Service.models import Service
import uuid

class Client(models.Model):
    GENDER_CHOICES = [
        ('Male' , 'Male'),
        ('Female' , 'Female'),
        ('Others' , 'Others'),
    ]
    MARKETING_CHOICES = [
        ('opt_in' , 'opt_in'),
        ('opt_out' , 'opt_out'),
    ]
    ABOUT_CHOICES = [
        ('Facebook' , 'Facebook'),
        ('Instagram' , 'Instagram'),
        ('Twitter' , 'Twitter'),
        ('Whatsapp' , 'Whatsapp'),
        ('Community' , 'Community'),
        ('Media_Ads' , 'Media Ads'),
        ('Friends' , 'Friends'),
    ]
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client' , null=True, blank=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_client')
    
    #business_addess = models.ForeignKey(BusinessAddress, on_delete=models.CASCADE,  null=True, blank=True,  related_name='business_addess_client')

    full_name = models.CharField(max_length=300, default='')
    image = models.ImageField(upload_to='client/client_images/', null=True, blank=True)
    client_id = models.CharField(max_length=50, default='')
    email = models.EmailField(default='')
    mobile_number = models.CharField(max_length=30, null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    is_mobile_verified = models.BooleanField(default=False)
    
    dob = models.DateField(verbose_name='Date of Birth', null=True, blank=True)
    gender = models.CharField(choices=GENDER_CHOICES, default='Male', max_length=20)

    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='country_clients')
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, related_name='state_clients')
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='city_clients')
    
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, related_name='language_clients', null=True, blank=True, max_length=100)
    
    about_us = models.CharField(choices=ABOUT_CHOICES, default='Community', max_length=100)
    marketing = models.CharField(choices=MARKETING_CHOICES, default='opt_in', max_length=50)
    customer_note = models.CharField(max_length=255, null=True, blank=True, verbose_name= 'Customer Note')
    
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(default='')
    card_number = models.CharField(max_length=30, null=True, blank=True)
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
    
    
class ClientGroup(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_client_group')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_client_group')
    
    email = models.EmailField(default='', null=True, blank=True)
    name = models.CharField(max_length=300, default='')
    
    client = models.ManyToManyField(Client, related_name='group_clients')

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)
    
    
class Subscription(models.Model):

    AMOUNT_CHOICES = [
        ('Limited', 'Limited'),
        ('Unlimited', 'Unlimited'),
    ]
    SUBSCRIPTION_TYPES = [
        ('Product' , 'Product'),
        ('Service' , 'Service'),
    ]

    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_subscriptions')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_subscriptions')
    
    subscription_type = models.CharField(default='Product', choices=SUBSCRIPTION_TYPES, max_length=20)
    
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='product_subscriptions')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_subscriptions')

    name = models.CharField(max_length=300, default='')
    days = models.PositiveIntegerField(default=0, verbose_name='Number of Days')
    select_amount = models.PositiveIntegerField(default=0)
    services_count = models.PositiveIntegerField(default=0, verbose_name='Total Number of Services')
    products_count = models.PositiveIntegerField(default=0, verbose_name='Total Number of Products')
    price = models.PositiveIntegerField(default=0, verbose_name='Subscription Price')

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)

class Promotion(models.Model):
    VALIDITY_DAY=[
        ('7 Days' , '7 Days'),
        ('14 Days' , '14 Days'),
        ('1 Month' ,  '1 Months'),
        ('2 Months' , '2 Months'),
        ('3 Months' , '3 Months'),
        ('4 Months' , '4 Months'),
        ('6 Months' , '6 Months'),
        ('8 Months' , '8 Months'),
        ('1 Years' , '1 Years'),
        ('18 Months' , '18 Months'),
        ('2 Years' , '2 Years'),
        ('5 Years' , '5 Years'),
    ]
    PROMOTION_TYPES = [
        ('Product' , 'Product'),
        ('Service' , 'Service'),
    ]

    DISCOUNT_DURATION = [
        ('Day' , 'Day'),
        ('Month' , 'Month'),
    ]

    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_promotions')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_promotions')

    name = models.CharField(max_length=100, default='', verbose_name='Promotion Name')
    promotion_type = models.CharField(default='Service', choices=PROMOTION_TYPES, max_length=20)

    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_promotions')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='product_promotions')
    
    purchases  = models.PositiveIntegerField(verbose_name='No. of Purchases', default=0, null=True, blank=True)

    discount = models.PositiveIntegerField(default=0)
    
    valid_til= models.CharField(choices=VALIDITY_DAY, default='7 Days', null = True, blank=  True ,verbose_name='No of Days/Month', max_length = 100)

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)


    def __str__(self):
        return str(self.id)

class Vouchers(models.Model):
    VALIDITY_CHOICE = [
        ('Days' , 'Days'),
        ('Months' , 'Months'),
    ]
    VOUCHER_CHOICES =[
        ('Product' , 'Product'),
        ('Service' , 'Service'),
    ]
    VALIDITY_DAY=[
        ('7 Days' , '7 Days'),
        ('14 Days' , '14 Days'),
        ('1 Months' ,  '1 Months'),
        ('2 Months' , '2 Months'),
        ('3 Months' , '3 Months'),
        ('4 Months' , '4 Months'),
        ('6 Months' , '6 Months'),
        ('8 Months' , '8 Months'),
        ('1 Years' , '1 Years'),
        ('18 Months' , '18 Months'),
        ('2 Years' , '2 Years'),
        ('5 Years' , '5 Years'),
    ]
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_voucher', verbose_name='Creator ( User )')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_voucher')
    
    name = models.CharField(max_length=100, default='')
    #value = models.PositiveIntegerField(default=0)
    
    voucher_type = models.CharField(choices= VOUCHER_CHOICES,default= 'Product', verbose_name = 'Voucher Type', max_length=20)
    # service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_voucher')
    # product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='product_voucher')
    
    #valid_for = models.CharField(choices=VALIDITY_CHOICE, default='Months' , verbose_name='Validity for Days or Months', max_length=20)

    # days = models.PositiveIntegerField(default=0, verbose_name='No. of Days', null=True, blank=True)
    # months = models.PositiveIntegerField(default=0, verbose_name='No. of Months', null=True, blank=True)
    #validity = models.PositiveIntegerField(default=0, verbose_name='No of Days/Month')
    validity = models.CharField(choices=VALIDITY_DAY, default='7 Days' ,verbose_name='No of Days/Month', max_length = 100)
    
    
    sales = models.PositiveIntegerField(default=0)
    price = models.PositiveIntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)

class Rewards(models.Model):

    REWARD_TYPES = [
        ('Product' , 'Product'),
        ('Service' , 'Service'),
    ]
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_reward', verbose_name='Creator ( User )')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_reward')
    
    name = models.CharField(max_length=100, default='')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_rewards')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='product_rewards')

    reward_value = models.PositiveIntegerField(default=0)
    reward_point = models.PositiveIntegerField(default=0)
    reward_type =  models.CharField(default='Product', choices=REWARD_TYPES, max_length=20)

    total_points = models.PositiveIntegerField(default=0)
    discount = models.PositiveIntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)

class Membership(models.Model):
    MEMBERSHIP_CHOICES =[
        ('Product' , 'Product'),
        ('Service' , 'Service'),
    ]
    VALIDITY_CHOICE = [
        ('7 Days' , '7 Days'),
        ('14 Days' , '14 Days'),
        ('1 Months' ,  '1 Months'),
        ('2 Months' , '2 Months'),
        ('3 Months' , '3 Months'),
        ('4 Months' , '4 Months'),
        ('6 Months' , '6 Months'),
        ('8 Months' , '8 Months'),
        ('1 Years' , '1 Years'),
        ('18 Months' , '18 Months'),
        ('2 Years' , '2 Years'),
        ('5 Years' , '5 Years'),
    ]
    DISCOUNT_CHOICE = [
        ('Limited' , 'Limited'),
        ('Free' , 'Free'),
    ]

    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_memberships')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_memberships')
    
    name =  models.CharField(max_length=100, default='')
    description =  models.CharField(max_length=300, null=True, blank=True)
    #membership = models.CharField(default='Product', choices=MEMBERSHIP_CHOICES, max_length=30, verbose_name = 'Membership_type')
    
    # service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_memberships')
    # product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='product_memberships')
    
    percentage = models.PositiveIntegerField(default=0)
    
    #total_number = models.PositiveIntegerField(default=0, null=True, blank=True)
    valid_for = models.CharField(choices=VALIDITY_CHOICE, default='7 Days' , verbose_name='Validity for Days or Months', max_length=20)
    discount = models.CharField(choices=DISCOUNT_CHOICE, default='Unlimited' , verbose_name='Discount Limit', max_length=20)
    
    #validity = models.PositiveIntegerField(default=0, verbose_name='No. of Validity Days/Month', null=True, blank=True)
    
    #color =  models.CharField(max_length=100, default='')
    term_condition =  models.CharField(max_length=300, null=True, blank=True)

    
    #price = models.PositiveIntegerField(default=0)
    #tax_rate = models.PositiveIntegerField(default=0)

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
    
class DiscountMembership(models.Model):
    DURATION_CHOICE=[
        ('7 Days', '7 Days'),
        ('14 Days', '14 Days'),
        ('1 Month', '1 Month'),
    ]
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='membership_discountmembership')
    duration = models.CharField(choices=DURATION_CHOICE, default='7 Days' , verbose_name='Duration', max_length=50, null=True, blank=True,)
    percentage = models.PositiveIntegerField(default=0)

    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_memberships')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='product_memberships')
    
    def __str__(self):
        return str(self.id)
class CurrencyPriceMembership(models.Model):
    
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='membership_currenypricemembership')
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.id)
    
#now = datetime.now()
class LoyaltyPoints(models.Model):
    
    LOYALTY_CHOICE = [
        ('Service', 'Service'),
        ('Retail', 'Retail'),
        ('Both', 'Both'),
        
    ]
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='user_loyalty', verbose_name='Creator ( User )')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_loyalty')
    location = models.ForeignKey(BusinessAddress, on_delete=models.CASCADE, related_name='location_loyaltypoints', null=True, blank=True)
    
    name = models.CharField(max_length=100, default='')
    loyaltytype = models.CharField(choices=LOYALTY_CHOICE, default='Service' , verbose_name='Loyalty Type', max_length=50)
    amount_spend = models.PositiveIntegerField(default=0, null=True, blank=True)
    number_points = models.PositiveIntegerField(default=0, null=True, blank=True)
    earn_points = models.PositiveIntegerField(default=0, null=True, blank=True)
    total_earn_from_points = models.PositiveIntegerField(default=0, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now, null=True) #null = True, default= datetime.now() )
    
    def __str__(self):
        return str(self.id)
class ClientPromotions(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='user_client_promotions', verbose_name='Creator ( User )')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_client_promotions')
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True, related_name='client_client_promotions')
    complimentary = models.ForeignKey('Promotions.ComplimentaryDiscount', on_delete=models.SET_NULL, null=True, blank=True, related_name='complimentry_client_promotions')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True, related_name='service_client_promotions')    

    visits = models.PositiveIntegerField(default=0, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now, null=True) 
    
    def __str__(self):
        return str(self.id)
    
class ClientPackageValidation(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='user_client_packagevalidation', verbose_name='Creator ( User )')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_client_packagevalidation')
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True, related_name='client_client_packagevalidation')
    package = models.ForeignKey('Promotions.PackagesDiscount', on_delete=models.SET_NULL, null=True, blank=True, related_name='package_client_packagevalidation')
    serviceduration = models.ForeignKey('Promotions.ServiceDurationForSpecificTime', on_delete=models.SET_NULL, null=True, blank=True, related_name='serviceduration_client_packagevalidation')
    service = models.ManyToManyField(Service, related_name='service_client_packagevalidation') 

    #month = models.PositiveIntegerField(default=0, null=True, blank=True)
    
    due_date = models.DateField(null=True) 
    
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now, null=True) 
    
    def __str__(self):
        return str(self.id)