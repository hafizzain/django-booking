
from django.contrib import admin

from .models import DateRestrictions, DayRestrictions, FixedPriceService, FreeService,SpecificGroupDiscount, ServiceGroupDiscount, PurchaseDiscount, DirectOrFlatDiscount,SpendDiscount,CategoryDiscount, BlockDate, SpendSomeAmountAndGetDiscount


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
admin.site.register(SpendSomeAmountAndGetDiscount)
admin.site.register(FixedPriceService)
admin.site.register(FreeService)