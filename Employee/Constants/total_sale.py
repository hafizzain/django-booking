from Order.models import Checkout, Order
from Appointment.models import AppointmentCheckout, AppointmentService
from django.db.models import F, Sum, FloatField
from django.db.models.functions import Coalesce

def total_sale_employee(employee_id):
    total_price = 0
    employee_id = str(employee_id)
    

    # Appointments Sale-------------------------------------
    appointment_checkout = AppointmentService.objects.filter(
        appointment_status = 'Done',
        member = employee_id,
        ).aggregate(appointment_sum=Sum('total_price'))['appointment_sum']
    
    if appointment_checkout:
        total_price += float(appointment_checkout)


    # Discounted Orders Sale------------------
    discounted_orders = Order.objects.filter(
        checkout__is_deleted = False, 
        member__id = employee_id,
        discount_price__isnull=False,
    ).annotate(
        total = F('discount_price') * F('quantity')
    ).aggregate(total_sum=Sum('total'))['total_sum']

    if discounted_orders:
        total_price += float(discounted_orders)



    # Non Discounted Sale-----------------------
    non_discounted_orders = Order.objects.filter(
        checkout__is_deleted = False, 
        member__id = employee_id,
        discount_price__isnull=True
    ).annotate(
        total = F('total_price') * F('quantity')
    ).aggregate(total_sum=Sum('total'))['total_sum']

    if non_discounted_orders:
        total_price += float(non_discounted_orders)


    return total_price

