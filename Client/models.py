from datetime import timezone
from datetime import datetime
import pytz

from itertools import count
from django.db import models

from uuid import uuid4
from Authentication.models import User
from Business.models import Business, BusinessAddress
from django.db import connection
from django.db.models import Subquery, OuterRef, DateTimeField, Count, Case, When, F, IntegerField, Value
from django.db.models.functions import Coalesce
from django.apps import apps
from Utility.models import Country, Currency, Language, State, City
from django.utils.timezone import now
from Product.models import Product
from Service.models import Service
import uuid
from googletrans import Translator
from dateutil.relativedelta import relativedelta
from django.db.models import Count, Q
from django.db.models.functions import Coalesce
# from Appointment.models import AppointmentService
# from Order.models import Checkout


class ClientManager(models.QuerySet):

    def with_last_transaction_date(self):
        """
        This custom queryset is used to get the last transaction date of (either Appointment or Sale)
        of a particular client and then compare them to find the least one.
        
        """
        AppointmentCheckout = apps.get_model(app_label='Appointment', model_name='AppointmentCheckout')
        last_appointment_subquery = AppointmentCheckout.objects \
                                        .filter(appointment__client=OuterRef('pk')) \
                                        .order_by('-created_at') \
                                        .values('updated_at')[
                                    :1]  # why updated_at -> because it can be created but not paid
        Checkout = apps.get_model(app_label='Order', model_name='Checkout')
        last_sale_subquery = Checkout.objects \
                                 .filter(client=OuterRef('pk')) \
                                 .order_by('-created_at') \
                                 .values('created_at')[:1]
        # some sort of validations
        appointment_query = Q(last_appointment_date__isnull=False,
                              last_sale_date__isnull=True) | \
                            Q(last_appointment_date__gt=F('last_sale_date'))
        # some sort of validations
        sale_query = Q(last_appointment_date__isnull=True,
                       last_sale_date__isnull=False) | \
                     Q(last_appointment_date__lte=F('last_sale_date'))

        return self.annotate(
            last_appointment_date=Coalesce(Subquery(last_appointment_subquery),
                                           Value(None)),
            last_sale_date=Coalesce(Subquery(last_sale_subquery),
                                    Value(None))
        ).annotate(
            last_transaction_date=Case(
                When(appointment_query, then=F('last_appointment_date')),
                When(sale_query, then=F('last_sale_date')),
                output_field=DateTimeField(),
                default=Value(None)
            )
        )

    def count_total_visit(self, start_date=None, end_date=None):
        if start_date and end_date:
            appointment_filter = Q(created_at__range=(start_date, end_date))
            return self.annotate(
                total_visit=Coalesce(
                    Count('client_appointments', filter=appointment_filter),
                    0,
                    output_field=IntegerField()
                )
            )
        else:
            return self.annotate(
                total_visit=Coalesce(
                    Count('client_appointments'),
                    0,
                    output_field=IntegerField()
                )
            )


