from django.db import models

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid
from django.utils.timezone import now

# Create your models here.


class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)

        # profile = Profile.objects.create(
        #     user=user,
        #     gender='Male',
        # )

        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)

        return user
    

class User(AbstractBaseUser):
    SOCIAL_PLATFORM_CHOICES = [
        ('Google', 'Google'),
        ('Facebook', 'Facebook'),
        ('Twitter', 'Twitter'),
        ('Apple', 'Apple'),
    ]
    # Required Fields

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    first_name = models.CharField(max_length=128)
    middle_name = models.CharField(max_length=128, null=True, blank=True)
    last_name = models.CharField(max_length=128, null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=30, unique=True)

    email = models.EmailField(verbose_name="email", max_length=60,) #unique=True)
    is_email_verified = models.BooleanField(default=False)

    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    # Add new fields
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    zip_code = models.CharField(max_length=255, null=True, blank=True)
    
    mobile_number = models.CharField(max_length=20, null=True, blank=True)
    is_mobile_verified = models.BooleanField(default=False)

    is_asked_for_data_update = models.BooleanField(default=False, verbose_name='Is Asked user to update his Default Data ( Location, Client, Employee, Service)? :')


    # maiden_name = models.CharField(max_length=128, null=True, blank=True)
    social_account = models.BooleanField(default=False)
    social_platform = models.CharField(max_length=32, choices=SOCIAL_PLATFORM_CHOICES, null=True, blank=True)
    social_id = models.CharField(max_length=128, default='', blank=True, null=True)


    joined_at = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Updated Date Time', null=True, blank=True)

    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = MyAccountManager()

    def __str__(self):
        return self.username

    # For checking permissions. to keep it simple all admin have ALL permissons
    def has_perm(self, perm, obj=None):
        return self.is_admin

    # Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
    def has_module_perms(self, app_label):
        return True

    def account_type(self):
        return self.user_account_type.account_type

    def get_all_permissions(self):
        return []

    @property
    def user_full_name(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        
        elif self.full_name:
            return f'{self.full_name}'
        else:
            return self.username

class AccountType(models.Model):
    ACCOUNT_TYPES = [
        ('Everyone', 'Everyone'),
        ('Business', 'Business'),
        ('Employee', 'Employee'),
    ]
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_account_type')
    account_type = models.CharField(default='Everyone', choices=ACCOUNT_TYPES, max_length=20)

    def __str__(self):
        return str(self.id)

    def username(self):
        return str(self.user.username)

    def email(self):
        return str(self.user.email)

    def is_everyone(self):
        if self.account_type == 'Everyone':
            return True
        return False

    def is_business(self):
        if self.account_type == 'Business':
            return True

        return False

class NewsLetterDetail(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='newsletter')

    terms_condition = models.BooleanField(default=False)

    is_subscribed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)

class VerificationOTP(models.Model):
    CODE_TYPE = [
        ('Email' , 'Email'),
        ('Mobile' , 'Mobile'),
    ]
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_otp')

    code = models.CharField(default='', max_length=10)
    code_for = models.CharField(choices=CODE_TYPE, default='Mobile', max_length=10)

    created_at = models.DateTimeField(auto_now_add=now)

    class Meta:
        unique_together = ['user', 'code', 'code_for']

    def __str__(self):
        return str(self.id)

    def username(self):
        return str(self.user.username)
