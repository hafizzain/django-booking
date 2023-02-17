from django.contrib import admin

from .models import User, AccountType, NewsLetterDetail, VerificationOTP


from Tenants.models import Tenant, Domain

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
        'is_email_verified',
        'is_tenant_user'
    ]

    list_filter = ['is_email_verified', 'is_mobile_verified']
    
    def is_tenant_user(self, user_obj):
        try:
            Domain.objects.get(
                user = user_obj
            )
        except:
            return False
        else:
            return True

    is_tenant_user.boolean = True


@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'account_type',
        'username',
    ]


@admin.register(NewsLetterDetail)
class NewsLetterDetailAdmin(admin.ModelAdmin):

    def username(self, obj):
        try:
            return str(obj.user.username)
        except Exception as err:
            return str(err)

    list_display = [
        'id',
        'username',
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