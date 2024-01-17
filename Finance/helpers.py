from Authentication.models import User
from django.db.models import Q,F
from Finance.models import AllowRefundPermissionsEmployees, AllowRefunds
from Invoices.models import SaleInvoice
from django.utils import timezone


# Short the UUID field Method
def short_uuid(uuid):
    uuid = str(uuid).replace('-','')[:6]
    return uuid

def check_days(invoice_id, location):
    try:
        # print(f"Checking for location: {location}")
        no_of_days = AllowRefunds.objects.get(location=location).number_of_days
        instance = SaleInvoice.objects.get(id=invoice_id)
        days_difference = (timezone.now() - instance.created_at).days
        return days_difference <= no_of_days
    except Exception as e:
        return f"An error occurred: {str(e)}"

def check_permission(user_id, location, invoice_id):
    if User.objects.get(id = user_id, is_admin = True) and SaleInvoice.objects.get(id=invoice_id):
        return True
    elif AllowRefundPermissionsEmployees.objects.filter(
        Q(employee_id=user_id) &
        Q(allowed_refund__location_id=location)
        ).exists():
        return True
    else:
        return False 