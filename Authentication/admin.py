from django.contrib import admin

from .models import User, AccountType, NewsLetterDetail, VerificationOTP


from Business.models import Business
from django_tenants.utils import tenant_context
from Tenants.models import Tenant, Domain

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ['email', 'username']
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

    actions = ['unlink_tenant_and_delete_user']
    
    def is_tenant_user(self, user_obj):
        try:
            Domain.objects.get(
                user = user_obj
            )
        except:
            return False
        else:
            return True

    @admin.action(description='Unlink Tenant & Delete User')
    def unlink_tenant_and_delete_user(modeladmin, request, queryset):
        for user in queryset:
            
            user_tenants = Tenant.objects.filter(user = user)
            ids = list(user_tenants.values_list('id', flat=True))
            user_tenants.update(
                name = '',
                user = None,
                is_active = False,
                is_ready = True,
            )
            Domain.objects.filter(
                tenant__id__in = ids
            ).delete()

            user.delete()
            for tenant in user_tenants:
                with tenant_context(tenant):
                    users = User.objects.all()
                    users.delete()
                    businesses = Business.objects.all()
                    businesses.delete()

    is_tenant_user.boolean = True


@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    search_fields = ['user__email']
    list_filter = ['account_type']
    list_display = [
        'id',
        'account_type',
        'username',
        'email',
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