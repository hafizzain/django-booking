
from django.contrib import admin

from .models import DateRestrictions, DayRestrictions,SpecificGroupDiscount, ServiceGroupDiscount, PurchaseDiscount, DirectOrFlatDiscount,SpendDiscount,CategoryDiscount, BlockDate


# Register your models here.



admin.site.register(DateRestrictions)
admin.site.register(DayRestrictions)
admin.site.register(SpecificGroupDiscount)
admin.site.register(ServiceGroupDiscount)
admin.site.register(PurchaseDiscount)
admin.site.register(DirectOrFlatDiscount)
admin.site.register(SpendDiscount)
admin.site.register(CategoryDiscount)
admin.site.register(BlockDate)