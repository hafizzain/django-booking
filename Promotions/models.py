# import uuid
# from django.db import models
# from django.utils.timezone import now
# from Authentication.models import User
# from Business.models import Business, BusinessAddress

# from Product.models import Product
# from Service.models import Service


# # Create your models here.
# class DirectOrFlatDiscount(models.Model):
#     id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='directorflatdiscount')
#     business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_directorflatdiscount')

#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_directorflatdiscount')    
#     service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='product_directorflatdiscount')    
    
#     location = models.ManyToManyField(BusinessAddress, null=True, related_name='location_directorflatdiscount')

    
#     start_date = models.DateField(verbose_name = 'Start Date', null=True)
#     end_date = models.DateField(verbose_name = 'End Date', null=True)
    
#     is_deleted = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=False)
#     is_blocked = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=now)
#     updated_at = models.DateTimeField(null=True, blank=True)

#     def __str__(self):
#         return str(self.id)
    
# class DayRestrictions(models.Model):
#     id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
#     directorflat = models.ForeignKey(DirectOrFlatDiscount, on_delete=models.CASCADE, related_name='directorflat_DayRestrictions')
    
#     day = models.CharField(max_length=20, null=True, blank=True)
    
#     is_deleted = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=False)
    
#     def __str__(self):
#         return str(self.id)
# class BlockDate(models.Model):
#     id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
#     directorflat = models.ForeignKey(DirectOrFlatDiscount, on_delete=models.CASCADE, related_name='directorflat_blockdate')
    
#     date = models.DateField(verbose_name = 'Block Date', null=True)
    
#     is_deleted = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=False)
    
#     def __str__(self):
#         return str(self.id)