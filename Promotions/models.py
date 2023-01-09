import uuid
from django.db import models
from django.utils.timezone import now
from Authentication.models import User
from Business.models import Business, BusinessAddress

from Product.models import Product
from Service.models import Service


# Create your models here.
class DirectOrFlatDiscount(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='directorflatdiscount')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_directorflatdiscount')
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
class CategoryDiscount(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    directorflat = models.ForeignKey(DirectOrFlatDiscount, on_delete=models.CASCADE, related_name='directorflat_categorydiscount')

    all_category = models.PositiveIntegerField(default=0, blank= True, null=True,)
    
    service_discount = models.PositiveIntegerField(default=0, blank= True, null=True,)
    retail_discount = models.PositiveIntegerField(default=0, blank= True, null=True,)
    voucher_discount = models.PositiveIntegerField(default=0, blank= True, null=True,)
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.id)
    
class DateRestrictions(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    directorflat = models.ForeignKey(DirectOrFlatDiscount, on_delete=models.CASCADE, related_name='directorflat_daterestrictions')
    business_address = models.ManyToManyField(BusinessAddress, null=True, blank=True, related_name='business_address_daterestrictions')
    
    start_date = models.DateField(verbose_name = 'Start Date', null=True)
    end_date = models.DateField(verbose_name = 'End Date', null=True)
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.id)
    
class DayRestrictions(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    directorflat = models.ForeignKey(DirectOrFlatDiscount, on_delete=models.CASCADE, related_name='directorflat_dayrestrictions')
    
    day = models.CharField(max_length=20, null=True, blank=True)
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.id)
    
class BlockDate(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    directorflat = models.ForeignKey(DirectOrFlatDiscount, on_delete=models.CASCADE, related_name='directorflat_blockdate')
    
    date = models.DateField(verbose_name = 'Block Date', null=True)
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.id)