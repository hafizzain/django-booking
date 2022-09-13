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

    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_subscriptions')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_subscriptions')
    
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='product_subscriptions')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_subscriptions')

    name = models.CharField(max_length=300, default='')
    days = models.PositiveIntegerField(default=0, verbose_name='Number of Days')
    select_amount = models.CharField(max_length=100, default='Limited', choices=AMOUNT_CHOICES)
    services_count = models.PositiveIntegerField(default=0, verbose_name='Total Number of Services')
    price = models.PositiveIntegerField(default=0, verbose_name='Subscription Price')

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)
    


# class Promotion(models.Model):
#     id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_subscriptions')
#     business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_subscriptions')

#     product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='product_subscriptions')
#     service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_subscriptions')


#     is_deleted = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=now)
#     def __str__(self):
#         return str(self.id)
    
# class Rewards(models.Model):
#     id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_reward', verbose_name='Creator ( User )')
#     business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_reward')
    
#     name = models.CharField(max_length=100, default='')
#     service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_reward')
    
    
#     is_active = models.BooleanField(default=True)
#     is_deleted = models.BooleanField(default=False)
#     is_blocked = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=now)

#     def __str__(self):
#         return str(self.id)

# class Membership(models.Model):
#     id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client')
#     business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_client')
    
#     name =  models.CharField(max_length=100, default='')
#     description =  models.CharField(max_length=300, null=True, blank=True)
    
    
#     is_deleted = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=False)
#     is_blocked = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=now)
#     updated_at = models.DateTimeField(null=True, blank=True)

#     def __str__(self):
#         return str(self.id)