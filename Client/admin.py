from django.contrib import admin
from .models import Client, ClientGroup, Subscription , Membership , Vouchers , Promotion , Rewards , DiscountMembership, ClientPackageValidation, CurrencyPriceMembership, LoyaltyPoints, ClientLoyaltyPoint, LoyaltyPointLogs, VoucherCurrencyPrice
# Register your models here.
admin.site.register(DiscountMembership)
admin.site.register(ClientPackageValidation)
admin.site.register(CurrencyPriceMembership)

@admin.register(VoucherCurrencyPrice)
class VoucherCurrencyPriceAdmin(admin.ModelAdmin):
    list_display=[
        'id',
        'voucher',
        'currency',
        'price',
        'is_deleted',
    ]

@admin.register(LoyaltyPointLogs)
class LoyaltyPointLogsAdmin(admin.ModelAdmin):
    list_display= [
        'id',
        'points_earned',
        'points_redeemed',
        'balance',
        'actual_sale_value_redeemed',
    ]
@admin.register(LoyaltyPoints)
class LoyaltyPointsAdmin(admin.ModelAdmin):
    list_display= [
        'id',
        'amount_spend',
        'number_points',
        'earn_points',
        'total_earn_from_points',
    ]


@admin.register(ClientLoyaltyPoint)
class ClientLoyaltyPointAdmin(admin.ModelAdmin):
    list_display= [
        'id',
        'client_name',
        'total_amount',
        'total_earn',
        'for_every_points',
        'customer_will_get_amount',
        'total_available_points',
        'created_at',
    ]

    def client_name(self, obj):
        if obj.client:
            return obj.client.full_name
        return '-------'
    
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display= [
        'id',
        'full_name', 
        'mobile_number',
        'email',
    ]
    
@admin.register(ClientGroup)
class ClientGroupAdmin(admin.ModelAdmin):
    list_display= [
                'id', 
                'user',
                'name', 
                'email',
                   ]
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display= [
        'id', 
        'user', 
        'name', 
        'days',
        ]    
@admin.register(Rewards)
class RewardsAdmin(admin.ModelAdmin):
    list_display= [
        'id', 
        'user', 
        'name', 
        'total_points',
        ]  
@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display= [
        'id', 
        'user', 
        ] 
@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display= [
        'id', 
        'user', 
        'name', 
        ] 
@admin.register(Vouchers)
class VouchersAdmin(admin.ModelAdmin):
    list_display= [
        'id', 
        'user', 
        'name', 
        'validity',
        'price',
        'is_active'
    ]