class Client(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Others', 'Others'),
    ]
    MARKETING_CHOICES = [
        ('opt_in', 'opt_in'),
        ('opt_out', 'opt_out'),
    ]
    ABOUT_CHOICES = [
        ('Facebook', 'Facebook'),
        ('Instagram', 'Instagram'),
        ('Twitter', 'Twitter'),
        ('Whatsapp', 'Whatsapp'),
        ('Community', 'Community'),
        ('Media_Ads', 'Media Ads'),
        ('Friends', 'Friends'),
    ]
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client', null=True, blank=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_client')

    # business_addess = models.ForeignKey(BusinessAddress, on_delete=models.CASCADE,  null=True, blank=True,  related_name='business_addess_client')

    full_name = models.CharField(max_length=300, default='')
    image = models.ImageField(upload_to='client/client_images/', null=True, blank=True)
    is_image_uploaded_s3 = models.BooleanField(default=False)

    client_id = models.CharField(max_length=50, default='')
    email = models.EmailField(default='')
    mobile_number = models.CharField(max_length=30, null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    is_mobile_verified = models.BooleanField(default=False)

    dob = models.DateField(verbose_name='Date of Birth', null=True, blank=True)
    gender = models.CharField(choices=GENDER_CHOICES, default='Male', max_length=20)

    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='country_clients')
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, related_name='state_clients')
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='city_clients')

    language = models.ForeignKey(Language, on_delete=models.SET_NULL, related_name='language_clients', null=True,
                                 blank=True, max_length=100)

    about_us = models.CharField(choices=ABOUT_CHOICES, default='Community', max_length=100)
    marketing = models.CharField(choices=MARKETING_CHOICES, default='opt_in', max_length=50)
    customer_note = models.CharField(max_length=255, null=True, blank=True, verbose_name='Customer Note')

    postal_code = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(default='')
    card_number = models.CharField(max_length=30, null=True, blank=True)

    is_default = models.BooleanField(default=False)

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    client_tag = models.CharField(max_length=50, default='')
    client_type = models.CharField(max_length=50, default='')

    objects = ClientManager.as_manager()

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if self.image:
            self.is_image_uploaded_s3 = True

        if not self.client_id:
            tenant = connection.get_tenant()

            tenant_name = str(tenant.domain).split('.')[0]
            tenant_name = tenant_name.split('-')
            tenant_name = [word[0].upper() for word in tenant_name if
                           word]  # Use upper() to capitalize letters and add a check to skip empty strings

            count = Client.objects.all().count()
            count += 1
            new_id = ''

            return_loop = True
            while return_loop:
                if 0 < count <= 9:
                    count = f'000{count}'
                elif 9 < count <= 99:
                    count = f'00{count}'
                elif 99 < count <= 999:
                    count = f'0{count}'
                new_id = f'{tenant_name}-CLI-{count}'

                try:
                    Client.objects.get(client_id=new_id)
                    count += 1
                except:
                    return_loop = False
                    break

            self.client_id = new_id
        super(Client, self).save(*args, **kwargs)


class ClientImages(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='avaliableclient/images/', null=True, blank=True)
    is_image_uploaded_s3 = models.BooleanField(default=False)
    file_name = models.TextField(null=True, blank=True)
    file_type = models.TextField(null=True, blank=True)


class ClientGroup(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_client_group')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_client_group')

    email = models.EmailField(default='', null=True, blank=True)
    name = models.CharField(max_length=300, default='')

    client = models.ManyToManyField(Client, related_name='group_clients')

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


class Subscription(models.Model):
    AMOUNT_CHOICES = [
        ('Limited', 'Limited'),
        ('Unlimited', 'Unlimited'),
    ]
    SUBSCRIPTION_TYPES = [
        ('Product', 'Product'),
        ('Service', 'Service'),
    ]

    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_subscriptions')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_subscriptions')

    subscription_type = models.CharField(default='Product', choices=SUBSCRIPTION_TYPES, max_length=20)

    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='product_subscriptions')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='service_subscriptions')

    name = models.CharField(max_length=300, default='')
    days = models.PositiveIntegerField(default=0, verbose_name='Number of Days')
    select_amount = models.FloatField(default=0)
    services_count = models.FloatField(default=0, verbose_name='Total Number of Services')
    products_count = models.FloatField(default=0, verbose_name='Total Number of Products')
    price = models.FloatField(default=0, verbose_name='Subscription Price')

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


