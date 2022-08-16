


from rest_framework import serializers

from Business.models import BookingSetting, BusinessType, Business, BusinessAddress, BusinessSocial, BusinessTheme, StaffNotificationSetting, ClientNotificationSetting, AdminNotificationSetting, StockNotificationSetting, BusinessPaymentMethod
from Authentication.serializers import UserSerializer

class BusinessTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessType
        fields = ['id', 'name', 'image']


class Business_GetSerializer(serializers.ModelSerializer):
    website = serializers.SerializerMethodField()
    facebook = serializers.SerializerMethodField()
    instagram = serializers.SerializerMethodField()

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
            'currency',
            'timezone',
            'time_format',
            'how_find_us',
            'website',
            'facebook',
            'instagram',
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

class BusinessAddress_GetSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAddress
        fields = [
            'id',
            'country',
            'state',
            'city',
            'address',
            'address_name',
            'postal_code',
            'website',
            'is_primary',
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