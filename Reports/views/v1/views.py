
from datetime import datetime, timedelta
from django.shortcuts import render


from rest_framework import status
from Appointment.models import Appointment, AppointmentCheckout, AppointmentService
from Business.models import Business
from Client.models import Client, Membership, Vouchers
from Order.models import Checkout, MemberShipOrder, Order, ProductOrder, ServiceOrder, VoucherOrder
from Reports.serializers import BusinesAddressReportSerializer, ComissionReportsEmployeSerializer, ReportBrandSerializer, ReportsEmployeSerializer, ServiceGroupReport, StaffCommissionReport, EmployeeCommissionReportsSerializer
from Sale.Constants.Custom_pag import CustomPagination
from Utility.Constants.Data.months import MONTHS
from Utility.models import Country, Currency, ExceptionRecord, State, City
from Authentication.models import User
from NStyle.Constants import StatusCodes
import json

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from Employee.models import Employee, EmployeeSelectedService, EmployeeCommission
from Business.models import BusinessAddress
from Service.models import PriceService, Service, ServiceGroup

from Product.models import Brand, Product, ProductOrderStockReport, ProductStock
from django.db.models import Avg, Count, Min, Sum, F, FloatField, Q

from Reports.models import DiscountPromotionSalesReport
from Reports.serializers import DiscountPromotionSalesReport_serializer
from Sale.serializers import AppointmentCheckout_ReportsSerializer, PromotionNDiscount_AppointmentCheckoutSerializer, PromotionNDiscount_CheckoutSerializer, MemberShipOrderSerializer, ProductOrderSerializer, ServiceGroupSerializer, ServiceOrderSerializer, ServiceSerializer, VoucherOrderSerializer, CheckoutCommissionSerializer
from datetime import datetime as dt


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
    
    # employee = Employee.objects.filter(is_deleted=False).order_by('-created_at')
    employee = Employee.objects.prefetch_related(
        'location'
    ).filter(
        is_deleted = False,
        is_active = True,
    ).order_by('-created_at')
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
    location = request.GET.get('location', None)
    
    address = ServiceGroup.objects.filter(
        is_deleted = False,
    ).order_by('-created_at')
    serialized = ServiceGroupReport(address, many=True, context={'request' : request, 
                    'month': month,
                    'location': location,
                    'year': year
                    })

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
    location = request.GET.get('location', None)
    
    brand = Brand.objects.filter(is_active=True).order_by('-created_at')
    serialized = ReportBrandSerializer(brand, many=True, context={'request' : request, 
                                            'month': month,
                                            'year': year,
                                            'location': location,
                                            })
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
def get_commission_reports_by_commission_details_updated(request):
    range_start = request.GET.get('range_start', None) # 2023-02-23
    year = request.GET.get('year', None) # non used
    range_end = request.GET.get('range_end', None) # 2023-02-25
    if range_end is not None:
        range_end = dt.strptime(range_end, '%Y-%m-%d').date()
        range_end = range_end + timedelta(days=1)
        range_end = str(range_end)

    print( range_start, range_end)
    
    data = []
    
    # if range_start:
    #     range_start = datetime.strptime(range_start, "%Y-%m-%d")
    #     range_end = datetime.strptime(range_end, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)

    #     checkout_order = Checkout.objects.filter(
    #         is_deleted=False,
    #         is_promotion = False,
    #         created_at__gte =  range_start ,
    #         created_at__lte = range_end
    #     ).order_by('-created_at')

    #     serialized = CheckoutCommissionSerializer(checkout_order,  many=True, context={
    #         'request' : request, 
    #         })
    #     data.extend(serialized.data)
            
    #     appointment_checkout = AppointmentService.objects.filter(
    #         appointment_status = 'Done', #appointment_service__
    #         created_at__gte =  range_start ,
    #         created_at__lte = range_end
    #         )
    #     serialized = AppointmentCheckout_ReportsSerializer(appointment_checkout, many = True, context={
    #         'request' : request, 
    #         })
    #     data.extend(serialized.data)
    #     sorted_data = sorted(data, key=lambda x: x['created_at'], reverse=True)
    # else:
    #     checkout_order = Checkout.objects.filter(
    #         is_deleted=False,
    #         is_promotion = False,
    #         ).order_by('-created_at')
    #     serialized = CheckoutCommissionSerializer(checkout_order,  many=True, context={
    #         'request' : request, 
    #         })
    #     data.extend(serialized.data)
        
    #     appointment_checkout = AppointmentService.objects.filter(appointment_status = 'Done')
    #     serialized = AppointmentCheckout_ReportsSerializer(appointment_checkout, many = True,context={
    #         'request' : request, 
    #         })
    #     data.extend(serialized.data)
    #     sorted_data = sorted(data, key=lambda x: x['created_at'], reverse=True)

    query = {}
    if range_start and range_end:
        query['created_at__range'] = (range_start, range_end)

    employee_commissions = EmployeeCommission.objects.select_related(
        'employee',
        'location',
    ).filter(
        is_active = True,
        # created_at__gte = range_start,
        # created_at__lte = range_end,
        **query
    ).order_by(
        '-created_at'
    )


    # 'location', 'order_type', 'employee', 'commission', 'commission_rate', 'sale', 'created_at'

    serialized = EmployeeCommissionReportsSerializer(employee_commissions, many=True)
    data = serialized.data

    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Sale Orders',
                'error_message' : None,
                'sales' : data,
                # 'sales' : [
                #     {
                #         'employee' : {},
                #         'location' : {},
                #         'commission' : 00,
                #         'commission_rate' : 00,
                #         'sale' : {},
                #     }
                # ]
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_promotions_and_discounts_sales(request):
    location_id = request.GET.get('location', None)
    start_date =  request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)

    if not all([location_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'location id is required',
                    'fields' : [
                        'location',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )


    paginator = CustomPagination()
    paginator.page_size = 10

    queries = {}

    if start_date and end_date:
        queries['created_at__range'] = (start_date, end_date)

    sales = DiscountPromotionSalesReport.objects.filter(
        is_deleted = False,
        is_active = True,
        location__id = location_id,
        **queries
    ).order_by('-created_at')
    data = DiscountPromotionSalesReport_serializer(sales, many=True).datta
    
    # checkout_order = Checkout.objects.filter(
    #     is_deleted=False,
    #     location__id=location_id,
    #     is_promotion = True,
    #     **queries,
    # )
    # appointment_checkout = AppointmentCheckout.objects.filter(
    #     appointment_service__appointment_status='Done',
    #     business_address__id=location_id,
    #     is_promotion = True,
    #     **queries,
    # )

    # data_total = list(PromotionNDiscount_CheckoutSerializer(checkout_order, many=True, context={'request': request}).data) + \
    #              list(PromotionNDiscount_AppointmentCheckoutSerializer(appointment_checkout, many=True, context={'request': request}).data)
                 
    # sorted_data = sorted(data_total, key=lambda x: x['created_at'], reverse=True)

    paginated_data = paginator.paginate_queryset(data, request)

    return paginator.get_paginated_response(paginated_data, 'sales')