class Promotion(models.Model):
    VALIDITY_DAY = [
        ('7 Days', '7 Days'),
        ('14 Days', '14 Days'),
        ('1 Month', '1 Months'),
        ('2 Months', '2 Months'),
        ('3 Months', '3 Months'),
        ('4 Months', '4 Months'),
        ('6 Months', '6 Months'),
        ('8 Months', '8 Months'),
        ('1 Years', '1 Years'),
        ('18 Months', '18 Months'),
        ('2 Years', '2 Years'),
        ('5 Years', '5 Years'),
    ]
    PROMOTION_TYPES = [
        ('Product', 'Product'),
        ('Service', 'Service'),
    ]

    DISCOUNT_DURATION = [
        ('Day', 'Day'),
        ('Month', 'Month'),
    ]

    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_promotions')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_promotions')

    name = models.CharField(max_length=100, default='', verbose_name='Promotion Name')
    promotion_type = models.CharField(default='Service', choices=PROMOTION_TYPES, max_length=20)

    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='service_promotions')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='product_promotions')

    purchases = models.FloatField(verbose_name='No. of Purchases', default=0, null=True, blank=True)

    discount = models.FloatField(default=0)

    valid_til = models.CharField(choices=VALIDITY_DAY, default='7 Days', null=True, blank=True,
                                 verbose_name='No of Days/Month', max_length=100)

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


class VoucherManager(models.QuerySet):

    def with_total_orders(self):
        return self.annotate(
            total_orders=Coalesce(
                Count('voucher_orders'),
                0,
                output_field=IntegerField()
            )
        )


class Vouchers(models.Model):
    VALIDITY_CHOICE = [
        ('Days', 'Days'),
        ('Months', 'Months'),
    ]
    VOUCHER_CHOICES = [
        ('Product', 'Product'),
        ('Service', 'Service'),
    ]
    VALIDITY_DAY = [
        ('7 Days', '7 Days'),
        ('14 Days', '14 Days'),
        ('1 Months', '1 Months'),
        ('2 Months', '2 Months'),
        ('3 Months', '3 Months'),
        ('4 Months', '4 Months'),
        ('6 Months', '6 Months'),
        ('8 Months', '8 Months'),
        ('1 Years', '1 Years'),
        ('18 Months', '18 Months'),
        ('2 Years', '2 Years'),
        ('5 Years', '5 Years'),
    ]
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_voucher',
                             verbose_name='Creator ( User )')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='business_voucher')
    name = models.CharField(max_length=100, default='')
    arabic_name = models.CharField(max_length=999, default='')
    voucher_type = models.CharField(choices=VOUCHER_CHOICES, default='Product', verbose_name='Voucher Type',
                                    max_length=20)
    discount_percentage = models.FloatField(default=0, blank=True, null=True)
    validity = models.CharField(choices=VALIDITY_DAY, default='7 Days', verbose_name='No of Days/Month', max_length=100)

    sales = models.FloatField(default=0)
    price = models.FloatField(default=0)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    objects = VoucherManager.as_manager()

    def save(self, *args, **kwargs):
        translator = Translator()
        arabic_text = translator.translate(f'{self.name}'.title(), src='en', dest='ar')
        self.arabic_name = arabic_text.text

        super(Vouchers, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)


class VoucherCurrencyPrice(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)

    voucher = models.ForeignKey(Vouchers, on_delete=models.CASCADE, related_name='voucher_vouchercurrencyprice')
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.FloatField(default=0)

    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Rewards(models.Model):
    REWARD_TYPES = [
        ('Product', 'Product'),
        ('Service', 'Service'),
    ]
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_reward',
                             verbose_name='Creator ( User )')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='business_reward')

    name = models.CharField(max_length=100, default='')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='service_rewards')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='product_rewards')

    reward_value = models.FloatField(default=0)
    reward_point = models.FloatField(default=0)
    reward_type = models.CharField(default='Product', choices=REWARD_TYPES, max_length=20)

    total_points = models.FloatField(default=0)
    discount = models.FloatField(default=0)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.id)


class MembershipManager(models.QuerySet):

    def with_total_orders(self):
        return self.annotate(
            total_orders=Coalesce(
                Count('membership_orders'),
                0,
                output_field=IntegerField()
            )
        )


