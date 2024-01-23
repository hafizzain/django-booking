from cmath import e
from dataclasses import field
from pyexpat import model
from Appointment.models import AppointmentService
from Employee.models import EmployeDailySchedule, Employee
from Utility.models import Currency, ExceptionRecord, State, Country,City
from rest_framework import serializers
from datetime import datetime, timedelta
from Order.models import Checkout,Order
from django.contrib.gis.geoip2 import GeoIP2

from Business.models import (BookingSetting, BusinessAddressMedia, BusinessType, Business, 
                             BusinessAddress, BusinessSocial, BusinessTheme, StaffNotificationSetting, 
                             ClientNotificationSetting, AdminNotificationSetting, StockNotificationSetting, 
                             BusinessPaymentMethod, BusinessTax, BusinessVendor,BusinessOpeningHour,
                             BusinessTaxSetting, BusinessPolicy, BusinessPrivacy
                        )
from Authentication.serializers import UserSerializer
from django.conf import settings

from Product.Constants.index  import tenant_media_base_url, tenant_media_domain
from Utility.serializers import CountrySerializer, StateSerializer, CitySerializer
from MultiLanguage.serializers import InvoiceTransSerializer

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        exclude = ['is_deleted', 'created_at', 'unique_code', 'key']
    
class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        exclude = ['is_deleted', 'created_at', 'unique_code', 'key']
        
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        exclude = ['is_deleted', 'created_at', 'unique_code', 'key']

class BusinessTypeSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        return obj.image_path
                
    class Meta:
        model = BusinessType
        fields = ['id', 'name', 'image', 'slug']

class BusinessGetSerializer(serializers.ModelSerializer):
    website = serializers.SerializerMethodField()
    facebook = serializers.SerializerMethodField()
    instagram = serializers.SerializerMethodField()
    business_types = serializers.SerializerMethodField()
    
    def get_business_types(obj, self):
        try:
            print(obj)
            obj_type = BusinessType.objects.get(id =obj)
            return obj_type
        except Exception as err:
            #print(err)
            return None

    def get_website(self, obj):
        try:
            social = BusinessSocial.objects.get(business=obj)
            return social.website
        except Exception as err:
            print(err)
            return None
    
    def get_facebook(self, obj):
        try:
            social = BusinessSocial.objects.get(business=obj)
            return social.facebook
        except:
            return None

    def get_instagram(self, obj):
        try:
            social = BusinessSocial.objects.get(business=obj)
            return social.instagram
        except:
            return None

    class Meta:
        model = Business
        fields = [
            'id',
            'business_name',
            'postal_code',
            'week_start',
            'team_size',
            'is_completed',
            'currency',
            'timezone',
            'time_format',
            'how_find_us',
            'website',
            'facebook',
            'instagram',
            'business_types'
        ]
class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class Business_GetSerializer(serializers.ModelSerializer):
    website = serializers.SerializerMethodField()
    facebook = serializers.SerializerMethodField()
    instagram = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()

    logo = serializers.SerializerMethodField()
    
    def get_currency(self, obj):
        if obj.currency:
            return CurrencySerializer(obj.currency).data
        else:
            request = self.context.get('request', None)
            if not request:
                return None

            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')

            try:
                g = GeoIP2()
                location = g.city(ip)
                location_country = location["country_code"]
            except:
                location_country = 'ae'

            currencies = Currency.objects.filter(code__icontains = location_country)
            if len(currencies) > 0:
                return CurrencySerializer(currencies[0]).data
            
            return None
    
    def get_logo(self, obj):
        if obj.logo :
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=obj.is_logo_uploaded_s3)
                return f'{url}{obj.logo}'
            except:
                obj.logo

        return None

    def get_website(self, obj):
        try:
            social = BusinessSocial.objects.get(business=obj)
            return social.website
        except Exception as err:
            print(err)
            return None
    
    def get_facebook(self, obj):
        try:
            social = BusinessSocial.objects.get(business=obj)
            return social.facebook
        except:
            return None

    def get_instagram(self, obj):
        try:
            social = BusinessSocial.objects.get(business=obj)
            return social.instagram
        except:
            return None

    class Meta:
        model = Business
        fields = [
            'id',
            'business_name',
            'logo',
            'is_logo_uploaded_s3',
            'banner',
            'postal_code',
            'week_start',
            'team_size',
            'is_completed',
            'currency',
            'timezone',
            'time_format',
            'how_find_us',
            'website',
            'facebook',
            'instagram',
            'business_types',
            'software_used'
        ]


class Business_PutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = [
            'business_name',
            'timezone',
            'time_format',
            'week_start',
        ]


class BusinessAddressMediaSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request, is_s3_url=obj.is_image_uploaded_s3)
                return f'{url}{obj.image}'
            except:
                return obj.image
        return None
    class Meta:
        model= BusinessAddressMedia
        fields= ['id', 'image']
        
class OpeningHoursSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= BusinessOpeningHour
        fields= '__all__'
class CurrencySerializer(serializers.ModelSerializer):
    
    class Meta:
        model= Currency
        fields= '__all__'

class ParentBusinessTax_RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessTax
        fields = ['id', 'name', 'parent_tax', 'tax_rate', 'tax_type', 'is_active']

class ParentBusinessTaxSerializer(serializers.ModelSerializer):
    # parent_tax = serializers.SerializerMethodField(read_only=True)
    
    # def get_parent_tax(self, obj):
    #     try:
    #         tax = obj.parent_tax.all()
    #         # ser = BusinessTax.objects.filter(service = obj).first()
    #         return tax.tax_rate
    #     except Exception as err:
    #         pass
    parent_tax = ParentBusinessTax_RateSerializer(many=True, read_only=True)

    class Meta:
        model = BusinessTax
        fields = ['id', 'name', 'parent_tax', 'tax_rate', 'location', 'tax_type', 'is_active']

class BusinessTaxBusinessAddressSerializer(serializers.ModelSerializer):

    parent_tax = ParentBusinessTaxSerializer(many=True, read_only=True)
    #location = BusinessAddress_GetSerializer()
    class Meta:
        model = BusinessTax
        fields = ['id', 'name', 'parent_tax',
                  'tax_rate', 'location', 'tax_type', 'is_active']
        
class BusinessAddress_GetSerializer(serializers.ModelSerializer):
    #opening_hours= OpeningHoursSerializer(read_only=True)
    opening_hours = serializers.SerializerMethodField(read_only=True)
    start_time=  serializers.SerializerMethodField(read_only=True)
    close_time= serializers.SerializerMethodField(read_only=True)
    currency = serializers.SerializerMethodField(read_only=True)
    images = serializers.SerializerMethodField(read_only=True)
    
    country = serializers.SerializerMethodField(read_only=True)
    state = serializers.SerializerMethodField(read_only=True)
    city = serializers.SerializerMethodField(read_only=True)
    businesstax = serializers.SerializerMethodField(read_only=True)

    def get_businesstax(self, obj):
        try:
            tax = BusinessTax.objects.get(location = obj)
            return BusinessTaxBusinessAddressSerializer(tax).data
        except Exception as err:
            print(err)
    
    def get_country(self, obj):
        try:
            return CountrySerializer(obj.country).data
        except Country.DoesNotExist:
            return None
    
    def get_state(self, obj):
        try:
            return StateSerializer(obj.state).data
        except State.DoesNotExist:
            return None
    
    def get_city(self, obj):
        try:
            return CitySerializer(obj.city).data
        except City.DoesNotExist:
            return None    
    
    def get_images(self, obj):
        try:
            image = BusinessAddressMedia.objects.get(business_address = obj)
            if image.image:
                try:
                    request = self.context["request"]
                    url = tenant_media_base_url(request, is_s3_url=image.is_image_uploaded_s3)
                    return f'{url}{image.image}'
                except:
                    return image.image
            return None
            #return BusinessAddressMediaSerializer(image, context=self.context).data
        except Exception as err:
            print(err)
            
    def get_currency(self, obj):
        try:
            currency = Currency.objects.get(id=obj.currency.id)
            return CurrencySerializer(currency).data
        
        except Exception as err:
            print(err)
    
    def get_opening_hours(self, obj):
        try:
            location = BusinessOpeningHour.objects.filter(business_address=obj).order_by('-created_at')
            return OpeningHoursSerializer(location, many=True).data
        
        except BusinessOpeningHour.DoesNotExist:
            return None

    def get_start_time(self, obj):
        try:
            location = BusinessOpeningHour.objects.get(
                business_address=obj,
                day__iexact = 'Monday'
            )
            return location.start_time
        except BusinessOpeningHour.DoesNotExist:
            return None
            
    def get_close_time(self, obj):
        try:
            location = BusinessOpeningHour.objects.get(
                business_address=obj,
                day__iexact = 'Monday'
            )
            return location.close_time
        except BusinessOpeningHour.DoesNotExist:
            return None

    class Meta:
        model = BusinessAddress
        fields = [
            'id',
            'country',
            'state',
            'city',
            'currency',
            'email',
            'mobile_number',
            'address',
            'address_name',
            'postal_code',
            'website',
            'businesstax',
            'is_primary',
            'banking',
            'start_time',
            'close_time',
            'service_avaiable',
            'location_name',
            'images',
            'opening_hours',
            'is_deleted',
            'is_publish',
            'description',
            'primary_translation',
            'secondary_translation',
            'privacy_policy'
        ]
