from Order.models import Checkout, Order
from Appointment.models import AppointmentCheckout, AppointmentService
from django.db.models import F, Sum
from django.db.models.functions import Coalesce

def total_sale_employee(employee_id):
    total_price = 0
    employee_id = str(employee_id)
    

    # Appointments Sale----------------------------
    appointment_checkout = AppointmentService.objects.filter(
        appointment_status = 'Done',
        member = employee_id,
        ).aggregate(appointment_sum=Coalesce(Sum('total_price'), 0))['appointment_sum']
    
    total_price += appointment_checkout


    # Orders Sale------------------
    orders = Order.objects.filter(
        checkout__is_deleted = False, 
        member__id = employee_id,
    )
    for order in orders:
        price = 0
        if order.discount_price:
            price = order.discount_price
        elif order.total_price:
            price = order.total_price
        total_price += float(price) * float(order.quantity)

        
    return total_price
