
from Promotions import models as ProModel

PROMOTION_TYPES_MODELS = {
    'Direct Or Flat' : ProModel.DirectOrFlatDiscount,
    'Specific Group Discount' : ProModel.DirectOrFlatDiscount,
    'Purchase Discount' : ProModel.DirectOrFlatDiscount,
    'Specific Brand Discount' : ProModel.DirectOrFlatDiscount,
    'Spend_Some_Amount' : ProModel.DirectOrFlatDiscount,
    'Fixed_Price_Service' : ProModel.DirectOrFlatDiscount,
    'Mentioned_Number_Service' : ProModel.DirectOrFlatDiscount,
    'Bundle_Fixed_Service' : ProModel.DirectOrFlatDiscount,
    'Retail_and_Get_Service' : ProModel.DirectOrFlatDiscount,
    'User_Restricted_discount' : ProModel.DirectOrFlatDiscount,
    'Complimentary_Discount' : ProModel.DirectOrFlatDiscount,
    'Packages_Discount' : ProModel.DirectOrFlatDiscount,
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
        return instance