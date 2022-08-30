from django.db import models

# class Client(models.Model):
#     GENDER_CHOICES = [
#         ('Male' , 'Male'),
#         ('Female' , 'Female'),
#         ('Others' , 'Others'),
#     ]
#     id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client')
#     business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_client')

#     full_name = models.CharField(max_length=300, default='')
#     image = models.ImageField(upload_to='employee/employee_images/', null=True, blank=True)
#     client_id = models.CharField(max_length=50, default='')
#     email = models.EmailField(default='')
#     mobile_number = models.CharField(max_length=30, default='')
#     is_email_verified = models.BooleanField(default=False)
#     is_mobile_verified = models.BooleanField(default=False)

#     dob = models.DateField(verbose_name='Date of Birth')
#     gender = models.CharField(choices=GENDER_CHOICES, default='Male', max_length=20)

#     country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='country_client')
#     state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, related_name='state_client')
#     city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='city_client')

#     postal_code = models.CharField(max_length=20, default='')
#     address = models.TextField(default='')
#     card_number = models.CharField(max_length=30, default='')


#     joining_date = models.DateField()
#     to_present = models.BooleanField(default=False)
#     ending_date = models.DateField(null=True, blank=True)

#     is_deleted = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=False)
#     is_blocked = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=now)
#     updated_at = models.DateTimeField(null=True, blank=True)

#     def __str__(self):
#         return str(self.id)