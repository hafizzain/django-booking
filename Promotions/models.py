import uuid
from django.db import models
from django.utils.timezone import now
from Authentication.models import User
from Business.models import Business, BusinessAddress
from Client.models import Client

from Product.models import Brand, Product
from Service.models import Service, ServiceGroup


# Create your models here.
class SpecificGroupDiscount(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_specificgroup_discount')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='businessgroup_specific_discount')
    promotion_name = models.CharField(default='Promotion Name', max_length=999)

    
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
    
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, blank= True, null=True, related_name='brand_specificgroupdiscount')
    brand_discount = models.PositiveIntegerField(default=0, blank= True, null=True)

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

    promotion_name = models.CharField(default='Promotion Name', max_length=999)

    
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_directorflatdiscount')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_directorflatdiscount')

    promotion_name = models.CharField(default='Promotion Name', max_length=999)
    
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
    
    promotion_name = models.CharField(default='Promotion Name', max_length=999)

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

class SpendSomeAmount(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_spendsomeamount')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_spendsomeamount')
    promotion_name = models.CharField(default='Promotion Name', max_length=999)

    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
    
class SpendSomeAmountAndGetDiscount(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    spend_amount = models.PositiveIntegerField(default=0, blank= True, null=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True, related_name='service_spendandgetdiscount')
    
    spandsomeamount = models.ForeignKey(SpendSomeAmount, on_delete=models.CASCADE, null=True, blank=True, related_name='spendandgetdiscount_spendsomeamount')
    
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
 
class FixedPriceService(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_fixedpriceservice')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_fixedpriceservice')

    promotion_name = models.CharField(default='Promotion Name', max_length=999)

    
    spend_amount = models.PositiveIntegerField(default=0, blank= True, null=True)
    duration = models.CharField(max_length=100, default='')
    service = models.ManyToManyField(Service, null=True, blank=True, related_name='service_fixedpriceservice')
    
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
    promotion_name = models.CharField(default='Promotion Name', max_length=999)
    
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
    
class MentionedNumberService(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_mentionednumberservice')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_mentionednumberservice')

    promotion_name = models.CharField(default='Promotion Name', max_length=999)

    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True, related_name='service_mentionednumberservice')    

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
    
class FreeService(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    quantity = models.PositiveIntegerField(default=0, blank= True, null=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True, related_name='service_freeservice')    
    
    mentionnumberservice = models.ForeignKey(MentionedNumberService, on_delete=models.CASCADE, null=True, blank=True, related_name='freeservice_mentionnumberservice')

    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
 
class BundleFixed(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_bundlefixed')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_bundlefixed')

    promotion_name = models.CharField(default='Promotion Name', max_length=999)
    

    
    service = models.ManyToManyField(Service, null=True, blank=True, related_name='service_bundlefixed')    
    spend_amount = models.PositiveIntegerField(default=0, blank= True, null=True)
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
  
class RetailAndGetService(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_retailandgetservice')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_retailandgetservice')

    promotion_name = models.CharField(default='Promotion Name', max_length=999)

    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)  

class ProductAndGetSpecific(models.Model):

    PROMOTION_TYPE_CHOICES = (
        ('Brand', 'Brand'),
        ('Product', 'Product'),
    )
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='product_productandgetspecific')    
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True, related_name='brand_productandgetspecific')    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True, related_name='service_productandgetspecific')    
    
    retailandservice = models.ForeignKey(RetailAndGetService, on_delete=models.CASCADE, null=True, blank=True, related_name='retailandservice_productandgetspecific')

    promotion_type = models.CharField(choices=PROMOTION_TYPE_CHOICES, default='Product', max_length=20)

    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
  
class UserRestrictedDiscount(models.Model):
    CORPORATE_CHOICE = [
        ('All_Service' , 'All Service'),
        ('Retail_Product' , 'Retail Product'),
    ] 
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_userrestricteddiscount', null= True, blank = True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_userrestricteddiscount')

    promotion_name = models.CharField(default='Promotion Name', max_length=999)

    
    corporate_type = models.CharField(choices=CORPORATE_CHOICE, default='All_Service', max_length=50)
    client = models.ManyToManyField(Client, related_name='client_userrestricteddiscount')
    discount_percentage = models.PositiveIntegerField(default=0, blank= True, null=True)
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id) 
  
