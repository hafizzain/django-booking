from django.db import models

from uuid import uuid4
from Authentication.models import User
from Business.models import Business

from Utility.models import Country, State, City
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
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_client')

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
    select_amount = models.CharField(max_length=100, default='Limited', choices=AMOUNT_CHOICES)
    services_count = models.PositiveIntegerField(default=0, verbose_name='Total Number of Services')
    products_count = models.PositiveIntegerField(default=0, verbose_name='Total Number of Products')
    price = models.PositiveIntegerField(default=0, verbose_name='Subscription Price')

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)
    


class Promotion(models.Model):
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

    #name = models.CharField(max_length=100, default='')
    promotion_type = models.CharField(default='Service', choices=PROMOTION_TYPES, max_length=20)

    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_promotions')
    services = models.PositiveIntegerField(verbose_name='No. of Services', default=0, null=True, blank=True)

    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='product_promotions')
    products = models.PositiveIntegerField(verbose_name='No. of Products', default=0, null=True, blank=True)

    discount_service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='discount_service_promotions')
    discount_product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='discount_product_promotions')

    discount = models.PositiveIntegerField(default=0)

    duration = models.CharField(default='Month', choices=DISCOUNT_DURATION, max_length=20)

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
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_voucher', verbose_name='Creator ( User )')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_voucher')
    
    name = models.CharField(max_length=100, default='')
    value = models.PositiveIntegerField(default=0)
    
    voucher_type = models.CharField(choices= VOUCHER_CHOICES,default= 'Product', verbose_name = 'Voucher Type', max_length=20)
    # service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_voucher')
    # product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='product_voucher')
    
    valid_for = models.CharField(choices=VALIDITY_CHOICE, default='Months' , verbose_name='Validity for Days or Months', max_length=20)

    days = models.PositiveIntegerField(default=0, verbose_name='No. of Days', null=True, blank=True)
    months = models.PositiveIntegerField(default=0, verbose_name='No. of Months', null=True, blank=True)
    
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

    VALIDITY_CHOICE = [
        ('Days' , 'Days'),
        ('Months' , 'Months'),
    ]

    COLOR_CHOICES = [
        ('Red', 'Red'),
        ('Purple', 'Purple'),
        ('Black', 'Black'),
        ('White', 'White'),
        ('Yellow', 'Yellow'),
        ('Orange', 'Orange'),
        ('Pink', 'Pink'),
        ('Gray', 'Gray'),
        ('DarkGray', 'DarkGray'),
        ('Blue', 'Blue'),
        ('Golden', 'Golden'),
        ('Green', 'Green'),
        ('Brown', 'Brown'),
        ('SkyBlue', 'SkyBlue'),
        ('DarkBlue', 'DarkBlue'),
    ]
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_memberships')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_memberships')
    
    name =  models.CharField(max_length=100, default='')
    description =  models.CharField(max_length=300, null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_memberships')
    session = models.PositiveIntegerField(default=0)

    valid_for = models.CharField(choices=VALIDITY_CHOICE, default='Months' , verbose_name='Validity for Days or Months', max_length=20)

    days = models.PositiveIntegerField(default=0, verbose_name='No. of Days', null=True, blank=True)
    months = models.PositiveIntegerField(default=0, verbose_name='No. of Months', null=True, blank=True)

    price = models.PositiveIntegerField(default=0)
    tax_rate = models.PositiveIntegerField(default=0)

    color = models.CharField(default='White', choices=COLOR_CHOICES, max_length=30)
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)