
from datetime import timedelta
from django.shortcuts import render

from rest_framework import status
from Appointment.models import Appointment, AppointmentCheckout, AppointmentService
from Business.models import Business
from Client.models import Client, Membership, Vouchers
from Order.models import Checkout, MemberShipOrder, Order, ProductOrder, ServiceOrder, VoucherOrder
from Reports.serializers import BusinesAddressReportSerializer, ComissionReportsEmployeSerializer, ReportsEmployeSerializer, ServiceGroupReport, StaffCommissionReport
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
    month = request.GET.get('month', None)
    year = request.GET.get('year', None)
    
    employee = Employee.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = ReportsEmployeSerializer(employee,  many=True, context={'request' : request, 'month': month, 'year': year})
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Employee Orders',
                'error_message' : None,
                'staff_report' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_commission_reports_by_staff(request):
    
    range_start = request.GET.get('range_start', None)
    year = request.GET.get('year', None)
    range_end = request.GET.get('range_end', None)
    
    employee = Employee.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = ComissionReportsEmployeSerializer(employee,  many=True, context={
                        'request' : request, 
                        'range_start': range_start, 
                        'range_end': range_end, 
                        'year': year
            })
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Employee Orders',
                'error_message' : None,
                'staff_report' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_store_target_report(request):
    month = request.GET.get('month', None)
    year = request.GET.get('year', None)
    
    address = BusinessAddress.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = BusinesAddressReportSerializer(address, many=True, context={'request' : request, 'month': month, 'year': year})
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Business Address Report',
                'error_message' : None,
                'address' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_commission_reports_by_commission_details(request):
    month = request.GET.get('month', None)
    range_start = request.GET.get('range_start', None)
    year = request.GET.get('year', None)
    range_end = request.GET.get('range_end', None)
    
    employee = Employee.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = StaffCommissionReport (employee,  many=True, context={
        'request' : request, 
        'range_start': range_start, 
        'range_end': range_end, 
        'year': year
        
        })
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Employee Orders',
                'error_message' : None,
                'staff_report' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_service_target_report(request):
    month = request.GET.get('month', None)
    year = request.GET.get('year', None)
    
    address = ServiceGroup.objects.filter(is_deleted=False).order_by('-created_at')
    serialized = ServiceGroupReport(address, many=True, context={'request' : request, 'month': month, 'year': year})
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Business Address Report',
                'error_message' : None,
                'address' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )