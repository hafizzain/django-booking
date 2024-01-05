
from django.db.models import Q
from Finance.models import AllowRefundPermissionsEmployees
# Short the UUID field Method
def short_uuid(uuid):
    uuid = str(uuid).replace('-','')[:6]
    return uuid

def check_permission(id):
    AllowRefundPermissionsEmployees.objects.filter(Q(employee_id=id) & Q(allowed_refund__number_of_days__lt=30)).exists() or \
        AllowRefundPermissionsEmployees.objects.filter(Q(employee_id=id) & Q(allowed_refund__number_of_days__gt=30)).exists()
