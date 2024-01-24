from datetime import datetime, timedelta
import uuid
from xml.parsers.expat import model
from django.db import models
from django.db.models import Sum, Subquery, OuterRef, FloatField, Case, When, Value, CharField, F, DateTimeField, Q
from django.db.models.functions import Coalesce

from Authentication.models import User
from Business.models import Business, BusinessAddress, BusinessTaxSetting, BusinessTax
from django.utils.timezone import now

from Promotions.models import Coupon
from Service.models import Service, PriceService
from Client.models import Client, Membership, Promotion, Rewards, Vouchers, LoyaltyPointLogs
from Employee.models import Employee
from Utility.Constants.Data.Durations import DURATION_CHOICES_DATA
from Order.models import Checkout
from . import choices
from Utility.models import CommonField
from .choices import AppointmentServiceStatus



class AppointmentCheckoutManager(models.QuerySet):

    def with_subtotal(self):
        """
        Return the subtotal.
        subtotal: total_price + gst_price + gst_price1
        """
        status_list = [
            AppointmentServiceStatus.STARTED, 
            AppointmentServiceStatus.FINISHED,
            AppointmentServiceStatus.BOOKED
        ]
        sum_filter=Q(appointment__appointment_services__status__in=status_list)
        return self.annotate(
            subtotal=Coalesce(
                Sum('appointment__appointment_services__price', filter=sum_filter) + F('gst_price') + F('gst_price1'),
                0.0,
                output_field=FloatField()
            ),
            just_services_price_inside=Coalesce(
                Sum(F('appointment__appointment_services__price'), filter=sum_filter),
                0.0,
                output_field=FloatField()
            ),
        )
    
    def with_payment_status(self):
        return self.annotate(
            payment_status=Case(
                    When(appointment__status=choices.AppointmentStatus.DONE, then=Value(choices.PaymentChoices.PAID)),
                    default=Value(choices.PaymentChoices.UNPAID)
                )
            )
    
    def with_client_name(self):
        return self.annotate(
            client_name=Coalesce(F('appointment__client__full_name'), Value(None), output_field=CharField())
        )
    
    def with_payment_date(self):
        return self.annotate(
            payment_date=Case(
                    When(appointment__status=choices.AppointmentStatus.DONE, then=F('updated_at')),
                    default=Value(None)
                    ),
        )

    def with_total_tax(self):
        return self.annotate(
            total_tax=Coalesce(
                F('gst_price') + F('gst_price1'),
                0.0,
                output_field=FloatField()
            )
        )


