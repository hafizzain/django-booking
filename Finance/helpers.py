from Tenants.models import Tenant
from django.db.models import Q,F
from Finance.models import AllowRefundPermissionsEmployees, AllowRefunds
from Invoices.models import SaleInvoice
from django.utils import timezone


# Short the UUID field Method
def short_uuid(uuid):
    uuid = str(uuid).replace('-','')[:6]
    return uuid



def check_days(invoice_id, location):
    # try:
        no_of_days = AllowRefunds.objects.get(location_id= location).number_of_days
        instance = SaleInvoice.objects.get(id=invoice_id, location=location)
        days_difference = (timezone.now() - instance.created_at).days
        return days_difference <= no_of_days
    # except SaleInvoice.DoesNotExist:
    #     return False

def check_permission(user_id, location):
    if Tenant.objects.filter(user_id = user_id).exists():
        return True
    elif AllowRefundPermissionsEmployees.objects.filter(
        Q(employee_id=user_id) &
        (
            Q(allowed_refund__number_of_days__gte=F('allowed_refund__number_of_days')) |
            Q(can_refund=True)
        ) &
        Q(allowed_refund__location=location)
        ).exists():
        return True
    else:
        return False