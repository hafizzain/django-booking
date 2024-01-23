from SaleRecords.models import SaleRecords

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q
from Utility.Campaign import send_refund_email

from Finance.models import Refund, RefundCoupon, AllowRefunds,AllowRefundPermissionsEmployees, RefundProduct, RefundServices
from Finance.serializers import RefundSerializer, CouponSerializer, AllowRefundsSerializer
from Finance.helpers import short_uuid, check_permission, check_days
from Invoices.models import SaleInvoice
from Client.serializers import SaleInvoiceSerializer
from Client.models import Client


from Appointment.models import AppointmentCheckout, AppointmentService
from Order.models import Checkout, ProductOrder, ServiceOrder


class SaleRecordViews(APIView):
    
    def post(self, request, *args, **kwargs):
        pass