class AppointmentLogs(models.Model):
    LOG_TYPE_CHOICES =[
        ('Create' , 'Create'),
        ('Edit', 'Edit'),
        ('Reschedule', 'Reschedule'),
        ('Cancel', 'Cancel'),
        ('done', 'Done'),
    ]

    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    member = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name='appointmentlogs_staffname', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='user_appointments_logs')

    
    location = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointmentlogs_location')

    log_type = models.CharField(choices=LOG_TYPE_CHOICES, max_length=50, null=True, blank=True, )
    customer_type =  models.CharField(max_length=50, null=True, blank=True, default='' )
    # not in use : customer_type

    appointment = models.ForeignKey('Appointment', on_delete=models.SET_NULL, related_name='appointmentlogs_service_type', null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    
    def __str__(self):
        return str(self.id)
    

class LogDetails(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    log = models.ForeignKey(AppointmentLogs, on_delete=models.CASCADE, related_name='appointment_log_details')
    appointment_service = models.ForeignKey('AppointmentService', on_delete=models.CASCADE, related_name='app_service_logs')

    start_time = models.TimeField()
    duration = models.CharField(default='', max_length=400)
    member = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name='member_log_details', null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)


    def __str__(self):
        return str(self.id)


class Appointment(models.Model):
    DISCOUNT_CHOICES =[
        ('Promotions' , 'Promotions'),
        ('Rewards', 'Rewards'),
        ('Vouchers', 'Vouchers'),
        ('Memberships', 'Memberships'),
        ('Subscriptions', 'Subscriptions')
    ]
    TYPE_CHOICES = [
        ('IN HOUSE', 'IN HOUSE'),
        ('SALOON', 'SALOON'),
    ]
    PAYMENT_CHOICES = [
        ('Cash', 'Cash'),
        ('Voucher', 'Voucher'),
        ('SplitBill', 'SplitBill'),
        ('MasterCard', 'MasterCard'),
        ('Visa', 'Visa'),
        ('Paypal', 'Paypal'),
        ('GooglePay', 'Google Pay'),
        ('ApplePay', 'Apple Pay')
    ]
    
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_appointments', verbose_name='Creator ( User )')
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_appointments')

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_appointments', null=True, blank=True)
    business_address = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointment_address')
    member = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name='employee_appointments_lg', null=True, blank=True)
    status = models.CharField(max_length=100, choices=choices.AppointmentStatus.choices, null=True, blank=True)
    
    client_type= models.CharField(choices=TYPE_CHOICES, max_length=50, null=True, blank=True, )
    discount_type = models.CharField(max_length=50, choices= DISCOUNT_CHOICES, null=True, blank=True)
    payment_method = models.CharField(max_length=100, choices= PAYMENT_CHOICES, default='', null=True, blank=True)  
    
    extra_price  = models.FloatField(default=0, null=True, blank=True)
    tip  = models.FloatField(default=0, null=True, blank=True) # Not in Use
    
    discount_price  = models.FloatField(default=0, null=True, blank=True)
    discount_percentage = models.FloatField(default = 0 , null=True, blank=True)
    
    service_commission = models.FloatField(default = 0 , null=True, blank=True)    
    service_commission_type = models.CharField( max_length=50 , default = '')

    cancel_reason = models.CharField(max_length=150, null=True, blank=True)
    cancel_note = models.TextField(null=True)
    is_promotion = models.BooleanField(default=False)
    selected_promotion_id = models.CharField(default='', max_length=800)
    selected_promotion_type = models.CharField(default='', max_length=400)
    
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_checkout = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)


    def business_name(self):
        try:
            return str(self.business.business_name)

        except:
            return ''
        
    def get_booking_id(self):
        id = str(self.id).split('-')[0:2]
        id = ''.join(id)
        return id


    def __str__(self):
        return str(self.id)


class AppointmentServiceCustomManager(models.QuerySet):

    def with_appointment_subtotal(self):
        """
        Return the subtotal of all the realted AppointmentServices
        subtotal: toal_price
        """
        status_list = [
            AppointmentServiceStatus.STARTED, 
            AppointmentServiceStatus.FINISHED,
            AppointmentServiceStatus.BOOKED
        ]
        sum_filter=Q(appointment__appointment_services__status__in=status_list)
        return self.annotate(
            subtotal=Coalesce(
                Sum('appointment__appointment_services__total_price', filter=sum_filter) ,
                0.0,
                output_field=FloatField()
            )
        )
    
    def get_active_appointment_services(self, *args, **kwargs):
        return self.filter(
            status__in = [
                choices.AppointmentServiceStatus.BOOKED,
                choices.AppointmentServiceStatus.FINISHED,
                choices.AppointmentServiceStatus.STARTED,
            ],
            **kwargs
        )

    
