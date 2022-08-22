from django.contrib import admin

from .models import User, AccountType, NewsLetterDetail, VerificationOTP



@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'email', 
        'username', 
        'first_name', 
        'last_name', 
        'mobile_number', 
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
        'terms_condition',
        'is_subscribed'
    ]


@admin.register(VerificationOTP)
class VerificationOTPAdmin(admin.ModelAdmin):

    def mobile_number(self, obj):
        try:
            return obj.user.mobile_number
        except:
            return 'N/A'
    list_display = [
        'id',
        'username',
        'mobile_number',
        'code',
        'code_for',
        'created_at',
    ]