from django.db import models

from uuid import uuid4
from Authentication.models import User
from Business.models import Business

from Utility.models import Country, State, City
from django.utils.timezone import now
from Product.models import Product

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
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_subscription')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_subscription')
    
    name = models.CharField(max_length=300, default='')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product')
    no_days = models.PositiveIntegerField(default=0)
    select_amount = models.CharField(max_length=100, default='')
    total_no_services = models.PositiveIntegerField(default=0)
    set_price = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return str(self.id)