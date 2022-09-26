from django.contrib import admin
from Sale.models import Service

# Register your models here.

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'name', 
        'is_package', 
        'description',
    ] 
