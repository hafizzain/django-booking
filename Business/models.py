from django.db import models
from django.utils.timezone import now
from Authentication.models import User
# from Employee.models import Employee
from Profile.models import Profile, UserLanguage
from Utility.models import Country, State, City, Software, Currency, CommonField
from Utility.Constants.compressImage import upload_to_bucket
import uuid


class BusinessType(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    name = models.CharField(default='', max_length=100)
    image = models.ImageField(upload_to='business/business_types/images/', null=True, blank=True)
    image_path = models.CharField(default='', max_length=2000, null=True, blank=True)
    slug = models.CharField(max_length=1000, default='')
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
    is_logo_uploaded_s3 = models.BooleanField(default=False)
    banner = models.ImageField(upload_to='business/banner/')
    is_banner_uploaded_s3 = models.BooleanField(default=False)

    postal_code = models.CharField(max_length=30, default='')

    business_types = models.ManyToManyField(BusinessType, related_name='type_businesses')
    software_used = models.ManyToManyField(Software, related_name='software_businesses')

    week_start = models.CharField(default='Monday', max_length=20)
    team_size = models.CharField(max_length=100, default='')
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    timezone = models.CharField(max_length=200, default='')
    time_format = models.CharField(max_length=300, default='')
    how_find_us = models.CharField(max_length=500, default='')

    is_completed = models.BooleanField(default=False, verbose_name='Business setting completed')

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def save(self, *args, **kwargs):
        if self.logo:
            self.is_logo_uploaded_s3 = True

        if self.banner:
            self.is_banner_uploaded_s3 = True
        super(Business, self).save(*args, **kwargs)

    def __str__(self):

        return str(self.id)


class BusinessSocial(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_socials')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='business_socials')

    website = models.TextField()
    facebook = models.TextField()
    instagram = models.TextField()
    whatsapp = models.TextField()

    def __str__(self):
        return str(self.id)


class BusinessAddress(models.Model):
    BANKING_CHOICE = [
        ('Enable', 'Enable'),
        ('Disable', 'Disable')
    ]

    SERVICE_CHOICE = [
        ('Everyone', 'Everyone'),
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_address')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='business_address')

    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='address_country')
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, related_name='address_state')
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='address_city')

    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='address_currency')

    address_name = models.CharField(max_length=500, default='')
    address = models.TextField(default='')

    service_avaiable = models.CharField(choices=SERVICE_CHOICE, default='Everyone', max_length=100)
    location_name = models.CharField(max_length=500, default='')

    latitude = models.CharField(default='', max_length=200, null=True, blank=True)
    longitude = models.CharField(default='', max_length=200, null=True, blank=True)
    postal_code = models.CharField(max_length=30, default='', null=True, blank=True)
    gstin = models.CharField(default='', max_length=1000, null=True, blank=True)
    website = models.TextField(null=True, blank=True)
    email = models.EmailField()
    is_email_verified = models.BooleanField(default=False)

    mobile_number = models.CharField(default='', max_length=30)
    is_mobile_verified = models.BooleanField(default=False)

    description = models.CharField(max_length=300, null=True, blank=True)
    banking = models.CharField(choices=BANKING_CHOICE, default='Disable', max_length=50)

    primary_translation = models.ForeignKey('MultiLanguage.InvoiceTranslation', related_name='primary',
                                            on_delete=models.SET_NULL, null=True)
    secondary_translation = models.ForeignKey('MultiLanguage.InvoiceTranslation', related_name='secondary',
                                              on_delete=models.SET_NULL, null=True)

    is_default = models.BooleanField(default=False)

    is_publish = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    privacy_policy = models.TextField(null=True)

    def __str__(self):
        return str(self.id)


class BusinessOpeningHour(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='business_hours')
    business_address = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='business_address_hours')

    day = models.CharField(max_length=20, default='')

    start_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    class Meta:
        unique_together = ['business', 'business_address', 'day']

    def __str__(self):
        return str(self.id)


class BusinessAddressMedia(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_businessaddress_media')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='business_businessaddress_media')
    business_address = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='business_address_businessaddress_media')

    image = models.ImageField(upload_to='business/address_media/', null=True, blank=True)
    is_image_uploaded_s3 = models.BooleanField(default=False)

    is_cover = models.BooleanField(default=False)

    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def save(self, *args, **kwargs):
        if self.image:
            self.is_image_uploaded_s3 = True

        super(BusinessAddressMedia, self).save(*args, **kwargs)

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
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='business_theme')

    theme_name = models.CharField(max_length=100, default='')
    primary_color = models.CharField(max_length=20, default='')
    secondary_color = models.CharField(max_length=20, default='')

    menu_option = models.CharField(max_length=300, default='', null=True, blank=True)
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
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='business_staff_notify_setting')

    sms_daily_sale = models.BooleanField(default=False, verbose_name='Send SMS Notification on Daily Sale')
    email_daily_sale = models.BooleanField(default=True, verbose_name="Send Email Notification on Daily Sale")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


