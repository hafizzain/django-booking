
from django.contrib import admin

from .models import DateRestrictions, DiscountOnFreeService, DayRestrictions, PackagesDiscount, ProductAndGetSpecific, RetailAndGetService, BundleFixed, MentionedNumberService, SpecificBrand, FixedPriceService, FreeService,SpecificGroupDiscount, ServiceGroupDiscount, PurchaseDiscount, DirectOrFlatDiscount,SpendDiscount,CategoryDiscount, BlockDate, SpendSomeAmountAndGetDiscount, SpendSomeAmount, ServiceDurationForSpecificTime , PromotionExcludedItem, ComplimentaryDiscount, UserRestrictedDiscount


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
admin.site.register(SpendSomeAmount)
admin.site.register(ServiceDurationForSpecificTime)
admin.site.register(ComplimentaryDiscount)
admin.site.register(UserRestrictedDiscount)
admin.site.register(SpecificBrand)
admin.site.register(MentionedNumberService)
admin.site.register(BundleFixed)
admin.site.register(RetailAndGetService)
admin.site.register(ProductAndGetSpecific)
admin.site.register(PackagesDiscount)
admin.site.register(DiscountOnFreeService)

@admin.register(PromotionExcludedItem)
class PromotionExcludedItemAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'object_type',
        'object_id',
        'excluded_type',
        'excluded_id',
        'is_deleted',
        'is_active',
    ]