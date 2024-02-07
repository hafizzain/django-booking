from django.contrib import admin

from .models import Deal, DealCategory, RedeemableChannel, DealRestriction
# Register your models here.


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'category',
    ]


@admin.register(DealCategory)
class DealCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'id'
    ]
@admin.register(RedeemableChannel)
class RedeemableChannelAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name'
    ]

@admin.register(DealRestriction)
class DealRestrictionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'deal'
    ]