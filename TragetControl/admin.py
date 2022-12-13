from django.contrib import admin
from .models import StaffTarget, StoreTarget, TierStoreTarget
# Register your models here.
admin.site.register(StaffTarget)
admin.site.register(StoreTarget)
admin.site.register(TierStoreTarget)
