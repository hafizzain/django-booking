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

from SaleRecords.serializers import *


class SaleRecordViews(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            serializer = SaleRecordSerializer(data=request.data)
            if serializer.is_valid():
                sale_record = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)