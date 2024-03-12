import json
from datetime import timedelta
from datetime import datetime as dt
from django.db.models import Sum, Avg, FloatField
from django.db.models import Value
from datetime import date, timedelta
from django.db.models import CharField, Q
from django.db.models.functions import Cast
from django.db.models.functions import Coalesce


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
from TragetControl.models import *
from SaleRecords.models import *
from Reports.serializers import *

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
        retail_target = retail_target.filter(year__year=year)
    if month:
        retail_target = retail_target.filter(month=month)
    retail_target = retail_target.count()
    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'Successfully retrieve the record',
                'retail_target': retail_target
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
    

# Get Sales Analytics For POS Analytics ------------------------------------------------------------------------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def get_sales_analytics(request):
    location_id = request.GET.get('location_id', None)
    year = request.GET.get('year', None)
    month = request.GET.get('month', None)
    today = request.GET.get('today', None)
    
    query = Q()
    location = Q()
    business= Q()
    sale_record = Q()
    
    try:    
        if location_id:
            location &= Q(location=location_id)
            business &= Q(business_address=location_id)
            sale_record &= Q(sale_record__location_id=location_id)
            
            
        if year:
            query &= Q(created_at__year=year)
        
        if month:
            query &= Q(created_at__month=month)
        
        if today:
            query &= Q(created_at__date=today)
            
        # Get Target Data    
        service_target = ServiceTarget.objects.filter(query, location) \
                            .aggregate(total_service_target=Coalesce(Sum('service_target', output_field=FloatField()), Value(0, output_field=FloatField())))
        retail_target = RetailTarget.objects.filter(query, location) \
                            .aggregate(total_retail_target=Coalesce(Sum('brand_target', output_field=FloatField()), Value(0, output_field=FloatField())))
        
        # Get Sale Records
        service = SaleRecordServices.objects.filter(query, sale_record).aggregate(total_service_sale=Coalesce(Sum('price', output_field=FloatField()), Value(0, output_field=FloatField())))
        product = SaleRecordsProducts.objects.filter(query, sale_record).aggregate(total_product_sale=Coalesce(Sum('price', output_field=FloatField()), Value(0, output_field=FloatField())))
        vouchers = SaleRecordVouchers.objects.filter(query, sale_record).aggregate(total_vouchers_sale=Coalesce(Sum('price', output_field=FloatField()), Value(0, output_field=FloatField())))
        membership = SaleRecordMembership.objects.filter(query, sale_record).aggregate(total_membership_sale=Coalesce(Sum('price', output_field=FloatField()), Value(0, output_field=FloatField())))
        gift_card = PurchasedGiftCards.objects.filter(query, sale_record).aggregate(total_gift_card_sale=Coalesce(Sum('price', output_field=FloatField()), Value(0, output_field=FloatField())))
        appointment = SaleRecordsAppointmentServices.objects.filter(query, sale_record).aggregate(total_appointment_sale=Coalesce(Sum('price', output_field=FloatField()), Value(0, output_field=FloatField())))
        
        # appointment_average = SaleRecordsAppointmentServices.objects.filter(query) \
        #                         .aggregate(avg_appointment=Coalesce(Avg('price', output_field=FloatField()), Value(0, output_field=FloatField())))
        
        # Appointment Count
        cancel_appointment = Appointment.objects.filter(business, query, status='Cancelled').count()
        if location_id:
            query = Q(sale_record__location__id=location_id)
        finished_appointment = SaleRecordsAppointmentServices.objects.filter(query, appointment__status__in=['Paid', 'Done']).count()
        
        # Total Appointment count
        total_appointment = cancel_appointment + finished_appointment
        
        # Calculate the total sum
        total_sale = (
            service['total_service_sale'] +
            product['total_product_sale'] +
            vouchers['total_vouchers_sale'] +
            membership['total_membership_sale'] +
            gift_card['total_gift_card_sale'] +
            appointment['total_appointment_sale']
        )
        avg_sale = total_sale / 5 # average of 5 sales records
        
    # Total Sale Chat ----------------------------------------
        
        # Calculate Previous Year and Current Year
        current_year = date.today().year
        previous_year = current_year - 1
        months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        
        # Calculate previous year total sales for each month
        previous_year_sales = []
        for month in months:
            total_monthly_sale = SaleRecords.objects.filter(created_at__year=previous_year,
                                        created_at__month=month) \
                                        .aggregate(total=Coalesce(Sum('total_price', output_field=FloatField()), Value(0, output_field=FloatField())))
            
            previous_year_sales.append(total_monthly_sale['total'])
        
        # Calculate current year total sales for each month
        current_year_sales = []
        for month in months:
            total_monthly_sale = SaleRecords.objects.filter(created_at__year=current_year,
                                        created_at__month=month) \
                                        .aggregate(total=Coalesce(Sum('total_price', output_field=FloatField()), Value(0, output_field=FloatField())))
                                        
            current_year_sales.append(total_monthly_sale['total'])
                
    # Sales channel POS Reports -----------------------------------------

        total_pos_sale = 0.0
        current_year_pos_sales = []
        for month in months:
            total_monthly_pos_sale = SaleRecords.objects.filter(created_at__year=current_year,
                                        created_at__month=month) \
                                        .filter(location) \
                                        .aggregate(total=Coalesce(Sum('total_price', output_field=FloatField()), Value(0, output_field=FloatField())))
            
            current_year_pos_sales.append(total_monthly_pos_sale['total'])
            total_pos_sale = total_pos_sale + total_monthly_pos_sale['total']
        data = {
            'success': True,
            'status_code': status.HTTP_200_OK,
            'message': 'Data fetched successfully',
            'error_message': None,
            'data': {
                'sales_cards':{
                    'avg_sale': avg_sale,
                    'appointment_average': appointment['total_appointment_sale'],
                },
                'sales_progress': {
                    'service': {
                        'total_service_target': service_target['total_service_target'],
                        'service_total_sale': service['total_service_sale'],
                    },
                    'product': {
                        'total_retail_target': retail_target['total_retail_target'],
                        'product_total_sale': product['total_product_sale'],
                    },
                    'vouchers_total_sale': vouchers['total_vouchers_sale'],
                    'membership_total_sale': membership['total_membership_sale'],
                    'gift_card_total_sale': gift_card['total_gift_card_sale'],
                    'total_sale': total_sale,
                },
                'appointment_progress': {
                    'cancel_appointment': cancel_appointment,
                    'finished_appointment': finished_appointment,
                    'total_appointment': total_appointment,
                },
                'total_sale_chart' : {
                    'previous_year_sales': previous_year_sales,
                    'current_year_sales': current_year_sales,
                },
                'sales_channel_pos' : {
                    'total_pos_sale' : total_pos_sale,
                    'current_year_pos_sale' : current_year_pos_sales,
                },
            }   
        }
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        # Handle exceptions and return error response
        error_data = {
            'success': False,
            'status_code': 400,
            'message': 'Internal Server Error',
            'error_message': str(e),
            'data': None
        }
        return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_search_result_analytic(request):
    location_id = request.GET.get('location_id', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    
    query = Q()
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        # Add one day to end_date
        end_date += timedelta(days=1)
        # Convert it back to the desired format
        end_date = end_date.strftime('%Y-%m-%d')
    
    if location_id:
        query &= Q(sale_record__location_id=location_id)
    
    if start_date and end_date:
        query &= Q(created_at__range=(start_date, end_date))
        
    product = SaleRecordsProducts.objects.filter(query).distinct('product')
    
    paginator = AppointmentsPagination()
    paginator.page_size = 10
    page_result = paginator.paginate_queryset(product, request)
    
    product_records = ProductsReportSerializer(page_result, many=True,)
    
    data = {
        'success': True,
        'status_code': status.HTTP_200_OK,
        'message': 'Product fetched successfully',
        'error_message': None,
        'data': {
            'product_records': product_records.data,
            'count': paginator.page.paginator.count,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
            'current_page': paginator.page.number,
            'per_page': paginator.page_size,
            'total_pages': paginator.page.paginator.num_pages,
        }
    }
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_customer_analytics(request):
    location_id = request.GET.get('location_id', None)
    year = request.GET.get('year', None)
    month = request.GET.get('month', None)
    today = request.GET.get('today', None)
    
    try:
        query = Q()
        if location_id:
            query &= Q(sale_record__location_id=location_id)
        if year: 
            query &= Q(created_at__year=year)
        if month:
            query &= Q(created_at__month=month)
        if today:
            query &= Q(created_at__date=today)
            
            
        # Get Sale Records Against Client
        service = SaleRecordServices.objects.filter(query, sale_record__client_type='In_Saloon').aggregate(total_service_sale=Coalesce(Sum('price', output_field=FloatField()), Value(0, output_field=FloatField())))
        product = SaleRecordsProducts.objects.filter(query, sale_record__client_type='In_Saloon').aggregate(total_product_sale=Coalesce(Sum('price', output_field=FloatField()), Value(0, output_field=FloatField())))
        vouchers = SaleRecordVouchers.objects.filter(query, sale_record__client_type='In_Saloon').aggregate(total_vouchers_sale=Coalesce(Sum('price', output_field=FloatField()), Value(0, output_field=FloatField())))
        membership = SaleRecordMembership.objects.filter(query, sale_record__client_type='In_Saloon').aggregate(total_membership_sale=Coalesce(Sum('price', output_field=FloatField()), Value(0, output_field=FloatField())))
        gift_card = PurchasedGiftCards.objects.filter(query, sale_record__client_type='In_Saloon').aggregate(total_gift_card_sale=Coalesce(Sum('price', output_field=FloatField()), Value(0, output_field=FloatField())))
        appointment = SaleRecordsAppointmentServices.objects.filter(query, sale_record__client_type='In_Saloon').aggregate(total_appointment_sale=Coalesce(Sum('price', output_field=FloatField()), Value(0, output_field=FloatField())))
        
        # Calculate the total sum -----------------------------
        total_sale = (
            service['total_service_sale'] +
            product['total_product_sale'] +
            vouchers['total_vouchers_sale'] +
            membership['total_membership_sale'] +
            gift_card['total_gift_card_sale'] +
            appointment['total_appointment_sale']    
        )
        
        # Service Spending ------------------------------------
        service_avg = SaleRecordServices.objects.filter(query, sale_record__client_type='In_Saloon').aggregate(total_service_sale=Coalesce(Avg('price', output_field=FloatField()), Value(0, output_field=FloatField())))
        appointment_avg = SaleRecordsAppointmentServices.objects.filter(query, sale_record__client_type='In_Saloon').aggregate(total_appointment_sale=Coalesce(Avg('price', output_field=FloatField()), Value(0, output_field=FloatField())))
        
        service_spending = (
            service_avg['total_service_sale'] +
            appointment_avg['total_appointment_sale']
        )
        service_spending_avg = service_spending / 2
        
        # Service Spending Monthly Reports ---------------------
        query = Q()
        if location_id:
            query &= Q(sale_record__location_id=location_id)
            
        if year:
            current_year = year
        else:
            current_year = date.today().year
            
        months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        service_year_sales = []
        for month in months:
            total_monthly_service = SaleRecordServices.objects.filter(query, created_at__year=current_year,
                                                                    created_at__month=month, sale_record__client_type='In_Saloon').aggregate(total_service_sale=Coalesce(Sum('price', output_field=FloatField()), Value(0, output_field=FloatField())))
            total_monthly_appointment = SaleRecordServices.objects.filter(query, created_at__year=current_year,
                                                                    created_at__month=month, sale_record__client_type='In_Saloon').aggregate(total_service_sale=Coalesce(Sum('price', output_field=FloatField()), Value(0, output_field=FloatField())))
            total_service_sale = total_monthly_service['total_service_sale'] + total_monthly_appointment['total_service_sale']
            service_year_sales.append(total_service_sale)
        
        # Product Spending Monthly Reports ------------------------
        product_year_sales = []
        for month in months:
            total_monthly_product = SaleRecordsProducts.objects.filter(query, created_at__year=current_year,
                                                                    created_at__month=month, sale_record__client_type='In_Saloon').aggregate(total_product_sale=Coalesce(Sum('price', output_field=FloatField()), Value(0, output_field=FloatField())))
            product_year_sales.append(total_monthly_product['total_product_sale'])
            
        # Total Client -----------------------------------------
        total_client = Client.objects.filter(is_deleted=False).count()
        data = {
                'success': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Customer analytics Data fetched successfully',
                'error_message': None,
                'data': {
                    'sales_cards':{
                        'total_customer': total_client,
                        'total_customer_sale': total_sale,
                    },
                    'service_spending' : {
                        'service_spending_avg': service_spending_avg,
                        'service_yearly_sales': service_year_sales,
                    },
                    'product_spending' : {
                        'product_total_sale': product['total_product_sale'],
                        'product_yearly_sales': product_year_sales,
                        
                    },
                    
                }
        }
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        # Handle exceptions and return error response
        error_data = {
            'success': False,
            'status_code': 400,
            'message': 'Internal Server Error',
            'error_message': str(e),
            'data': None
        }
        return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
    