class ComplimentaryDiscount(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_complimentrydiscount')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_complimentrydiscount')

    promotion_name = models.CharField(default='Promotion Name', max_length=999)

        
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)  
    
class PackagesDiscount(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_packagesdiscount', null= True, blank = True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_packagesdiscount')

    promotion_name = models.CharField(default='Promotion Name', max_length=999)

    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id) 

class ServiceDurationForSpecificTime(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    service = models.ManyToManyField(Service, null=True, blank=True, related_name='service_servicedurationspecifictime')
    package = models.ForeignKey(PackagesDiscount, on_delete=models.CASCADE, null=True, blank=True, related_name='package_servicedurationspecifictime')    

    service_duration= models.CharField(max_length=100, null=True, blank=True )
    package_duration= models.CharField(max_length=100, null=True, blank=True )
    total_amount = models.PositiveIntegerField(default=0, blank= True, null=True)
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.id)
    
class DiscountOnFreeService(models.Model):
    TYPE_CHOICES = [
        ('Next 1 visit', 'Next 1 visit'),
        ('Next 2 visit', 'Next 2 visit'),
        ('Next 3 visit', 'Next 3 visit'),
        ('Next 4 visit', 'Next 4 visit'),
        ('Next 5 visit', 'Next 5 visit'),
        ('Next 6 visit', 'Next 6 visit'),
        ('Next 7 visit', 'Next 7 visit'),
        ('Next 8 visit', 'Next 8 visit'),
        ('Next 9 visit', 'Next 9 visit'),
        ('Next 10 visit', 'Next 10 visit')
    ]
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    complimentary = models.ForeignKey(ComplimentaryDiscount, on_delete=models.CASCADE, null=True, blank=True, related_name='complimentary_discountonfreeservice')    

    discount_percentage = models.PositiveIntegerField(default=0, blank= True, null=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True, related_name='service_discountonfreeservice')    
    discount_duration= models.CharField(choices=TYPE_CHOICES, max_length=100, null=True, blank=True,default= 'Next 1 visit' )
    
    
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
    spenddiscount = models.ForeignKey(SpendDiscount, on_delete=models.CASCADE, null=True, blank=True, related_name='spenddiscount_daterestrictions')
    spendsomeamount = models.ForeignKey(SpendSomeAmount, on_delete=models.CASCADE, null=True, blank=True, related_name='spendsomeamount_daterestrictions')
    
    fixedpriceservice = models.ForeignKey(FixedPriceService, on_delete=models.CASCADE, null=True, blank=True, related_name='fixedpriceservice_daterestrictions')
    mentionednumberservice = models.ForeignKey(MentionedNumberService, on_delete=models.CASCADE, null=True, blank=True, related_name='mentionednumberservice_daterestrictions')
    bundlefixed = models.ForeignKey(BundleFixed, on_delete=models.CASCADE, null=True, blank=True, related_name='bundlefixed_daterestrictions')
    
    retailandservice = models.ForeignKey(RetailAndGetService, on_delete=models.CASCADE, null=True, blank=True, related_name='retailandservice_daterestrictions')
    userrestricteddiscount = models.ForeignKey(UserRestrictedDiscount, on_delete=models.CASCADE, null=True, blank=True, related_name='userrestricteddiscount_daterestrictions')
    complimentary = models.ForeignKey(ComplimentaryDiscount, on_delete=models.CASCADE, null=True, blank=True, related_name='complimentary_daterestrictions')    
    
    package = models.ForeignKey(PackagesDiscount, on_delete=models.CASCADE, null=True, blank=True, related_name='package_daterestrictions')    

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
    spenddiscount = models.ForeignKey(SpendDiscount, on_delete=models.CASCADE, null=True, blank=True, related_name='spenddiscount_dayrestrictions')
    spendsomeamount = models.ForeignKey(SpendSomeAmount, on_delete=models.CASCADE, null=True, blank=True, related_name='spendsomeamount_dayrestrictions')
    
    fixedpriceservice = models.ForeignKey(FixedPriceService, on_delete=models.CASCADE, null=True, blank=True, related_name='fixedpriceservice_dayrestrictions')
    mentionednumberservice = models.ForeignKey(MentionedNumberService, on_delete=models.CASCADE, null=True, blank=True, related_name='mentionednumberservice_dayrestrictions')
    bundlefixed = models.ForeignKey(BundleFixed, on_delete=models.CASCADE, null=True, blank=True, related_name='bundlefixed_dayrestrictions')
    
    retailandservice = models.ForeignKey(RetailAndGetService, on_delete=models.CASCADE, null=True, blank=True, related_name='retailandservice_dayrestrictions')
    userrestricteddiscount = models.ForeignKey(UserRestrictedDiscount, on_delete=models.CASCADE, null=True, blank=True, related_name='userrestricteddiscount_dayrestrictions')
    complimentary = models.ForeignKey(ComplimentaryDiscount, on_delete=models.CASCADE, null=True, blank=True, related_name='complimentary_dayrestrictions')    
    
    package = models.ForeignKey(PackagesDiscount, on_delete=models.CASCADE, null=True, blank=True, related_name='package_dayrestrictions')    

    
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
    spenddiscount = models.ForeignKey(SpendDiscount, on_delete=models.CASCADE, null=True, blank=True, related_name='spenddiscount_blockdate')
    spendsomeamount = models.ForeignKey(SpendSomeAmount, on_delete=models.CASCADE, null=True, blank=True, related_name='spendsomeamount_blockdate')
    
    fixedpriceservice = models.ForeignKey(FixedPriceService, on_delete=models.CASCADE, null=True, blank=True, related_name='fixedpriceservice_blockdate')
    mentionednumberservice = models.ForeignKey(MentionedNumberService, on_delete=models.CASCADE, null=True, blank=True, related_name='mentionednumberservice_blockdate')
    bundlefixed = models.ForeignKey(BundleFixed, on_delete=models.CASCADE, null=True, blank=True, related_name='bundlefixed_blockdate')
    
    retailandservice = models.ForeignKey(RetailAndGetService, on_delete=models.CASCADE, null=True, blank=True, related_name='retailandservice_blockdate')
    userrestricteddiscount = models.ForeignKey(UserRestrictedDiscount, on_delete=models.CASCADE, null=True, blank=True, related_name='userrestricteddiscount_blockdate')
    complimentary = models.ForeignKey(ComplimentaryDiscount, on_delete=models.CASCADE, null=True, blank=True, related_name='complimentary_blockdate')    
    
    package = models.ForeignKey(PackagesDiscount, on_delete=models.CASCADE, null=True, blank=True, related_name='package_blockdate')    

    
    date = models.DateField(verbose_name = 'Block Date', null=True)
    
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.id)



