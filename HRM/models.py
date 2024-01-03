from django.db import models
from Authentication.models import User
from Business.models import Business
from Utility.models import CommonField
from Business.models import BusinessAddress
from datetime import datetime

# Create your models here.
class Holiday(CommonField):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    location = models.ForeignKey(BusinessAddress, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200)
    note = models.TextField(null=True, blank=True, max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    
    REQUIRED_FIELDS = ['name', 'start_date']
    
    def __str__(self):
        return self.name
    
    def is_holiday(self):
        today_date = datetime.now().date()

        # Convert start_date to datetime.date
        start_date = self.start_date.date() if self.start_date else None

        # Convert end_date to datetime.date
        end_date = self.end_date.date() if self.end_date else None

        # Check if today is within the holiday period
        return start_date <= today_date <= (end_date or datetime.max.date())