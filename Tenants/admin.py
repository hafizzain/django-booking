from django.contrib import admin

# Register your models here.


from .models import Tenant, Domain

admin.site.register(Tenant)
admin.site.register(Domain)