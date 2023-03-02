
from datetime import datetime, timedelta
from django.shortcuts import render


from rest_framework import status
from Appointment.models import Appointment, AppointmentCheckout, AppointmentService
from Business.models import Business
from Client.models import Client, Membership, Vouchers
from Order.models import Checkout, MemberShipOrder, Order, ProductOrder, ServiceOrder, VoucherOrder
from Reports.serializers import BusinesAddressReportSerializer, ComissionReportsEmployeSerializer, ReportBrandSerializer, ReportsEmployeSerializer, ServiceGroupReport, StaffCommissionReport
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

from Product.models import Brand, Product, ProductOrderStockReport, ProductStock
from django.db.models import Avg, Count, Min, Sum


from Sale.serializers import AppointmentCheckout_ReportsSerializer, AppointmentCheckoutSerializer, BusinessAddressSerializer, CheckoutSerializer, MemberShipOrderSerializer, ProductOrderSerializer, ServiceGroupSerializer, ServiceOrderSerializer, ServiceSerializer, VoucherOrderSerializer


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
    
# @api_view(['GET'])
# @permission_classes([AllowAny])
# def get_commission_reports_by_commission_details(request):
#     month = request.GET.get('month', None)
#     range_start = request.GET.get('range_start', None)
#     year = request.GET.get('year', None)
#     range_end = request.GET.get('range_end', None)
#     response_data = []
#     Append_data = [] 
#     newdata = {} 
        
#     employee = Employee.objects.filter(is_deleted=False).order_by('-created_at')
#     serialized = StaffCommissionReport (employee,  many=True, context={
#         'request' : request, 
#         'range_start': range_start, 
#         'range_end': range_end, 
#         'year': year
        
#         })
#     response_data = serialized.data
    
#     for da in response_data:
#         location =  da['location']
#         name = da['full_name']
#         service_sale_price = da['service_sale_price']
#         product_sale_price = da['product_sale_price']
#         voucher_sale_price = da['voucher_sale_price']
        
#         newdata = {
#             'employee': name,
#             'location': location,
#             'sale': service_sale_price,
#             }
#         Append_data.append(newdata)
        
#         newdata = {
#             'employee': name,
#             'location': location,
#             'sale': product_sale_price,
#             }
#         Append_data.append(newdata)
#         newdata = {
#             'employee': name,
#             'location': location,
#             'sale': voucher_sale_price,
#             }
#         Append_data.append(newdata)
    
#     return Response(
#         {
#             'status' : 200,
#             'status_code' : '200',
#             'response' : {
#                 'message' : 'All Employee Orders',
#                 'error_message' : None,
#                 'staff_report' : Append_data
#             }
#         },
#         status=status.HTTP_200_OK
#     )
    
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
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_retail_target_report(request):
    month = request.GET.get('month', None)
    year = request.GET.get('year', None)
    
    brand = Brand.objects.filter(is_active=True).order_by('-created_at')
    serialized = ReportBrandSerializer(brand, many=True, context={'request' : request, 'month': month, 'year': year})
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Brand Sale Report',
                'error_message' : None,
                'sale' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_commission_reports_by_commission_details(request):
    range_start = request.GET.get('range_start', None)
    year = request.GET.get('year', None)
    range_end = request.GET.get('range_end', None)
    
    # #pagination
    
    # paginator = CustomPagination()
    # paginator.page_size = 1
    # result_page = paginator.paginate_queryset(product_order, request)
    # serialized = ProductOrderSerializer(result_page,  many=True)
    
    data=[]
    Append_data = [] 
    newdata = {} 
    if range_start:
        range_start = datetime.strptime(range_start, "%Y-%m-%d")
        range_end = datetime.strptime(range_end, "%Y-%m-%d")
        checkout_order = Checkout.objects.filter(
            is_deleted=False,
            created_at__gte =  range_start ,
            created_at__lte = range_end
            ).order_by('-created_at')
        serialized = CheckoutSerializer(checkout_order,  many=True, context={
            'request' : request, 
            })
        data.extend(serialized.data)
            
        appointment_checkout = AppointmentCheckout.objects.filter(
            appointment_service__appointment_status = 'Done',
            created_at__gte =  range_start ,
            created_at__lte = range_end
            )
        serialized = AppointmentCheckout_ReportsSerializer(appointment_checkout, many = True)
        data.extend(serialized.data)
    else:
        checkout_order = Checkout.objects.filter(is_deleted=False).order_by('-created_at')
        serialized = CheckoutSerializer(checkout_order,  many=True, context={
            'request' : request, 
            })
        data.extend(serialized.data)
            
        appointment_checkout = AppointmentCheckout.objects.filter(appointment_service__appointment_status = 'Done')
        serialized = AppointmentCheckout_ReportsSerializer(appointment_checkout, many = True)
        data.extend(serialized.data)
        
    for da in data:
        try:
            location =  da.get('location', None)
            name = da.get('member', None)
            service_sale_price = da.get('service', None)
            product_sale_price = da.get('product', None)
            voucher_sale_price = da.get('voucher', None)
            service_commission = da.get('service_commission', None)
            voucher_commission = da.get('voucher_commission', None)
            product_commission = da.get('product_commission', None)
            voucher_commission_type = da.get('voucher_commission_type', None)
            product_commission_type = da.get('product_commission_type', None)
            service_commission_type = da.get('service_commission_type', None)
            
            newdata = {
                'employee': name,
                'location': location,
                'commission': service_commission,
                'commission_rate': service_commission_type,
                'sale': service_sale_price,
                }
            Append_data.append(newdata)
            
            newdata = {
                'employee': name,
                'location': location,
                'commission': product_commission,
                'commission_rate': product_commission_type,
                'sale': product_sale_price,
                }
            Append_data.append(newdata)
            newdata = {
                'employee': name,
                'location': location,
                'commission': voucher_commission,
                'commission_rate': voucher_commission_type,
                'sale': voucher_sale_price,
                }
            Append_data.append(newdata)
        except Exception as err:
            pass
        
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Sale Orders',
                'error_message' : None,
                'sales' : Append_data
            }
        },
        status=status.HTTP_200_OK
    )
    
