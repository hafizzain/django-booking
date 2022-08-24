from uuid import uuid4
from django.db import models
from django.utils.timezone import now


from Authentication.models import User
from Business.models import Business
from Utility.models import Country, State, City

class Employee(models.Model):
    GENDER_CHOICES = [
        ('Male' , 'Male'),
        ('Female' , 'Female'),
        ('Others' , 'Others'),
    ]
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employee')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_employees')

    full_name = models.CharField(max_length=300, default='')
    employee_id = models.CharField(max_length=50, default='')
    email = models.EmailField(default='')
    mobile_number = models.CharField(max_length=30, default='')
    is_email_verified = models.BooleanField(default=False)
    is_mobile_verified = models.BooleanField(default=False)

    dob = models.DateField(verbose_name='Date of Birth')
    gender = models.CharField(choices=GENDER_CHOICES, default='Male', max_length=20)

    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='country_employees')
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, related_name='state_employees')
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='city_employees')

    postal_code = models.CharField(max_length=20, default='')
    address = models.TextField(default='')

    joining_date = models.DateField()
    to_present = models.BooleanField(default=False)
    ending_date = models.DateField()

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)

class EmployeeProfessionalInfo(models.Model):
    INCOME_TYPE_CHOICES = [
        ('Hourly_Rate', 'Hourly_Rate'),
        ('Daily_Income', 'Daily_Income'),
        ('Monthly_Salary', 'Monthly_Salary'),
    ]
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_professional_details')
    designation = models.CharField(max_length=300, default='')
    income_type = models.CharField(choices=INCOME_TYPE_CHOICES, default='Hourly_Rate', max_length=30)
    salary = models.PositiveIntegerField(default=0)
    # services = models.ManyToManyField()

    def __str__(self):
        return str(self.id)
