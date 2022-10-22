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
        ('Consumable', 'Consumable'),
        ('Both', 'Both'),
    ]
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_products')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_products')
    vendor = models.ForeignKey(BusinessVendor, on_delete=models.CASCADE, related_name='vendor_products', default=None, null=True, blank=True)
    
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='category_products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='brand_products')
    product_type = models.CharField(default='Sellable', choices=PRODUCT_TYPE_CHOICES, max_length=20)

    name = models.CharField(max_length=1000, default='')

    cost_price = models.PositiveIntegerField(default=0)
    full_price = models.PositiveIntegerField(default=0)
    sell_price = models.PositiveIntegerField(default=0)
    #product_size = models.PositiveIntegerField(default=0)
    product_size = models.CharField(max_length=50, null=True, blank=True)


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
    is_cover = models.BooleanField(default=False)

    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)


    def __str__(self):
        return str(self.id)


class ProductStock(models.Model):
    TURN_CHOICES =[
        ('Lowest', 'Lowest'),
        ('Highest', 'Highest')
    ]
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_product_stocks')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_product_stocks')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_stock')
    
    sellable_quantity = models.IntegerField(validators=[MinValueValidator(0)],null=True, blank=True, default=0, verbose_name= 'Sellable Quantity')
    consumable_quantity = models.IntegerField(validators=[MinValueValidator(0)],null=True, blank=True, default=0, verbose_name= 'Consumable Quantity')
    
    #quantity = models.PositiveIntegerField(validators=[MinValueValidator(0),], default=0, verbose_name='Total Quantity')
    available_quantity = models.PositiveIntegerField(validators=[MinValueValidator(0),], default=0)
    sold_quantity = models.PositiveIntegerField(validators=[MinValueValidator(0),], default=0)
    
    amount = models.PositiveIntegerField(default=0, verbose_name='Usage Amount', null=True, blank=True)
    unit = models.PositiveIntegerField(default=0, verbose_name='Usage Unit', null=True, blank=True)
    product_unit = models.PositiveIntegerField(default=0, verbose_name='Product Unit', null=True, blank=True)

    alert_when_stock_becomes_lowest = models.BooleanField(default=None, null=True, blank=True)
    
    #turnover = models.CharField(default='Highest', choices=TURN_CHOICES, max_length=40)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)


    def __str__(self):
        return str(self.id)


class OrderStock(models.Model):
    STATUS_CHOICES =[
        ('Placed', 'Placed'),
        ('Delivered', 'Delivered'),
        ('Partially_Received', 'Partially Received'),
        ('Received', 'Received'),
        ('Cancelled', 'Cancelled'),
    ]
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_order_stock')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_order_stock')
    
    vendor = models.ForeignKey(BusinessVendor, on_delete=models.CASCADE, related_name='vendor_order_stock', default=None, null=True, blank=True)
    location = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='locations_order_stock')
    
    status= models.CharField(choices = STATUS_CHOICES, max_length =100, default='Placed')
    rec_quantity= models.PositiveIntegerField(default=0, verbose_name= 'Received Quantity', null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)


    def __str__(self):
        return str(self.id)
    
class OrderStockProduct(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    order = models.ForeignKey(OrderStock, on_delete=models.CASCADE , related_name='order_stock')
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_order_stock')
    quantity = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return str(self.id)
    
    