class BusinessAddress_CustomerSerializer(serializers.ModelSerializer):
    #opening_hours= OpeningHoursSerializer(read_only=True)
    opening_hours = serializers.SerializerMethodField(read_only=True)
    start_time=  serializers.SerializerMethodField(read_only=True)
    close_time= serializers.SerializerMethodField(read_only=True)
    currency = serializers.SerializerMethodField(read_only=True)
    images = serializers.SerializerMethodField(read_only=True)
    
    country = serializers.SerializerMethodField(read_only=True)
    state = serializers.SerializerMethodField(read_only=True)
    city = serializers.SerializerMethodField(read_only=True)
    
    def get_country(self, obj):
        try:
            return CountrySerializer(obj.country).data
        except Country.DoesNotExist:
            return None
    def get_state(self, obj):
        try:
            return StateSerializer(obj.state).data
        except State.DoesNotExist:
            return None
    
    def get_city(self, obj):
        try:
            return CitySerializer(obj.city).data
        except City.DoesNotExist:
            return None    
    
    def get_images(self, obj):
        try:
            image = BusinessAddressMedia.objects.get(business_address = obj)
            if image.image:
                try:
                    tenant = self.context["tenant"]
                    url = tenant_media_domain(tenant, is_s3_url=image.is_image_uploaded_s3)
                    return f'{url}{image.image}'
                except:
                    return image.image
            return None
            #return BusinessAddressMediaSerializer(image, context=self.context).data
        except Exception as err:
            print(err)
            
    def get_currency(self, obj):
        try:
            currency = Currency.objects.get(id=obj.currency.id)
            return CurrencySerializer(currency).data
        
        except Exception as err:
            print(err)
    
    def get_opening_hours(self, obj):
        try:
            location = BusinessOpeningHour.objects.filter(business_address=obj).order_by('-created_at')
            return OpeningHoursSerializer(location, many=True).data
        
        except BusinessOpeningHour.DoesNotExist:
            return None

    def get_start_time(self, obj):
        try:
            location = BusinessOpeningHour.objects.get(
                business_address=obj,
                day__iexact = 'Monday'
            )
            return location.start_time
        except BusinessOpeningHour.DoesNotExist:
            return None
            
    def get_close_time(self, obj):
        try:
            location = BusinessOpeningHour.objects.get(
                business_address=obj,
                day__iexact = 'Monday'
            )
            return location.close_time
        except BusinessOpeningHour.DoesNotExist:
            return None

    class Meta:
        model = BusinessAddress
        fields = [
            'id',
            'country',
            'state',
            'city',
            'currency',
            'email',
            'mobile_number',
            'address',
            'address_name',
            'postal_code',
            'website',
            'is_primary',
            'banking',
            'start_time',
            'close_time',
            'service_avaiable',
            'location_name',
            'images',
            'opening_hours',
            'is_deleted',
            'is_publish',
            'description',
        ]

class BusinessThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessTheme
        fields = [
            'id',
            'primary_color',
            'secondary_color',
            'menu_option',
            'calendar_option',
            'theme_name',
        ]

class StaffNotificationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffNotificationSetting
        fields = [
            # 'id',
            'sms_daily_sale',
            'email_daily_sale'
        ]

class ClientNotificationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientNotificationSetting
        fields = [
            'sms_purchase_plan',
            'sms_for_rewards_on_quick_sale',
            'sms_pending_services_quicksale',
            'sms_for_ewallet_balance_on_quick_sale',
            'sms_pending_payment',
            'email_notify_on_purchase_plan',
            'sms_quick_sale',
            'sms_appoinment',
            'sms_appoinment_reschedule',
            'sms_birthday',
        ]

class AdminNotificationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminNotificationSetting
        fields = [
            'sms_notify_on_appoinment',
            'sms_notify_on_quick_sale',
            'sms_notify_for_daily_book',
            'email_notify_on_appoinment',
            'email_notify_on_quick_sale',
            'email_notify_on_daily_book',
        ]

class StockNotificationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockNotificationSetting
        fields = [
            'notify_for_lowest_stock',
            'notify_stock_turnover',
        ]

class BookingSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingSetting
        fields = [
            'id',
            'cancel_or_reschedule',
            'client_can_book',
            'controls_time_slot',
            'time_slots_interval',
            'allow_client_to_select_team_member',
            'send_to_client',
            'send_to_specific_email_address',
            'auto_confirmation',
            'admin_confirmation',
            'start_time',
            'services',
            'duration',
            'choose_team_member',
            'select_payment_type',
            'initial_deposit',
        ]