class AppointmentService(models.Model):
    
    BOOKED_CHOICES = [
        ('Appointment_Booked',  'Appointment Booked'),
        ('Arrived', 'Arrived'),
        ('In Progress', 'In Progress'),
        ('Done', 'Done'),
        ('Paid', 'Paid'),
        ('Cancel', 'Cancel'),
    ]

    REDEEMED_TYPES = [
        ('Voucher', 'Voucher'),
        ('Membership', 'Membership')
    ]
    
    REFUND_STATUS = [
        ('refund','Refund'),
        ('cancel','Cancel')
    ]

    
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_appointment_services', verbose_name='Creator ( User )')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True, blank=True, related_name='business_appointment_services')
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True, related_name='appointment_services')
    business_address = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='b_address_appointment_services')

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='serivce_appointments', null=True, blank=True) # This is 
    member = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name='member_appointments', null=True, blank=True)
    is_favourite = models.BooleanField(default = False)
        
    appointment_date = models.DateField()
    appointment_time = models.TimeField(verbose_name='Appointment Start Time')

    duration = models.CharField(max_length=100, default='')
    
    client_can_book = models.CharField(max_length=100, default='', null=True, blank=True)
    slot_availible_for_online = models.CharField(max_length=100, default='', null=True, blank=True,)
    
    # Need to add refund
    # is_refund = models.CharField(choices = REFUND_STATUS,max_length = 50, default='', null=True, blank=True)
    # previous_app_service_refunded = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='app_service_refunded')
    
    
    # still using appointment_status in some places but status should be used now
    appointment_status = models.CharField(choices=BOOKED_CHOICES, max_length=100, default='Appointment Booked')
    status = models.CharField(max_length=100, choices=choices.AppointmentServiceStatus.choices, null=True, blank=True)
    tip = models.FloatField(default=0, null=True, blank=True) # Not in Use
    price = models.FloatField(default=0, null=True, blank=True)
    
    service_commission = models.FloatField(default = 0 , null=True, blank=True)    
    service_commission_type = models.CharField( max_length=50 , default = '')
    
    discount_price = models.FloatField(default=None, null=True, blank=True)    
    discount_percentage = models.FloatField(default = 0 , null=True, blank=True)

    total_price = models.FloatField(default = 0 , null=True, blank=True)
    service_start_time = models.DateTimeField(default=None, null=True)
    service_end_time = models.DateTimeField(default=None, null=True)

    # redeemed attributes
    is_redeemed = models.BooleanField(default=False)
    redeemed_type = models.CharField(default='', max_length=300)
    redeemed_price = models.FloatField(default=0)
    redeemed_instance_id = models.CharField(default='', max_length=800)
    
    
    end_time = models.TimeField(null=True, blank=True)
    details = models.CharField(max_length=255, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)

    client_tag = models.CharField(max_length=50, default='')
    client_type = models.CharField(max_length=50, default='')
    
    reason = models.CharField(max_length=100, null=True, blank=True)
    
    objects = AppointmentServiceCustomManager.as_manager()


    def get_final_price(self):
        """
        Only slight changes to reflect the Non None values
        a real meaning.
        """
        if self.is_redeemed == True:
            return round(self.redeemed_price, 2)
        elif self.discount_price is not None:
            price = self.discount_price
            return round(price, 2)
        elif self.price:
            price = self.price
            return round(price, 2)
        else:
            price = self.total_price
            return round(price, 2)

        
    
    def member_name(self):
        try:
            return str(self.member.full_name)
        except:
            return None

    def appointment_end_time(self):
        app_date_time = f'2000-01-01 {self.appointment_time}'

        try:
            duration = DURATION_CHOICES_DATA[self.duration]
            app_date_time = datetime.fromisoformat(app_date_time)
            datetime_duration = app_date_time + timedelta(minutes=duration)
            datetime_duration = datetime_duration.strftime('%H:%M:%S')
            return datetime_duration
        except Exception as err:
            return str(err)
    

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.price
        
        if self.status == choices.AppointmentServiceStatus.FINISHED and self.appointment and self.appointment.client and self.appointment.status in [choices.AppointmentStatus.DONE, choices.AppointmentStatus.FINISHED]:
            client = self.appointment.client
            client_f_month = int(client.created_at.strftime('%m'))
            # client_f_month = 10

            apps_services = AppointmentService.objects.filter(
                appointment__client = self.appointment.client,
                status = choices.AppointmentServiceStatus.FINISHED,
            )
            
            client_appointments = Appointment.objects.filter(
                client = client,
                status__in = [choices.AppointmentStatus.DONE, choices.AppointmentStatus.FINISHED]
            )
            # total_spend = AppointmentCheckout.objects.filter(appointment__client=client, appointment=self.appointment)
            price = 0
            for ck in apps_services:
                price = price + ck.get_final_price()
            
            last_month = int(datetime.now().strftime('%m'))
            months = max(last_month - client_f_month , 1)

            if client_appointments.count() >= months:
                tag = 'Most Visitor'
            else:
                tag = 'Least Visitor'

            monthly_spending = price / months
            if monthly_spending >= 100:
                client_type = 'Most Spender'
            else:
                client_type = f'{price}/{months}/{monthly_spending}'

            client.client_tag = tag
            client.client_type = client_type
            client.save()

    
        super(AppointmentService, self).save(*args, **kwargs)
    

    def __str__(self):
        return str(self.id)


