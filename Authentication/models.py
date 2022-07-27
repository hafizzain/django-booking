from django.db import models

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid

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

    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    is_email_verified = models.BooleanField(default=False)

    joined_at = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    mobile_number = models.CharField(max_length=20, null=True, blank=True)
    is_mobile_verified = models.BooleanField(default=False)


    # User Defined Fields

    # maiden_name = models.CharField(max_length=128, null=True, blank=True)
    social_account = models.BooleanField(default=False)
    social_platform = models.CharField(max_length=32, choices=SOCIAL_PLATFORM_CHOICES, null=True, blank=True)
    social_id = models.CharField(max_length=128, default='', blank=True, null=True)

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


class AccountType(models.Model):
    ACCOUNT_TYPES = [
        ('Everyone', 'Everyone'),
        ('Business', 'Business'),
    ]
    id = models.CharField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_account_type')
    account_type = models.CharField(default='Everyone', choices=ACCOUNT_TYPES)

    def __str__(self):
        return str(self.id)

    def username(self):
        return str(self.user.username)

    def is_everyone(self):
        if self.account_type == 'Everyone':
            return True
        return False

    def is_business(self):
        if self.account_type == 'Business':
            return True

        return False