class PaymentMethodSerializer(serializers.ModelSerializer):

    method_type_count = serializers.SerializerMethodField(read_only=True)

    def get_method_type_count(self, obj):
        checkout_count = Order.objects.filter(payment_type=obj.method_type).count()
        return checkout_count

    class Meta:
        model = BusinessPaymentMethod
        fields = ['id', 'method_type', 'is_active','method_type_count']
        
class BusinessTaxSerializer(serializers.ModelSerializer):

    parent_tax = ParentBusinessTaxSerializer(many=True, read_only=True)
    location = BusinessAddress_GetSerializer()
    class Meta:
        model = BusinessTax
        fields = ['id', 'name', 'parent_tax',
                  'tax_rate', 'location', 'tax_type', 'is_active']

class BusinessTaxSerializerNew(serializers.ModelSerializer):
    parent_tax = ParentBusinessTaxSerializer(many=True, read_only=True)
    
    class Meta:
        model = BusinessTax
        exclude = ('created_at','user')

class BusinessVendorSerializer(serializers.ModelSerializer):

    country = CountrySerializer(read_only=True)
    state = StateSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    class Meta:
        model = BusinessVendor
        fields = [ 
            'id',
            'country',
            'state',
            'city',
            'address',
            'vendor_name',
            'mobile_number',
            'email',
            'gstin',
            'postal_code',
            'website',
            'is_primary',
            'is_active',
        ]


class BusinessVendorSerializerDropdown(serializers.ModelSerializer):

    class Meta:
        model = BusinessVendor
        fields = ['id', 'vendor_name']

class BusiessAddressAppointmentSerializer(serializers.ModelSerializer):
    currency = serializers.SerializerMethodField()
    
    def get_currency(self, obj):
        try:
            currency = Currency.objects.get(id = obj.currency.id)
            return currency.code
        except Exception as err:
            return str(err)
    class Meta:
        model = BusinessAddress
        fields = ['id', 'address_name', 'currency']


class BusinessAddressNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessAddress
        fields = ['id', 'address_name']


class BusiessAddressTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAddress
        fields = ['id', 'address_name']
class AppointmentServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppointmentService
        fields = '__all__'
class ScheduleSerializer(serializers.ModelSerializer):

         
    class Meta:
        model = EmployeDailySchedule
        fields = '__all__'
        
class EmployeTenatSerializer(serializers.ModelSerializer):
    appointmemt = serializers.SerializerMethodField(read_only=True)
    schedule =  serializers.SerializerMethodField(read_only=True)
    
    def get_schedule(self, obj):
        schedule =  EmployeDailySchedule.objects.filter(employee= obj )
        return ScheduleSerializer(schedule, many = True,context=self.context).data
    
    def get_appointmemt(self, obj):
        service = AppointmentService.objects.filter(member = obj,is_deleted = False).order_by('-created_at')
        for ser in service:
            date = datetime.strptime(self.context["date"], "%Y-%m-%d")
            start_time = self.context["start_time"]
            app_date = ser.appointment_date
            app_time = ser.appointment_time
            duration = ser.duration
            cal_duration = str(duration).split(' ')[0]
            
            ExceptionRecord.objects.create(
                text = f'user {cal_duration} database date {start_time}'
            )
            
            app_date_time = f'2000-01-01 {app_time}'

            app_date_time = datetime.fromisoformat(app_date_time)
            datetime_duration = app_date_time + timedelta(minutes=int(cal_duration))
            datetime_duration = datetime_duration.strftime('%H:%M:%S')
            end_time = datetime_duration
            
            
            if date.date() == app_date:
                if end_time == start_time and end_time :
                    return f'Date are same{end_time}'
            else:
                return 'create emmployee'
             
        return AppointmentServiceSerializer(service, many = True).data
    
    class Meta:
        model = Employee
        fields = '__all__'
        
class EmployeAppointmentServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppointmentService
        fields = ( 'appointment_time', 'end_time')


class BusinessTaxSettingSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessTaxSetting
        fields = '__all__'


class BusinessAddressSerilaizer(serializers.ModelSerializer):

    primary_translation = InvoiceTransSerializer(read_only=True)
    secondary_translation = InvoiceTransSerializer(read_only=True)


    class Meta:
        model = BusinessAddress
        fields = ['primary_translation', 'secondary_translation']


class BusinessPolicySerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessPolicy
        fields = '__all__'

class BusinessPrivacySerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessPrivacy
        fields = '__all__'