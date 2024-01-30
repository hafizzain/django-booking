import json
from datetime import timedelta
from datetime import datetime as dt

from django.db.models import CharField, Q
from django.db.models.functions import Cast

from rest_framework import status
from Reports.serializers import (BusinesAddressReportSerializer, ComissionReportsEmployeSerializer,
                                 ReportBrandSerializer, ReportsEmployeSerializer, ServiceGroupReport,
                                 EmployeeCommissionReportsSerializer)
from Sale.Constants.Custom_pag import CustomPagination, AppointmentsPagination
from TragetControl.models import StaffTarget, RetailTarget
from TragetControl.serializers import RetailTargetSerializers
from Utility.Constants.Data.months import MONTHS
from NStyle.Constants import StatusCodes

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from Employee.models import Employee, EmployeeCommission
from Business.models import BusinessAddress
from Service.models import ServiceGroup
from Product.models import Brand
from Business.serializers.v1_serializers import BusinessAddressSerilaizer

from Reports.models import DiscountPromotionSalesReport
from Reports.serializers import DiscountPromotionSalesReport_serializer, DiscountPromotionSalesReport_serializerOP


@api_view(['GET'])
@permission_classes([AllowAny])
def get_reports_staff_target(request):
    location_id = request.GET.get('location_id', None)
    employee_id = request.GET.get('employee_id', None)
    no_pagination = request.GET.get('no_pagination', None)
    month = request.GET.get('month', None)
    year = request.GET.get('year', None)

    query = Q(is_deleted=False)
    query &= Q(location__id=location_id)

    if employee_id:
        query &= Q(id=str(employee_id))

    employee = Employee.objects.filter(query).order_by('-created_at')
    serialized = list(
        ReportsEmployeSerializer(employee, many=True, context={'request': request, 'month': month, 'year': year}).data)

    paginator = CustomPagination()
    paginator.page_size = 100000 if no_pagination else 10
    paginated_data = paginator.paginate_queryset(serialized, request)
    response = paginator.get_paginated_response(paginated_data, 'staff_report')
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def get_commission_reports_by_staff(request):
    location_id = request.GET.get('location_id', None)
    range_start = request.GET.get('range_start', None)
    year = request.GET.get('year', None)
    range_end = request.GET.get('range_end', None)

    employee = Employee.objects.prefetch_related(
        'location'
    ).filter(
        is_deleted=False,
        is_active=True,
        location__id=location_id
    ).order_by('-created_at')
    serialized = ComissionReportsEmployeSerializer(employee, many=True, context={
        'request': request,
        'range_start': range_start,
        'range_end': range_end,
        'year': year
    })
    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'All Employee Orders',
                'error_message': None,
                'staff_report': serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_store_target_report(request):
    month = request.GET.get('month', None)
    year = request.GET.get('year', None)
    no_pagination = request.GET.get('no_pagination', None)
    location_id = request.GET.get('location_id', None)

    address = BusinessAddress.objects.filter(is_deleted=False).order_by('-created_at')

    if location_id:
        address = address.filter(id=str(location_id))

    serialized = list(BusinesAddressReportSerializer(address,
                                                     many=True,
                                                     context={'request': request,
                                                              'month': month,
                                                              'year': year}).data)

    paginator = CustomPagination()
    paginator.page_size = 100000 if no_pagination else 10
    paginated_data = paginator.paginate_queryset(serialized, request)
    response = paginator.get_paginated_response(paginated_data, 'address')
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def get_service_target_report(request):
    no_pagination = request.GET.get('no_pagination', None)
    month = request.GET.get('month', None)
    year = request.GET.get('year', None)
    location_id = request.GET.get('location_id', None)
    service_group_id = request.GET.get('service_group_id', None)

    service_groups = ServiceGroup.objects.filter(
        is_deleted=False,
    ).order_by('-created_at')

    if service_group_id:
        service_groups = service_groups.filter(id=str(service_group_id))

    serialized = list(ServiceGroupReport(service_groups, many=True, context={'request': request,
                                                                             'month': month,
                                                                             'location': location_id,
                                                                             'year': year
                                                                             }).data)

    paginator = CustomPagination()
    paginator.page_size = 100000 if no_pagination else 10
    paginated_data = paginator.paginate_queryset(serialized, request)
    response = paginator.get_paginated_response(paginated_data, 'servicegroups')
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def get_retail_target_report(request):
    no_pagination = request.GET.get('no_pagination', None)
    month = request.GET.get('month', None)
    year = request.GET.get('year', None)
    location_id = request.GET.get('location_id', None)
    brand_id = request.GET.get('brand_id', None)

    brands = Brand.objects.filter(is_active=True).order_by('-created_at')

    if brand_id:
        brands = brands.filter(id=str(brand_id))

    serialized = list(ReportBrandSerializer(brands, many=True, context={'request': request,
                                                                        'month': month,
                                                                        'year': year,
                                                                        'location': location_id,
                                                                        }).data)
    paginator = CustomPagination()
    paginator.page_size = 100000 if no_pagination else 10
    paginated_data = paginator.paginate_queryset(serialized, request)
    response = paginator.get_paginated_response(paginated_data, 'sale')
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def get_commission_reports_by_commission_details_updated(request):
    no_pagination = request.GET.get('no_pagination', None)
    range_start = request.GET.get('range_start', None)  # 2023-02-23
    range_end = request.GET.get('range_end', None)  # 2023-02-25
    location_id = request.GET.get('location_id', None)
    order_type = request.GET.get('order_type', None)
    employee_id = request.GET.get('employee_id', None)

    if range_end is not None:
        range_end = dt.strptime(range_end, '%Y-%m-%d').date()
        range_end = range_end + timedelta(days=1)
        range_end = str(range_end)

    query = {}

    if location_id:
        query['location_id'] = location_id

    if order_type:
        query['commission_category'] = order_type

    if employee_id:
        employee = Employee.objects.get(id=str(employee_id))
        query['employee'] = employee

    if range_start and range_end:
        query['created_at__range'] = (range_start, range_end)

    employee_commissions = EmployeeCommission.objects.select_related(
        'employee',
        'location',
    ).filter(
        is_active=True,
        **query
    ).order_by(
        '-created_at'
    )

    # invoice translation data
    business_address = BusinessAddress.objects.get(id=location_id)
    invoice_translations = BusinessAddressSerilaizer(business_address).data

    serialized = list(
        EmployeeCommissionReportsSerializer(employee_commissions, many=True, context={'request': request}).data)
    paginator = CustomPagination()
    paginator.page_size = 100000 if no_pagination else 10
    paginated_data = paginator.paginate_queryset(serialized, request)
    response = paginator.get_paginated_response(paginated_data, 'sales', invoice_translations)
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def get_promotions_and_discounts_sales_detail(request):
    location_id = request.GET.get('location_id', None)
    search_text = request.GET.get('search_text', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    id = request.GET.get('id', None)

    if not all([location_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'location id is required',
                    'fields': [
                        'location',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    paginator = CustomPagination()
    paginator.page_size = 10

    query = Q(is_deleted=False, is_active=True, location__id=location_id)

    if id:
        query &= Q(id=id)

    if search_text:
        query = Q(invoice_id_str__icontains=search_text)
        query |= Q(promotion_name__icontains=search_text)

    if start_date and end_date:
        query &= Q(created_at__range=(start_date, end_date))

    sales = DiscountPromotionSalesReport.objects \
        .filter(query) \
        .select_related('location', 'client', 'invoice') \
        .annotate(invoice_id_str=Cast('invoice__id', CharField())) \
        .order_by('-created_at')

    data = DiscountPromotionSalesReport_serializer(sales, many=True, context={'request': request}).data

    paginated_data = paginator.paginate_queryset(data, request)

    business_address = BusinessAddress.objects.get(id=location_id)
    invoice_translations = BusinessAddressSerilaizer(business_address).data

    return paginator.get_paginated_response(paginated_data, 'sales', invoice_translations=invoice_translations)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_promotions_and_discounts_sales_list(request):
    location_id = request.GET.get('location_id', None)
    search_text = request.GET.get('search_text', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)

    if not all([location_id]):
        return Response(
            {
                'status': False,
                'status_code': StatusCodes.MISSING_FIELDS_4001,
                'status_code_text': 'MISSING_FIELDS_4001',
                'response': {
                    'message': 'Invalid Data!',
                    'error_message': 'location id is required',
                    'fields': [
                        'location',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    paginator = CustomPagination()
    paginator.page_size = 10

    query = Q(is_deleted=False, is_active=True, location__id=location_id, )

    if search_text:
        query = Q(invoice_id_str__icontains=search_text)
        query |= Q(promotion_name__icontains=search_text)

    if start_date and end_date:
        query &= Q(created_at__range=(start_date, end_date))

    sales = DiscountPromotionSalesReport.objects \
        .filter(query) \
        .select_related('location', 'client', 'invoice') \
        .annotate(invoice_id_str=Cast('invoice__id', CharField())) \
        .order_by('-created_at')

    data = DiscountPromotionSalesReport_serializerOP(sales, many=True, context={'request': request}).data

    paginated_data = paginator.paginate_queryset(data, request)

    return paginator.get_paginated_response(paginated_data, 'sales')


@api_view(['GET'])
@permission_classes([AllowAny])
def get_sales_record(request):
    retail_target = 0
    search_text = request.query_params.get('search_text', None)
    no_pagination = request.query_params.get('no_pagination', None)
    month = request.query_params.get('month', None)
    year = request.query_params.get('year', None)
    location_id = request.query_params.get('location_id', None)
    retail_target = RetailTarget.objects.all().order_by('-created_at').distinct()
    if location_id:
        retail_target = retail_target.filter(location=location_id)
    if year:
        retail_target = retail_target.filter(year__year=year).count()
    if month:
        retail_target = retail_target.filter(month=month).count()
    if location_id is None and year is None and month is None:
        retail_target = retail_target.count()
        retail_target = json.loads(retail_target)
    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'Successfully retrieve the record',
                'retail_target': str(retail_target)
            }
        },
        status=status.HTTP_200_OK
    )
    # if search_text:
    #     retail_target = retail_target.filter(brand__name__icontains=search_text)

    # paginator = AppointmentsPagination()
    # paginator.page_size = 10
    # retail_target = paginator.paginate_queryset(retail_target, request)
    # serialized = list(RetailTargetSerializers(retail_target, many=True, context={'request': request}).data)
    # paginator = CustomPagination()
    # paginator.page_size = 100000 if no_pagination else 10
    # paginated_data = paginator.paginate_queryset(serialized, request)
    # response = paginator.get_paginated_response(paginated_data, 'retailtarget')
    # return serialized
    # return Response(
    #     {
    #         'status': 200,
    #         'status_code': '200',
    #         'response': {
    #             'message': 'Successfully retrieve the record',
    #             'response':str(response)
    #         }
    #     },
    #     status=status.HTTP_200_OK
    # )