class AppointmentCheckout(models.Model):
    PAYMENT_CHOICES = [
        ('Cash', 'Cash'),
        ('Voucher', 'Voucher'),
        ('SplitBill', 'SplitBill'),
        ('MasterCard', 'MasterCard'),
        ('Visa', 'Visa'),
        ('Paypal', 'Paypal'),
        ('GooglePay', 'Google Pay'),
        ('ApplePay', 'Apple Pay')
    ]
    
    REFUND_STATUS = [
        ('refund','Refund'),
        ('cancel','Cancel')
    ]
    
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True , related_name='appointment_checkout')
    appointment_service = models.ForeignKey(AppointmentService, on_delete=models.CASCADE, null=True, blank=True ,related_name='appointment_service_checkout') # this is not in use
    coupon_discounted_price = models.FloatField(null=True)
    
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='coupon_appointment_checkout', null=True)
    
    payment_method = models.CharField(max_length=100, choices= PAYMENT_CHOICES, default='', null=True, blank=True)  
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='checkout_service_appointments', null=True, blank=True) # This is being using to fetch the prices of the Services
    member = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='checkout_member_appointments', null=True, blank=True)
    business_address = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointment_address_checkout')
    is_coupon_redeemed = models.TextField(null=True)
    
    voucher =models.ForeignKey(Vouchers, on_delete=models.CASCADE, related_name='checkout_voucher_appointments', null=True, blank=True) 
    promotion =models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='checkout_promotion_appointments', null=True, blank=True) 
    membership =models.ForeignKey(Membership, on_delete=models.CASCADE, related_name='checkout_membership_appointments', null=True, blank=True) 
    rewards =models.ForeignKey(Rewards, on_delete=models.CASCADE, related_name='checkout_reward_appointments', null=True, blank=True) 
    
    # Added new fields for managing refunds Parent, child relation (original_checkout, refunded_checkout)
    
    is_refund = models.CharField(choices = REFUND_STATUS, max_length = 50 ,default='', null=True, blank=True)
    previous_checkout = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='refund_checkout')
    
    tip = models.FloatField(default=0, null=True, blank=True) # this field is not in use
    gst = models.FloatField(default=0, null=True, blank=True)
    gst1 = models.FloatField(default=0, null=True, blank=True)
    gst_price = models.FloatField(default=0, null=True, blank=True)
    gst_price1 = models.FloatField(default=0, null=True, blank=True)
    tax_name = models.CharField(max_length=250, default='')
    tax_name1 = models.CharField(max_length=250, default='')
    
    service_price = models.FloatField(default=0, null=True, blank=True)
    total_price = models.FloatField(default=0, null=True, blank=True)
    
    service_commission = models.DecimalField(default = 0 , null=True, blank=True, decimal_places=5, max_digits=8)    
    service_commission_type = models.CharField( max_length=50 , default = '')


    is_promotion = models.BooleanField(default=False)
    selected_promotion_id = models.CharField(default='', max_length=800)
    selected_promotion_type = models.CharField(default='', max_length=400)
    """
        Direct Or Flat
        Specific Group Discount
        Purchase Discount
        Specific Brand Discount
        Spend_Some_Amount
        Fixed_Price_Service
        Mentioned_Number_Service
        Bundle_Fixed_Service
        Retail_and_Get_Service
        User_Restricted_discount
        Complimentary_Discount
        Packages_Discount
    """
    
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    objects = AppointmentCheckoutManager.as_manager()
    
    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if self.appointment and self.appointment.is_promotion:

            self.is_promotion = self.appointment.is_promotion
            self.selected_promotion_id = self.appointment.selected_promotion_id
            self.selected_promotion_type = self.appointment.selected_promotion_type

        super(AppointmentCheckout, self).save(*args, **kwargs)

    def get_client_loyalty_points(self):
        if self.appointment.client:
            redeemed_points_obj = LoyaltyPointLogs.objects.filter(client=self.appointment.client,
                                                              location=self.business_address) \
                                                        .order_by('-created_at')
            if redeemed_points_obj:
                return redeemed_points_obj[0].points_redeemed
            else:
                return None
        else:
            return None
        

    def get_total_tax(self):
        """
        A helper method to add total tax.
        """
        total = 0
        if self.gst_price:
            total += self.gst_price
        if self.gst_price1:
            total += self.gst_price1
        return total
    
    def total_service_price(self):
        currency = self.business_address.currency
        query_for_price = Q(service=OuterRef('service'), currency=currency)        
        appointment_service = AppointmentService.objects \
                                        .filter(appointment=self.appointment) \
                                        .annotate(
                                            service_price=Coalesce(
                                                PriceService.objects \
                                                .filter(query_for_price) \
                                                .order_by('-created_at') \
                                                .values('price')[:1],
                                                0.0,
                                                output_field=FloatField()
                                            )
                                            
                                        ).aggregate(
                                            final_price=Sum('service_price')
                                        )
        return appointment_service['final_price']
    
    def apply_taxes(self):
        """
        Calculating the Tax and Total Price
        """

        # default values if either is not calculated
        gst_price = 0
        gst_price1 = 0

        total_price = self.void_excluded_services_price()
        tax_setting = BusinessTaxSetting.objects.get(business=self.appointment.business)
        business_tax = BusinessTax.objects.filter(location=self.appointment.business_address).first()
        parent_tax = business_tax.parent_tax.all()[0]
        parent_taxes = parent_tax.parent_tax.all()

        # workaround here
        if parent_tax.is_individual():
            parent_taxes = [parent_tax]

        if tax_setting.is_combined():
            gst_price = round((parent_taxes[0].tax_rate * total_price / 100), 2)
            if parent_tax.is_group():
                gst_price1 = round((parent_taxes[1].tax_rate * total_price / 100), 2)

        elif tax_setting.is_seperately():
            gst_price = round((parent_taxes[0].tax_rate * total_price / 100), 2)
            if parent_tax.is_group():
                total_price += gst_price
                gst_price1 = round((parent_taxes[1].tax_rate * total_price / 100), 2)

        self.gst_price = gst_price
        self.gst_price1 = gst_price1
        self.save()


    def void_excluded_services_price(self):
        """
        Calculate the appointment services price (VOID excluded)
        """
        return AppointmentService.objects \
            .filter(appointment=self.appointment) \
            .exclude(status=choices.AppointmentServiceStatus.VOID) \
            .aggregate(total_price=Sum('price'))['total_price']
    
    @property
    def fun():
        return 'rewards'