class Membership(models.Model):
    MEMBERSHIP_CHOICES = [
        ('Product', 'Product'),
        ('Service', 'Service'),
    ]
    VALIDITY_CHOICE = [
        ('7 Days', '7 Days'),
        ('14 Days', '14 Days'),
        ('1 Months', '1 Months'),
        ('2 Months', '2 Months'),
        ('3 Months', '3 Months'),
        ('4 Months', '4 Months'),
        ('6 Months', '6 Months'),
        ('8 Months', '8 Months'),
        ('1 Years', '1 Years'),
        ('18 Months', '18 Months'),
        ('2 Years', '2 Years'),
        ('5 Years', '5 Years'),
    ]
    DISCOUNT_CHOICE = [
        ('Limited', 'Limited'),
        ('Free', 'Free'),
    ]

    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_memberships')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_memberships')

    name = models.CharField(max_length=100, default='')
    arabic_name = models.CharField(max_length=999, default='')

    description = models.CharField(max_length=300, null=True, blank=True)
    percentage = models.FloatField(default=0)

    valid_for = models.CharField(choices=VALIDITY_CHOICE, default='7 Days', verbose_name='Validity for Days or Months',
                                 max_length=20)
    discount = models.CharField(choices=DISCOUNT_CHOICE, default='Unlimited', verbose_name='Discount Limit',
                                max_length=20)

    term_condition = models.CharField(max_length=300, null=True, blank=True)

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(null=True, blank=True)

    objects = MembershipManager.as_manager()

    def save(self, *args, **kwargs):
        translator = Translator()
        arabic_text = translator.translate(f'{self.name}'.title(), src='en', dest='ar')
        self.arabic_name = arabic_text.text

        super(Membership, self).save(*args, **kwargs)

    def is_expired(self):
        """
        This functions is used to check tthe expiration of Membership
        based on the valid_for attribute.
        """

        split_them = self.valid_for.split(" ")
        utc = pytz.UTC
        duration = int(split_them[0])
        term = split_them[1]
        validity_time = None

        if term == 'Days':
            validity_time = self.created_at + relativedelta(months=duration)
        elif term == 'Months':
            validity_time = self.created_at + relativedelta(months=duration)
        elif term == 'years':
            validity_time = self.created_at + relativedelta(years=duration)

        if validity_time:
            current_time = datetime.now(tz=pytz.UTC)
            if validity_time >= current_time:
                return True
            else:
                return False

    def __str__(self):
        return str(self.id)


class DiscountMembership(models.Model):
    DURATION_CHOICE = [
        ('7 Days', '7 Days'),
        ('14 Days', '14 Days'),
        ('1 Month', '1 Month'),
    ]
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)

    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='membership_discountmembership')
    duration = models.CharField(choices=DURATION_CHOICE, default='7 Days', verbose_name='Duration', max_length=50,
                                null=True, blank=True, )
    percentage = models.FloatField(default=0)

    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='service_memberships')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='product_memberships')

    def __str__(self):
        return str(self.id)


class CurrencyPriceMembership(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)

    membership = models.ForeignKey(Membership, on_delete=models.CASCADE,
                                   related_name='membership_currenypricemembership')
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.FloatField(default=0)

    def __str__(self):
        return str(self.id)


# now = datetime.now()
class LoyaltyPoints(models.Model):
    LOYALTY_CHOICE = [
        ('Service', 'Service'),
        ('Retail', 'Retail'),
        ('Both', 'Both'),

    ]
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='user_loyalty',
                             verbose_name='Creator ( User )')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='business_loyalty')
    location = models.ForeignKey(BusinessAddress, on_delete=models.CASCADE, related_name='location_loyaltypoints',
                                 null=True, blank=True)

    name = models.CharField(max_length=100, default='')
    loyaltytype = models.CharField(choices=LOYALTY_CHOICE, default='Service', verbose_name='Loyalty Type',
                                   max_length=50)
    amount_spend = models.FloatField(default=0, null=True, blank=True)
    number_points = models.FloatField(default=0, null=True, blank=True)
    earn_points = models.FloatField(default=0, null=True, blank=True)
    total_earn_from_points = models.FloatField(default=0, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now, null=True)  # null = True, default= datetime.now() )

    def __str__(self):
        return str(self.id)


