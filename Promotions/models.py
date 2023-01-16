import uuid
from django.db import models
from django.utils.timezone import now
from Authentication.models import User
from Business.models import Business, BusinessAddress

from Product.models import Brand, Product
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
    
    select_type= models.CharField(choices=TYPE_CHOICES, max_length=50, default = 'Product')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='product_purchase_discount')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True, related_name='service_purchase_discount')
    
    purchase = models.PositiveIntegerField(default=0, blank= True, null=True)
    
    discount_product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='discountproduct_purchase_discount')
    discount_service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True, related_name='discountservice_purchase_discount')
    
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

class SpendDiscount(models.Model):
    TYPE_CHOICES = [
        ('Service', 'Service'),
        ('Product', 'Product'),
    ]
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_spend_discount')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_spend_discount')
    
    spend_amount = models.PositiveIntegerField(default=0, blank= True, null=True)
    select_type= models.CharField(choices=TYPE_CHOICES, max_length=50, default = 'Service')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True, related_name='service_spend_discount')
    
    discount_product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='discountproduct_spend_discount')
    discount_service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True, related_name='discountservice_spend_discount')
    
    discount_value = models.PositiveIntegerField(default=0, blank= True, null=True)
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
    
class SpecificBrand(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_specific_brand')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_specific_brand')
    
    servicegroup = models.ForeignKey(ServiceGroup, on_delete=models.CASCADE, related_name='servicegroup_specific_brand')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='brand_specific_brand')
    
    discount_brand = models.PositiveIntegerField(default=0, blank= True, null=True)
    discount_service_group = models.PositiveIntegerField(default=0, blank= True, null=True)
    
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
    purchasediscount = models.ForeignKey(PurchaseDiscount, on_delete=models.CASCADE, null=True, blank=True, related_name='purchasediscount_daterestrictions')
    
    specificbrand = models.ForeignKey(SpecificBrand, on_delete=models.CASCADE, null=True, blank=True, related_name='specificbrand_daterestrictions')
    
    
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
    purchasediscount = models.ForeignKey(PurchaseDiscount, on_delete=models.CASCADE, null=True, blank=True, related_name='purchasediscount_dayrestrictions')
    
    specificbrand = models.ForeignKey(SpecificBrand, on_delete=models.CASCADE, null=True, blank=True, related_name='specificbrand_dayrestrictions')
    
    day = models.CharField(max_length=20, null=True, blank=True)
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.id)
    
class BlockDate(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    directorflat = models.ForeignKey(DirectOrFlatDiscount, on_delete=models.CASCADE, null=True, blank=True, related_name='directorflat_blockdate')
    specificgroupdiscount = models.ForeignKey(SpecificGroupDiscount, on_delete=models.CASCADE, null=True, blank=True, related_name='specificgroupdiscount_blockdate')
    purchasediscount = models.ForeignKey(PurchaseDiscount, on_delete=models.CASCADE, null=True, blank=True, related_name='purchasediscount_blockdate')
    
    specificbrand = models.ForeignKey(SpecificBrand, on_delete=models.CASCADE, null=True, blank=True, related_name='specificbrand_blockdate')

    
    date = models.DateField(verbose_name = 'Block Date', null=True)
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.id)