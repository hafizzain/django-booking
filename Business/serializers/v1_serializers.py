


from cmath import e
from dataclasses import field
from locale import currency
from pyexpat import model
from Utility.models import Currency, State, Country,City
from rest_framework import serializers

from Business.models import BookingSetting, BusinessAddressMedia, BusinessType, Business, BusinessAddress, BusinessSocial, BusinessTheme, StaffNotificationSetting, ClientNotificationSetting, AdminNotificationSetting, StockNotificationSetting, BusinessPaymentMethod, BusinessTax, BusinessVendor,BusinessOpeningHour
from Authentication.serializers import UserSerializer
from django.conf import settings

from Product.Constants.index  import tenant_media_base_url

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
    currency =CurrencySerializer()

    logo = serializers.SerializerMethodField()
    
    
    def get_logo(self, obj):
        if obj.logo :
            try:
                request = self.context["request"]
                url = tenant_media_base_url(request)
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
    
    class Meta:
        model= BusinessAddressMedia
        fields= '__all__'
        
class OpeningHoursSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= BusinessOpeningHour
        fields= '__all__'
class CurrencySerializer(serializers.ModelSerializer):
    
    class Meta:
        model= Currency
        fields= '__all__'

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
            return BusinessAddressMediaSerializer(image).data
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
            location = BusinessOpeningHour.objects.filter(business_address=obj)
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
            'is_deleted'
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

    class Meta:
        model = BusinessPaymentMethod
        fields = ['id', 'method_type', 'is_active']
        
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

class BusinessTaxSerializer(serializers.ModelSerializer):

    parent_tax = ParentBusinessTaxSerializer(many=True, read_only=True)
    location = BusinessAddress_GetSerializer()
    class Meta:
        model = BusinessTax
        fields = ['id', 'name', 'parent_tax',
                  'tax_rate', 'location', 'tax_type', 'is_active']


class BusinessVendorSerializer(serializers.ModelSerializer):
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

class BusiessAddressAppointmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessAddress
        fields = ['id', 'address_name']