class ClientNotificationSetting(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_client_notify_setting')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='business_client_notify_setting')

    sms_purchase_plan = models.BooleanField(default=False, verbose_name="Send SMS Notification on Purchase Plan")
    sms_for_rewards_on_quick_sale = models.BooleanField(default=False,
                                                        verbose_name="Send SMS Notification for Rewards on quick Sale")
    sms_pending_services_quicksale = models.BooleanField(default=False,
                                                         verbose_name="Send SMS Notification on Pending Services Quick Sale")
    sms_for_ewallet_balance_on_quick_sale = models.BooleanField(default=False,
                                                                verbose_name="Send SMS Notification for ewallet balance on quick sale")
    sms_pending_payment = models.BooleanField(default=False, verbose_name="Send SMS Notification on Pending Payment")
    email_notify_on_purchase_plan = models.BooleanField(default=True,
                                                        verbose_name="Send Email Notification On Purchase Plan")
    sms_quick_sale = models.BooleanField(default=True, verbose_name="Send SMS Notification on Quick Sale")
    sms_appoinment = models.BooleanField(default=True, verbose_name="Send Notification on Appoinment")
    sms_appoinment_reschedule = models.BooleanField(default=False,
                                                    verbose_name="Send SMS Notification on Appoinment reschedule")
    sms_birthday = models.BooleanField(default=False, verbose_name="Send SMS Notification on Birthday")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


class AdminNotificationSetting(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_admin_notify_setting')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='business_admin_notify_setting')

    sms_notify_on_appoinment = models.BooleanField(default=False, verbose_name="Send SMS Notification on Apoinment")
    sms_notify_on_quick_sale = models.BooleanField(default=False, verbose_name="Send SMS Notification on quick sale")
    sms_notify_for_daily_book = models.BooleanField(default=False, verbose_name="Send SMS Notification for daily book")
    email_notify_on_appoinment = models.BooleanField(default=True, verbose_name="Send Email Notification on Appoinment")
    email_notify_on_quick_sale = models.BooleanField(default=True, verbose_name="Send Email Notification on Quick Sale")
    email_notify_on_daily_book = models.BooleanField(default=False,
                                                     verbose_name="Send Email Notification on Daily Book")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


class StockNotificationSetting(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_stock_notify_setting')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='business_stock_notify_setting')

    notify_for_lowest_stock = models.BooleanField(default=True, verbose_name="Alert when stock becomes the lowest")
    notify_stock_turnover = models.BooleanField(default=True, verbose_name="Alert on highest/lowest turnover")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


class BookingSetting(models.Model):
    CANCEL_OR_RESCHEDULE_CHOICES = [
        ('Anytime', 'Anytime'),
        ('12_Hours_Prior_To_The_Appoinment', '12 Hours Prior To The Appoinment'),
        ('24_Hours_Prior_To_The_Appoinment', '24 Hours Prior To The Appoinment'),
        ('36_Hours_Prior_To_The_Appoinment', '36 Hours Prior To The Appoinment'),
    ]

    CLIENT_CAN_BOOK_CHOICES = [
        ('Anytime', 'Anytime'),
        ('5_Hours_Before', '5 Hours Before'),
        ('12_Hours_Before', '12 Hours Before'),
        ('24_Hours_Before', '24 Hours Before'),
        ('36_Hours_Before', '36 Hours Before'),
    ]

    CONTROLS_TIME_SLOT_CHOICES = [
        ('Anytime_In_The_Future', 'Anytime In The Future'),
        ('No_More_Than_1_Months_In_The_Future', 'No More Than 1 Months In The Future'),
        ('No_More_Than_2_Months_In_The_Future', 'No More Than 2 Months In The Future'),
        ('No_More_Than_3_Months_In_The_Future', 'No More Than 3 Months In The Future'),
    ]

    TIME_SLOT_INTERVAL_CHOICES = [
        ('15_Mins', '15 Mins'),
        ('30_Mins', '30 Mins'),
        ('45_Mins', '45 Mins'),
        ('60_Mins', '60 Mins'),
        ('120_Mins', '120 Mins'),
    ]

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_booking_setting')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='business_booking_setting')

    # ONLINE CANCELLATION AND RESCHEDULING 
    cancel_or_reschedule = models.CharField(choices=CANCEL_OR_RESCHEDULE_CHOICES, default='Anytime', max_length=100)

    # ONLINE BOOKING AVAILABILITY 
    client_can_book = models.CharField(choices=CLIENT_CAN_BOOK_CHOICES, max_length=100, default='Anytime')
    controls_time_slot = models.CharField(choices=CONTROLS_TIME_SLOT_CHOICES, max_length=100,
                                          default='Anytime_In_The_Future')
    time_slots_interval = models.CharField(choices=TIME_SLOT_INTERVAL_CHOICES, default='15_Mins', max_length=50)
    allow_client_to_select_team_member = models.BooleanField(default=True)

    # ONLINE BOOKING ACTIVITY EMAILS 
    send_to_client = models.BooleanField(default=False)
    send_to_specific_email_address = models.BooleanField(default=False)

    # BOOKING CONFIRMATION 
    auto_confirmation = models.BooleanField(default=False)
    admin_confirmation = models.BooleanField(default=False)

    # BOOKING FORM
    start_time = models.BooleanField(default=True)
    services = models.BooleanField(default=True)
    duration = models.BooleanField(default=False)
    choose_team_member = models.BooleanField(default=True)
    select_payment_type = models.BooleanField(default=False)
    initial_deposit = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


class BusinessPaymentMethod(models.Model):
    METHOD_TYPE_CHOICES = [
        ('Cash', 'Cash'),
        ('Mastercard', 'Mastercard'),
        ('Visa', 'Visa'),
        ('Paypal', 'Paypal'),
        ('GooglePay', 'Google Pay'),
        ('ApplePay', 'Apple Pay'),
    ]

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_available_payment_methods')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='business_available_payment_methods')

    method_type = models.CharField(choices=METHOD_TYPE_CHOICES, max_length=100, default='Cash')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


class BusinessTax(models.Model):
    TAX_TYPES = [
        ('Individual', 'Individual'),
        ('Group', 'Group'),
        ('Location', 'Location'),
    ]
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_tax')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='business_tax')

    tax_type = models.CharField(choices=TAX_TYPES, default='Individual', max_length=20)
    name = models.CharField(default='', max_length=100)
    parent_tax = models.ManyToManyField('BusinessTax', blank=True, )
    tax_rate = models.FloatField(default=0, null=True, blank=True)
    location = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='locations_taxs')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=now)

    def is_individual(self):
        return self.tax_type == BusinessTax.TAX_TYPES[0][0]
    
    def is_group(self):
        return self.tax_type == BusinessTax.TAX_TYPES[1][0]
    
    def is_location(self):
        return self.tax_type == BusinessTax.TAX_TYPES[2][0]

    def __str__(self):
        return str(self.id)


class BusinessVendor(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_vendors')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='business_vendors')

    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='country_vendors')
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, related_name='state_vendors')
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='city_vendors')

    vendor_name = models.CharField(max_length=500, default='')
    address = models.TextField(default='')

    latitude = models.CharField(default='', max_length=200, null=True, blank=True)
    longitude = models.CharField(default='', max_length=200, null=True, blank=True)
    postal_code = models.CharField(max_length=30, default='')
    gstin = models.CharField(default='', max_length=1000, null=True, blank=True)
    website = models.TextField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    is_email_verified = models.BooleanField(default=False, null=True, blank=True)

    mobile_number = models.CharField(max_length=30, null=True, blank=True)
    is_mobile_verified = models.BooleanField(default=False)

    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


class BusinessTaxSetting(models.Model):
    SETTING_TYPE = [
        ('Combined', 'Combined'),
        ('Seperately', 'Seperately')
    ]

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_tax_setting')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_tax_setting')
    tax_setting = models.CharField(max_length=15, choices=SETTING_TYPE, default='Combined')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return str(self.id)
    

    def is_combined(self):
        return self.tax_setting == BusinessTaxSetting.SETTING_TYPE[0][0]
    
    def is_seperately(self):
        return self.tax_setting == BusinessTaxSetting.SETTING_TYPE[1][0]


class BusinessPrivacy(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_privacies')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_privacies')

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title


class BusinessPolicy(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_policies')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_policies')

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title