from django.contrib import admin

from .models import Deal, DealCategory
# Register your models here.


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = [
        'id'
    ]


@admin.register(DealCategory)
class DealCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'id'
    ]