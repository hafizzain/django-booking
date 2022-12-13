from uuid import uuid4
from django.db import models
from django.utils.timezone import now


from Authentication.models import User
from Business.models import Business, BusinessAddress
from Employee.models import Employee
from Utility.models import Country, State, City
from Service.models  import Service

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
    
    service_target = models.PositiveIntegerField(default=0)
    retail_target = models.PositiveIntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=now) 
    
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

    is_primary = models.BooleanField(default=False)

    
    def __str__(self):
        return str(self.id)
    


