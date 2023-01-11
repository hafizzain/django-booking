import uuid
from django.db import models
from django.utils.timezone import now
from Authentication.models import User
from Business.models import Business, BusinessAddress

from Product.models import Product
from Service.models import Service, ServiceGroup


# Create your models here.
class SpecificGroupDiscount(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_specificgroup_discount')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='businessgroup_specific_discount')
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
    
class ServiceGroupDiscount(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    specificgroupdiscount = models.ForeignKey(SpecificGroupDiscount, on_delete=models.CASCADE, related_name='servicegroupdiscount_specificgroupdiscount')
    
    servicegroup = models.ForeignKey(ServiceGroup, on_delete=models.CASCADE, related_name='servicegroup_specificgroupdiscount')
    discount = models.PositiveIntegerField(default=0, blank= True, null=True)
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.id) 
    
class PurchaseDiscount(models.Model):
    TYPE_CHOICES = [
        ('Service', 'Service'),
        ('Product', 'Product'),
    ]
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_purchase_discount')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_purchase_discount')
    
    select_type= models.CharField(choices=TYPE_CHOICES, max_length=50, null=True, blank=True, default = 'Product')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_purchase_discount')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='service_purchase_discount')
    
    purchase = models.PositiveIntegerField(default=0, blank= True, null=True)
    
    discount_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='discountproduct_purchase_discount')
    discount_service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='discountservice_purchase_discount')
    
    discount_value = models.PositiveIntegerField(default=0, blank= True, null=True)
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)

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
    TYPE_CHOICES = [
        ('All', 'All'),
        ('Service', 'Service'),
        ('Retail', 'Retail'),
        ('Voucher', 'Voucher'),
    ]
    
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    directorflat = models.ForeignKey(DirectOrFlatDiscount, on_delete=models.CASCADE, related_name='directorflat_categorydiscount')
    
    category_type= models.CharField(choices=TYPE_CHOICES, max_length=50, null=True, blank=True, )
    discount = models.PositiveIntegerField(default=0, blank= True, null=True)
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.id)
    
class DateRestrictions(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    directorflat = models.ForeignKey(DirectOrFlatDiscount, on_delete=models.CASCADE,  null=True, blank=True, related_name='directorflat_daterestrictions')
    specificgroupdiscount = models.ForeignKey(SpecificGroupDiscount, on_delete=models.CASCADE, null=True, blank=True, related_name='specificgroupdiscount_daterestrictions')
    
    
    business_address = models.ManyToManyField(BusinessAddress, null=True, blank=True, related_name='business_address_daterestrictions')
    start_date = models.DateField(verbose_name = 'Start Date', null=True)
    end_date = models.DateField(verbose_name = 'End Date', null=True)
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.id)
    
class DayRestrictions(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    directorflat = models.ForeignKey(DirectOrFlatDiscount, on_delete=models.CASCADE, null=True, blank=True, related_name='directorflat_dayrestrictions')
    specificgroupdiscount = models.ForeignKey(SpecificGroupDiscount, on_delete=models.CASCADE, null=True, blank=True, related_name='specificgroupdiscount_dayrestrictions')
    day = models.CharField(max_length=20, null=True, blank=True)
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.id)
    
class BlockDate(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    directorflat = models.ForeignKey(DirectOrFlatDiscount, on_delete=models.CASCADE, null=True, blank=True, related_name='directorflat_blockdate')
    specificgroupdiscount = models.ForeignKey(SpecificGroupDiscount, on_delete=models.CASCADE, null=True, blank=True, related_name='specificgroupdiscount_blockdate')

    
    date = models.DateField(verbose_name = 'Block Date', null=True)
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.id)