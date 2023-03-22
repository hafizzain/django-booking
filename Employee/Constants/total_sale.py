from Order.models import Checkout
from Appointment.models import AppointmentCheckout

def total_sale_employee(employee_id):
    total_price = 0
    employee_id = str(employee_id)
    checkout_orders_total = Checkout.objects.filter(
        is_deleted=False, 
        member__id=employee_id,
    )   
    
    apps_checkouts_total = AppointmentCheckout.objects.filter(
        is_deleted=False, 
        member__id=employee_id,
    )
    
    for price in checkout_orders_total:
        if price.total_service_price is not None:
            total_price += int(price.total_service_price)
        if price.total_product_price is not None:
            total_price += int(price.total_product_price)
        if price.total_voucher_price is not None:
            total_price += int(price.total_voucher_price)
        if price.total_membership_price is not None:
            total_price += int(price.total_membership_price)
    
    for price in apps_checkouts_total:
        if price.total_price is not None:
            total_price += int(price.total_price)
        
    return total_price


# def total_sale_employee(employee_id):
#     total_price = 0
#     employee_id = str(employee_id)
#     checkout_orders_total = Checkout.objects.filter(
#         is_deleted=False, 
#         member__id=employee_id,
#     )   
    
#     apps_checkouts_total = AppointmentCheckout.objects.filter(
#         is_deleted=False, 
#         member__id=employee_id,
#     )
    
#     for price in checkout_orders_total:
#         total_price += int(price.total_service_price)
#         total_price += int(price.total_product_price)
#         total_price += int(price.total_voucher_price)
#         total_price += int(price.total_membership_price)
    
#     for price in apps_checkouts_total:
#         total_price += int(price.total_price)
        
#     return total_price