class PromotionExcludedItem(models.Model):

    EXCLUDED_TYPES = (
        ('Product', 'Product'),
        ('Service', 'Service'),
        ('Voucher', 'Voucher'),
    )

    OBJECT_TYPES = (
        ('Direct Or Flat' , 'Direct Or Flat'),
        ('Specific Group Discount' , 'Specific Group Discount'),
        ('Purchase Discount' , 'Purchase Discount'),
        ('Specific Brand Discount' , 'Specific Brand Discount'),
        ('Spend_Some_Amount' , 'Spend_Some_Amount'),
        ('Fixed_Price_Service' , 'Fixed_Price_Service'),
        ('Mentioned_Number_Service' , 'Mentioned_Number_Service'),
        ('Bundle_Fixed_Service' , 'Bundle_Fixed_Service'),
        ('Retail_and_Get_Service' , 'Retail_and_Get_Service'),
        ('User_Restricted_discount' , 'User_Restricted_discount'),
        ('Complimentary_Discount' , 'Complimentary_Discount'),
        ('Packages_Discount' , 'Packages_Discount'),

    )
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    object_type = models.CharField(max_length=800, default='', choices=OBJECT_TYPES)
    object_id = models.CharField(max_length=800, default='')

    excluded_type = models.CharField(max_length=100, default='', choices=EXCLUDED_TYPES)
    excluded_id = models.CharField(max_length=800, default='')

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)