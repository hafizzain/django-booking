from Employee.models import CategoryCommission, CommissionSchemeSetting


def calculate_commission(member, price):
    commission = CommissionSchemeSetting.objects.get(employee=str(member))
    category = CategoryCommission.objects.filter(commission=commission.id).order_by('from_value')
    commission_percentage = None
    for cat in category:
        if cat.category_comission == 'Service':
            if cat.to_value is not None and price >= int(cat.from_value) and price < int(cat.to_value):
                commission_percentage = int(cat.commission_percentage)
                break
            elif cat.to_value is None and price >= int(cat.from_value):
                commission_percentage = int(cat.commission_percentage)
                break
    if commission_percentage is None:
        return 0, ''
    elif cat.symbol == '%':
        service_commission = price * commission_percentage / 100
        service_commission_type = str(commission_percentage) + cat.symbol
    else:
        service_commission = commission_percentage
        service_commission_type = str(commission_percentage) + cat.symbol
    return service_commission, service_commission_type