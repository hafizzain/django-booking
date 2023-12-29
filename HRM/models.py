from django.db import models
from Authentication.models import User
from Business.models import Business
from Utility.models import CommonField
from Business.models import BusinessAddress

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