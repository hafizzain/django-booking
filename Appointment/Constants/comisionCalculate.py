from Employee.models import CategoryCommission, CommissionSchemeSetting
from Utility.models import ExceptionRecord


def calculate_commission(member, price):
    # if price <= 0:
    #     return 0, ''
    
    # commission = CommissionSchemeSetting.objects.get(employee=str(member))
    # category = CategoryCommission.objects.filter(commission=commission.id).order_by('from_value')
    # commission_percentage = None
    # for cat in category:
    #     if cat.category_comission == 'Service':
    #         if cat.to_value is not None and price >= int(cat.from_value) and price <= int(cat.to_value):
    #             commission_percentage = int(cat.commission_percentage)
    #             break
    #         elif cat.to_value is None and price >= int(cat.from_value):
    #             commission_percentage = int(cat.commission_percentage)
    #             break
            
    # if commission_percentage is None:
    #     return 0, ''
    # elif cat.symbol == '%':
    #     service_commission = price * (commission_percentage / 100)
    #     service_commission_type = str(commission_percentage) + cat.symbol
    # else:
    #     service_commission = commission_percentage
    #     service_commission_type = str(commission_percentage) + cat.symbol
    # return service_commission, service_commission_type
    
    try:
        commission = CommissionSchemeSetting.objects.get(employee = str(member))
        category = CategoryCommission.objects.filter(commission = commission.id)
        for cat in category:
            try:
                toValue = int(cat.to_value)
            except :
                sign  = cat.to_value
            if cat.category_comission == 'Service':
                if (int(cat.from_value) <= price and  price <  toValue) or (int(cat.from_value) <= price and sign ):
                    if cat.symbol == '%':
                        service_commission = price * int(cat.commission_percentage) / 100
                        service_commission_type = str(service_commission_type) + cat.symbol
                    else:
                        service_commission = int(cat.commission_percentage)
                        service_commission_type = str(service_commission) + cat.symbol
                                        
    except Exception as err:
        ExceptionRecord.objects.create(
            text = f'calculate_commission error {str(err)}'
        )