class ClientLoyaltyPoint(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)

    location = models.ForeignKey(BusinessAddress, on_delete=models.CASCADE,
                                 related_name="location_client_loyalty_points")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="client_loyalty_points")
    loyalty_points = models.ForeignKey(LoyaltyPoints, on_delete=models.CASCADE, related_name="loyalty_points_clients")

    total_amount = models.FloatField(default=0, null=True, blank=True,
                                     verbose_name='Number of Total Amount (Amount to Spend)')
    total_earn = models.FloatField(default=0, null=True, blank=True, verbose_name='Total Number Of Points')

    points_redeemed = models.FloatField(default=0, verbose_name='Total Number Of Points Redeemed')

    for_every_points = models.PositiveIntegerField(default=0, null=True, blank=True,
                                                   verbose_name='For every (this) points')
    customer_will_get_amount = models.FloatField(default=0, null=True, blank=True,
                                                 verbose_name='a customer will get (this) amount')
    invoice = models.CharField(max_length=128, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=now, null=True)
    updated_at = models.DateTimeField(auto_now_add=now, null=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

    @property
    def total_available_points(self):
        return self.total_earn - self.points_redeemed

    @property
    def is_redeemable(self):
        return True

    def __str__(self):
        return str(self.id)


class LoyaltyPointLogs(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    location = models.ForeignKey(BusinessAddress, on_delete=models.CASCADE, related_name="location_loyaltypointlogs")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="client_loyaltypointlogs")
    client_points = models.ForeignKey(ClientLoyaltyPoint, on_delete=models.CASCADE, related_name="client_points_logs",
                                      null=True, blank=True)

    loyalty = models.ForeignKey(LoyaltyPoints, on_delete=models.CASCADE, related_name="loyalty_points_logs", null=True,
                                blank=True)

    points_earned = models.FloatField(default=0, null=True, blank=True)
    points_redeemed = models.FloatField(default=0)
    balance = models.FloatField(default=0, null=True, blank=True)
    actual_sale_value_redeemed = models.FloatField(default=0)

    invoice = models.CharField(max_length=128, null=True, blank=True)
    checkout = models.CharField(max_length=128, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=now, null=True)
    updated_at = models.DateTimeField(auto_now_add=now, null=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

    @property
    def short_id(self):
        instance_id = f'{self.id}'
        instance_id = instance_id.split('-')
        if len(instance_id) > 0:
            return f'{instance_id[0]}'

        return ''

    def __str__(self):
        return str(self.id)


class ClientPromotions(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='user_client_promotions',
                             verbose_name='Creator ( User )')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='business_client_promotions')

    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True,
                               related_name='client_client_promotions')
    complimentary = models.ForeignKey('Promotions.ComplimentaryDiscount', on_delete=models.SET_NULL, null=True,
                                      blank=True, related_name='complimentry_client_promotions')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True,
                                related_name='service_client_promotions')

    visits = models.PositiveIntegerField(default=0, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now, null=True)

    def __str__(self):
        return str(self.id)


class ClientPackageValidation(models.Model):
    id = models.UUIDField(default=uuid4, unique=True, editable=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='user_client_packagevalidation',
                             verbose_name='Creator ( User )')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='business_client_packagevalidation')

    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True,
                               related_name='client_client_packagevalidation')
    package = models.ForeignKey('Promotions.PackagesDiscount', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='package_client_packagevalidation')
    serviceduration = models.ForeignKey('Promotions.ServiceDurationForSpecificTime', on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='serviceduration_client_packagevalidation')
    service = models.ManyToManyField(Service, related_name='service_client_packagevalidation')

    due_date = models.DateField(null=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now, null=True)

    def __str__(self):
        return str(self.id)
