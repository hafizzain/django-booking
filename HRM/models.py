from django.db import models
from Authentication.models import User
from Business.models import Business
from Utility.models import CommonField
from Business.models import BusinessAddress
from Employee.models import EmployeDailySchedule

# Create your models here.
class Holiday(CommonField):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    location = models.ForeignKey(BusinessAddress, on_delete=models.CASCADE)
    employee_schedule = models.ForeignKey(EmployeDailySchedule, on_delete=models.SET_NULL, null= True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200)
    note = models.TextField(null=True, blank=True, max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    
    REQUIRED_FIELDS = ['name', 'start_date']
    
    def __str__(self):
        return self.name