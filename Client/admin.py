from django.contrib import admin
from .models import Client, ClientGroup, Subscription , Membership , Vouchers , Promotion , Rewards

# Register your models here.
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
        'duration',
        ] 
@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display= [
        'id', 
        'user', 
        'name', 
        'days',
        ] 
@admin.register(Vouchers)
class VouchersAdmin(admin.ModelAdmin):
    list_display= [
        'id', 
        'user', 
        'name', 
        'days',
        ] 