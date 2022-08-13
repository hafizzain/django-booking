from django.db import models
from django.utils.timezone import now
from Authentication.models import User
from Profile.models import Profile
from Utility.models import Country, State, City, Software, Currency


import uuid


class BusinessType(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    name = models.CharField(default='', max_length=100)
    image = models.ImageField(upload_to='business/business_types/images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


class Business(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_business')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='profile_business')

    business_name = models.CharField(default='', max_length=300)

    logo = models.ImageField(upload_to='business/logo/')
    banner = models.ImageField(upload_to='business/banner/')

    postal_code = models.CharField(max_length=30, default='')

    business_types = models.ManyToManyField(BusinessType, related_name='type_businesses')
    software_used = models.ManyToManyField(Software, related_name='software_businesses')

    week_start = models.CharField(default='Monday', max_length=20)
    team_size = models.CharField(max_length=100, default='')
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    timezone = models.CharField(max_length=200, default='')
    time_format = models.CharField(max_length=300, default='')
    how_find_us = models.CharField(max_length=500, default='')

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


class BusinessSocial(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_socials')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_socials')

    website = models.TextField()
    facebook = models.TextField()
    instagram = models.TextField()
    whatsapp = models.TextField()

    def __str__(self):
        return str(self.id)


class BusinessAddress(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_address')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_address')

    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='address_country')
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, related_name='address_state')
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='address_city')
    
    address_name = models.CharField(max_length=500, default='')
    address = models.TextField(default='')
    latitude = models.CharField(default='', max_length=200, null=True, blank=True)
    longitude = models.CharField(default='', max_length=200, null=True, blank=True)
    postal_code = models.CharField(max_length=30, default='')
    gstin = models.CharField(default='', max_length=1000, null=True, blank=True)
    website = models.TextField(null=True, blank=True)
    email = models.EmailField()
    is_email_verified = models.BooleanField(default=False)

    mobile_number = models.CharField(default='', max_length=30)
    is_mobile_verified = models.BooleanField(default=False)

    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)

class BusinessOpeningHour(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_hours')
    business_address = models.ForeignKey(BusinessAddress, on_delete=models.CASCADE, related_name='business_address_hours')

    day = models.CharField(max_length=20, default='')

    start_time = models.TimeField()
    close_time = models.TimeField()
    is_closed = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


    
# THEME CUSTOMIZATION 

class BusinessTheme(models.Model):
    CALENDAR_CHOICES = [
        ('HorizontalView', 'Horizontal View'),
        ('VerticalView', 'Vertical View'),
    ]
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_theme')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_theme')

    primary_color = models.CharField(max_length=20, default='')
    secondary_color = models.CharField(max_length=20, default='')

    menu_option = models.CharField(max_length=300, default='', null=True)
    calendar_option = models.CharField(max_length=50, default='HorizontalView', choices=CALENDAR_CHOICES)

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)


    def __str__(self):
        return str(self.id)

    
class StaffNotificationSetting(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_staff_notify_setting')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_staff_notify_setting')

    sms_daily_sale = models.BooleanField(default=True , verbose_name='Send SMS Notification on Daily Sale')
    email_daily_sale = models.BooleanField(default=True , verbose_name="Send Email Notification on Daily Sale")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=now)


    def __str__(self):
        return str(self.id)


    
class ClientNotificationSetting(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_client_notify_setting')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_client_notify_setting')


    sms_purchase_plan = models.BooleanField(default=True, verbose_name="Send SMS Notification on Purchase Plan")
    sms_for_rewards_on_quick_sale = models.BooleanField(default=True , verbose_name="Send SMS Notification for Rewards on quick Sale")
    sms_pending_services_quicksale = models.BooleanField(default=True , verbose_name="Send SMS Notification on Pending Services Quick Sale")
    sms_for_ewallet_balance_on_quick_sale = models.BooleanField(default=True , verbose_name="Send SMS Notification for ewallet balance on quick sale")
    sms_pending_payment = models.BooleanField(default=True , verbose_name="Send SMS Notification on Pending Payment")
    email_notify_on_purchase_plan = models.BooleanField(default=True , verbose_name="Send Email Notification On Purchase Plan")
    sms_quick_sale = models.BooleanField(default=True , verbose_name="Send SMS Notification on Quick Sale")
    sms_appoinment = models.BooleanField(default=True , verbose_name="Send Notification on Appoinment")
    sms_appoinment_reschedule = models.BooleanField(default=True , verbose_name="Send SMS Notification on Appoinment reschedule")
    sms_birthday = models.BooleanField(default=True , verbose_name="Send SMS Notification on Birthday")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=now)


    def __str__(self):
        return str(self.id)


    
class AdminNotificationSetting(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_admin_notify_setting')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_admin_notify_setting')

    sms_notify_on_appoinment = models.BooleanField(default=True , verbose_name="Send SMS Notification on Apoinment")
    sms_notify_on_quick_sale = models.BooleanField(default=True , verbose_name="Send SMS Notification on quick sale")
    sms_notify_for_daily_book = models.BooleanField(default=True , verbose_name="Send SMS Notification for daily book")
    email_notify_on_appoinment = models.BooleanField(default=True , verbose_name="Send Email Notification on Appoinment")
    email_notify_on_quick_sale = models.BooleanField(default=True , verbose_name="Send Email Notification on Quick Sale")
    email_notify_on_daily_book = models.BooleanField(default=True , verbose_name="Send Email Notification on Daily Book")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=now)


    def __str__(self):
        return str(self.id)

    
class StockNotificationSetting(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_stock_notify_setting')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_stock_notify_setting')

    notify_for_lowest_stock = models.BooleanField(default=True , verbose_name="Alert when stock becomes the lowest")
    notify_stock_turnover = models.BooleanField(default=True , verbose_name="Alert on highest/lowest turnover")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