class AppointmentEmployeeTip(models.Model):    
    
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True , related_name='tips_checkout')    
    member = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='checkout_member_tips', null=True, blank=True)
    
    business_address = models.ForeignKey(BusinessAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointment_address_tips')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True, blank=True, related_name='business_appointment_tips') 

    checkout = models.ForeignKey(Checkout, on_delete=models.CASCADE,related_name="checkout_tips", null=True, blank=True)

    tip = models.FloatField(default=0, null=True, blank=True)
    gst = models.FloatField(default=0, null=True, blank=True)
    gst_price = models.FloatField(default=0, null=True, blank=True)
    
    service_price = models.FloatField(default=0, null=True, blank=True)
    total_price = models.FloatField(default=0, null=True, blank=True)
    
    
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=now)
    
    def __str__(self):
        return str(self.id)



class AppointmentNotes(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='appointment_notes')
    
    text = models.TextField(default='', null=True, blank=True)
    
    def __str__(self):
        return str(self.id)

class ClientMissedOpportunity(CommonField):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_missed_opportunities', null=True)
    location = models.ForeignKey(BusinessAddress, on_delete=models.CASCADE, related_name='location_missed_opportunities', null=True)
    client_type = models.CharField(max_length=200, choices=choices.ClientType.choices, null=True, blank=True)
    dependency = models.CharField(max_length=200, choices=choices.MissedOpportunityReason.choices, null=True, blank=True)
    note = models.TextField(null=True)
    date_time = models.DateTimeField()

class OpportunityEmployeeService(CommonField):
    client_missed_opportunity = models.ForeignKey(ClientMissedOpportunity, on_delete=models.CASCADE ,related_name='missed_opportunities', null=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='service_missed_opportunities')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_missed_opportunities')
    duration = models.CharField(default='', max_length=200)
    time = models.TimeField()


class Reversal(CommonField):
    email = models.TextField(null=True)
    description = models.TextField(null=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True)
    appointment_services = models.ForeignKey(AppointmentService, on_delete=models.CASCADE, null=True)
    request_status = models.TextField(default="void",null=True)
    d