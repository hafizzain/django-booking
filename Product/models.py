from django.db import models
from django.utils.timezone import now
from django.core.validators import MinValueValidator
import uuid

from Authentication.models import User
from Business.models import Business, BusinessAddress, BusinessVendor



class Category(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=500, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)



class Brand(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    name = models.CharField(max_length=500, default='')
    description = models.TextField(default='', null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    image = models.ImageField(upload_to='brand/images/')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)



    

class Product(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('Sellable', 'Sellable'),
        ('Non_Sellable', 'Non_Sellable')
    ]
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_products')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_products')
    vendor = models.ForeignKey(BusinessVendor, on_delete=models.CASCADE, related_name='vendor_products', default=None, null=True, blank=True)
    
    #image = models.ImageField(upload_to='product/product_images/', null=True, blank=True)

    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='category_products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='brand_products')
    product_type = models.CharField(default='Sellable', choices=PRODUCT_TYPE_CHOICES, max_length=20)

    name = models.CharField(max_length=1000, default='')

    cost_price = models.PositiveIntegerField(default=0)
    full_price = models.PositiveIntegerField(default=0)
    sell_price = models.PositiveIntegerField(default=0)

    tax_rate = models.PositiveIntegerField(default=0, null=True, blank=True)

    short_description = models.TextField(default='', null=True, blank=True)
    description = models.TextField(default='', null=True, blank=True)

    barcode_id = models.CharField(max_length=500, default='', null=True, blank=True)
    sku = models.CharField(max_length=500, default='')
    slug = models.CharField(max_length=1000, default='')


    published = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)


    def __str__(self):
        return str(self.id)


class ProductMedia(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_product_medias')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_product_medias')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_medias')

    image = models.ImageField(upload_to='business/product_images/')

    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)


    def __str__(self):
        return str(self.id)


class ProductStock(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_product_stocks')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_product_stocks')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_stock')

    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0),], default=0, verbose_name='Total Quantity')
    available_quantity = models.PositiveIntegerField(validators=[MinValueValidator(0),], default=0)
    sold_quantity = models.PositiveIntegerField(validators=[MinValueValidator(0),], default=0)
    amount = models.PositiveIntegerField(default=0, verbose_name='Usage Amount', null=True, blank=True)
    unit = models.PositiveIntegerField(default=0, verbose_name='Usage Unit', null=True, blank=True)

    alert_when_stock_becomes_lowest = models.BooleanField(default=None, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)


    def __str__(self):
        return str(self.id)
