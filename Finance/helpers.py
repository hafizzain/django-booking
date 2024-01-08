
from django.db.models import Q
from Finance.models import AllowRefundPermissionsEmployees
from Invoices.models import SaleInvoice
from django.utils import timezone


# Short the UUID field Method
def short_uuid(uuid):
    uuid = str(uuid).replace('-','')[:6]
    return uuid



def check_days(invoice_id, location):
    try:
        instance = SaleInvoice.objects.get(id=invoice_id, location=location)
        days_difference = (timezone.now() - instance.created_at).days
        return days_difference <= 30
    except SaleInvoice.DoesNotExist:
        return False

def check_permission(user_id, location):
    return AllowRefundPermissionsEmployees.objects.filter(
        Q(employee_id=user_id) &
        (
            Q(allowed_refund__number_of_days__gte=30) |
            Q(can_refund=True)
        ) &
        Q(allowed_refund__location=location)
    ).exists()