from django.contrib import admin

from .models import User, AccountType, TenantDetail, NewsLetterDetail, VerificationOTP



@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'email', 
        'username', 
        'first_name', 
        'last_name', 
        'is_active', 
        'is_admin', 
        'is_staff', 
        'is_superuser', 
        'is_mobile_verified', 
        'is_email_verified'
    ]

@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'account_type',
        'username',
    ]


@admin.register(NewsLetterDetail)
class NewsLetterDetailAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'is_subscribed'
    ]

@admin.register(TenantDetail)
class TenantDetailAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'is_tenant_admin',
        'is_tenant_staff',
        'is_tenant_superuser',
    ]

@admin.register(VerificationOTP)
class VerificationOTPAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'username',
        'code',
        'code_for',
    ]