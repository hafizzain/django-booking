
from datetime import timedelta
from django.shortcuts import render

from rest_framework import status
from Appointment.models import Appointment, AppointmentCheckout, AppointmentService
from Business.models import Business
from Client.models import Client, Membership, Vouchers
from Order.models import Checkout, MemberShipOrder, Order, ProductOrder, ServiceOrder, VoucherOrder
from Sale.Constants.Custom_pag import CustomPagination
from Utility.Constants.Data.months import MONTHS
from Utility.models import Country, Currency, ExceptionRecord, State, City
from Authentication.models import User
from NStyle.Constants import StatusCodes
import json

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from Employee.models import Employee, EmployeeSelectedService
from Business.models import BusinessAddress
from Service.models import PriceService, Service, ServiceGroup

from Product.models import Product, ProductOrderStockReport, ProductStock
from django.db.models import Avg, Count, Min, Sum


from Sale.serializers import AppointmentCheckoutSerializer, BusinessAddressSerializer, CheckoutSerializer, MemberShipOrderSerializer, ProductOrderSerializer, ServiceGroupSerializer, ServiceOrderSerializer, ServiceSerializer, VoucherOrderSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def get_reports_staff_target(request):
    data = []
    employee = Employee.objects.filter(is_deleted=False).order_by('-created_at')
    for emp in employee:
        service_orders = ServiceOrder.objects.filter(is_deleted=False, member = emp.id ).annotate(total=Sum('total_price'))
        
        data.append({
                        'employee_name' : emp.full_name,
                        'sales' : service_orders,
                    })
        
        
    #serialized = ServiceOrderSerializer(service_orders,  many=True, context={'request' : request, })
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Service Orders',
                'error_message' : None,
                'orders' : data
            }
        },
        status=status.HTTP_200_OK
    )