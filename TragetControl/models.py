from uuid import uuid4
from django.db import models
from django.utils.timezone import now


from Authentication.models import User
from Business.models import Business, BusinessAddress
from Employee.models import Employee
from Product.models import Brand
from Utility.models import Country, State, City
from Service.models  import Service, ServiceGroup

class StaffTarget(models.Model):
    MONTH_CHOICE =[
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),

    ]
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_stafftarget')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_stafftarget')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_stafftarget')
    
    month = models.CharField(choices=MONTH_CHOICE, max_length=100, default='January')
    year = models.DateTimeField( null = True, blank =True)

    
    service_target = models.PositiveIntegerField(default=0)
    retail_target = models.PositiveIntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=now) 
    
    @property
    def year_add(self):
        try:
            year = self.year.split('-')[0]
            print(year)
            return year
        except:
            return self.year
    
    def __str__(self):
        return str(self.id)
    
    
class StoreTarget(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_storetarget')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_storetarget')
    
    location = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, related_name='location_storetarget')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=now) 
    
    def __str__(self):
        return str(self.id)
    
class TierStoreTarget(models.Model):
    MONTH_CHOICE =[
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    ]
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    storetarget = models.ForeignKey(StoreTarget, on_delete=models.CASCADE, null=True, blank=True, related_name='storetarget_address')

    month = models.CharField(choices=MONTH_CHOICE, max_length=100, default='January')
    
    service_target = models.PositiveIntegerField(default=0)
    retail_target = models.PositiveIntegerField(default=0)
    voucher_target = models.PositiveIntegerField(default=0)
    membership_target = models.PositiveIntegerField(default=0)
    year = models.DateTimeField( null = True, blank =True)

    is_primary = models.BooleanField(default=False)

    
    def __str__(self):
        return str(self.id)
    
class ServiceTarget(models.Model):
    MONTH_CHOICE =[
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    ]
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_servicetarget')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_servicetarget')
    
    location = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, related_name='location_servicetarget')
    service_group = models.ForeignKey(ServiceGroup, on_delete=models.SET_NULL, null=True, related_name='servicegroup_servicetarget')
    
    month = models.CharField(choices=MONTH_CHOICE, max_length=100, default='January')
    year = models.DateTimeField( null = True, blank =True)

    service_target = models.PositiveIntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(null=True, auto_now_add=now) 
    
    def __str__(self):
        return str(self.id)
    
class RetailTarget(models.Model):
    MONTH_CHOICE =[
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    ]
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_retailtarget')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_retailtarget')
    
    location = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, related_name='location_retailtarget')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, related_name='brand_retailtarget')
    
    month = models.CharField(choices=MONTH_CHOICE, max_length=100, default='January')
    year = models.DateTimeField( null = True, blank =True)

    brand_target = models.PositiveIntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=now, null= True) 
    
    def __str__(self):
        return str(self.id)