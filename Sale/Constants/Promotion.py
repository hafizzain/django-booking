
from Promotions import models as ProModel

PROMOTION_TYPES_MODELS = {
    'Direct Or Flat' : ProModel.DirectOrFlatDiscount,
    'Specific Group Discount' : ProModel.SpecificGroupDiscount,
    'Purchase Discount' : ProModel.PurchaseDiscount,
    'Specific Brand Discount' : ProModel.SpecificBrand,
    'Spend_Some_Amount' : ProModel.SpendSomeAmount,
    'Fixed_Price_Service' : ProModel.FixedPriceService,
    'Mentioned_Number_Service' : ProModel.MentionedNumberService,
    'Bundle_Fixed_Service' : ProModel.BundleFixed,
    'Retail_and_Get_Service' : ProModel.RetailAndGetService,
    'User_Restricted_discount' : ProModel.UserRestrictedDiscount,
    'Complimentary_Discount' : ProModel.ComplimentaryDiscount,
    'Packages_Discount' : ProModel.PackagesDiscount,
}



def get_promotions(promotion_type=None, promotion_id=None):

    TypeModel = PROMOTION_TYPES_MODELS.get(promotion_type, None)
    if not TypeModel:
        return None

    try:
        instance = TypeModel.objects.get(id = promotion_id)
    except:
        return None
    else:
        return {
            'promotion_name' : instance.promotion_name,
        }