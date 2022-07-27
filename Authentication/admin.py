from django.contrib import admin

from .models import User, AccountType



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