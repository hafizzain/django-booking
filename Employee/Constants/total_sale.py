from Order.models import Checkout, Order
from Appointment.models import AppointmentCheckout, AppointmentService
from django.db.models import F
from django.db.models.functions import Coalesce

def total_sale_employee(employee_id):
    total_price = 0
    employee_id = str(employee_id)
    
    # appointment_checkout = AppointmentService.objects.filter(
    #     appointment_status = 'Done',
    #     member = employee_id,
    #     ).values_list('total_price', flat=True)
    # total_price += sum(appointment_checkout)
    
    orders = Order.objects.filter(
        checkout__is_deleted = False, 
        member__id = employee_id,
    )   
    
    apps_checkouts_total = AppointmentCheckout.objects.filter(
        is_deleted=False, 
        member__id=employee_id,
    )
    
    for order in orders:
        price = 0
        if order.discount_price:
            price = order.discount_price
        elif order.total_price:
            price = order.total_price
        total_price += float(price) * float(order.quantity)
    
    # for price in apps_checkouts_total:
    #     if price.total_price is not None:
    #         total_price += float(price.total_price)
        
    return total_price
