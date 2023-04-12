from django.conf import settings
from operator import ge
from Appointment.serializers import CheckoutSerializer
from Order.models import Checkout, ProductOrder,VoucherOrder,MemberShipOrder,ServiceOrder
from Utility.Constants.Data.months import  FIXED_MONTHS, MONTHS
from Order.models import Order, ProductOrder,VoucherOrder,MemberShipOrder,ServiceOrder,Checkout
from Sale.serializers import AppointmentCheckoutSerializer, CheckoutSerializer, OrderSerializer
from Utility.Constants.Data.months import  FIXED_MONTHS, MONTH_DICT, MONTHS, MONTHS_DEVICE

from Dashboard.serializers import EmployeeDashboradSerializer
from Employee.models import Employee,CategoryCommission,CommissionSchemeSetting
from TragetControl.models import StaffTarget
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from Appointment.models import Appointment, AppointmentCheckout, AppointmentService
from Client.models import Client
from NStyle.Constants import StatusCodes
from Business.models import Business, BusinessAddress
from Product.models import ProductStock
from datetime import datetime,timedelta

@api_view(['GET'])
@permission_classes([AllowAny])
def get_busines_client_appointment(request):
    business_id = request.GET.get('location', None)
    duration = request.GET.get('duration', None) 
    
    if business_id is None:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Following fields are required',
                    'fields' : [
                        'business',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    avg = 0
    revenue = 0
    footfalls = 0
    total_price = 0
    appointment = 0

    footfalls = Client.objects.filter(is_deleted=False, client_appointments__appointment_services__appointment_status='Appointment_Booked').count()
    # footfalls = AppointmentService.objects.filter(is_deleted=False).exclude(appointment_status__iexact ='cancel').count()
    

    client_count = Client.objects.prefetch_related('client_appointments__business_address').filter(client_appointments__business_address__id = business_id).count()
 
    if duration is not None:
        today = datetime.today()
        day = today - timedelta(days=int(duration))
        checkouts = AppointmentCheckout.objects.filter(business_address__id = business_id, created_at__gte = day)
    else:
        checkout_orders_total = Checkout.objects.filter(
        is_deleted=False, 
        location__id = business_id
        #member__id=employee_id,
        )   
        
        checkouts = AppointmentCheckout.objects.filter(
            is_deleted=False, 
            business_address__id = business_id
            #member__id=employee_id,
        )
        
        for price in checkout_orders_total:
            total_price += int(price.total_service_price or 0)
            total_price += int(price.total_product_price or 0)
            total_price += int(price.total_voucher_price or 0)
            total_price += int(price.total_membership_price or 0)
        
        for price in checkouts:
            appointment +=1
            total_price += int(price.total_price or 0)
    #     checkouts = AppointmentCheckout.objects.filter(business_address__id = business_id)
    # for check in checkouts:
    #     appointment +=1
    #     if check.total_price is not None:
    #         revenue += check.total_price
    
    avg = appointment / footfalls if footfalls > 0 else 0
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'Total Revenue',
                'error_message' : None,
                'revenue' : total_price,
                'client_count':client_count,
                'footfalls': footfalls,
                'appointments_count': appointment,
                'average_appointent':avg,
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_dashboard_day_wise(request):
    date = request.GET.get('date', None)
    #date = '2022-10-22'
    total_revenue = 0
    appointments_count = 0
    total_client = 0
    appointment = AppointmentCheckout.objects.filter(is_deleted=False)
    for app in appointment:
        create_at = str(app.created_at)
        if (create_at.split(" ")[0] == date ):
            appointments_count +=1
            if app.total_price is not None:
                total_revenue += app.total_price
        
    client = Client.objects.filter(is_deleted=False)
    for cl in client:
        create_at = str(cl.created_at)
        if (create_at.split(" ")[0] == date ):
            total_client +=1
    
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'Total Revenue',
                'error_message' : None,
                'revenue' : total_revenue,
                'appointments_count': appointments_count,
                'total_client': total_client,
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_appointments_client(request):
    businesaddress= request.data.get('businesaddress', None)
    appointment = AppointmentCheckout.objects.filter(appointment_service__business_address= businesaddress)
    for i in appointment:
        print(i)
    print('hello')
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Appointment',
                'error_message' : None,
                #'appointments' : serialize.data
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_dashboard_targets(request):
    employee_id = request.data.get('employee_id', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)

    if not all([employee_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Employee id are required',
                    'fields' : [
                        'employee_id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try: 
        employee_id = Employee.objects.get(id=employee_id, is_deleted=False)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_EMPLOYEE_4025,
                    'status_code_text' : 'INVALID_EMPLOYEE_4025',
                    'response' : {
                        'message' : 'Employee Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
    serialized = EmployeeDashboradSerializer(employee_id, context={
                        'request' : request, 
                        'range_start': start_date, 
                        'range_end': end_date, 
            })
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'Employee',
                'error_message' : None,
                'employee' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_acheived_target_report(request):
    employee_id = request.GET.get('employee_id', None)
    start_month =  request.GET.get('start_month', None)
    end_month = request.GET.get('end_month', None)
    start_year = request.GET.get('start_year', 1900)
    end_year = request.GET.get('end_year', 3000)

    if not all([employee_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required',
                    'fields' : [
                        'employee_id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try: 
        employee = Employee.objects.get(id=employee_id, is_deleted=False)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_EMPLOYEE_4025,
                    'status_code_text' : 'INVALID_EMPLOYEE_4025',
                    'response' : {
                        'message' : 'Employee Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
    if start_month is not None and end_month is not None :
        start_index = FIXED_MONTHS.index(start_month) # 1
        end_index = FIXED_MONTHS.index(end_month) # 9
        fix_months = FIXED_MONTHS[start_index : end_index]
    else:
        fix_months = FIXED_MONTHS
        print(fix_months)
    
    targets = StaffTarget.objects.filter(
        employee_id = employee_id,
        month__in = fix_months, # 8
        year__gte = start_year,
        year__lte = end_year,
    )
    acheived=0
    if len(targets) >0:
        for target in targets :
            s = target.service_target
            r = target.retail_target
            acheived = acheived + s + r
    print(acheived)
    return Response(
            {
                'status' : 200,
                'status_code' : '200',
                'response' : {
                    'message' : 'achieved Target',
                    'error_message' : None,
                    'employee_id' : employee_id,
                    'total_achieved_targets' : acheived,
                }
            },
            status=status.HTTP_200_OK
        )
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_dashboard_target_overview(request):

    employee_id = request.GET.get('employee_id', None)
    
    range_start =  request.GET.get('range_start', '1990-01-01')
    range_end = request.GET.get('range_end', '2050-12-20')
    

    # employee_id = request.GET.get('employee_id', None)
    # start_month =  request.GET.get('start_month', None)
    # end_month = request.GET.get('end_month', None)
    # start_year = request.GET.get('start_year', '1900-01-01')
    # end_year = request.GET.get('end_year', '3000-12-30')

    if not all([employee_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required',
                    'fields' : [
                        'employee_id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try: 
        employee = Employee.objects.get(id=employee_id, is_deleted=False)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_EMPLOYEE_4025,
                    'status_code_text' : 'INVALID_EMPLOYEE_4025',
                    'response' : {
                        'message' : 'Employee Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
    #achieved_target_member = ProductOrder.objects.filter(member = employee_id)
    sum_service_targets=0
    sum_retail_target= 0
    sum_total_set = 0
    sum_acheived_voucher_target = 0
    sum_acheived_service_target = 0
    sum_acheived_retail_target = 0
    sum_acheived_membership_target = 0
    sum_acheived_voucher_target = 0
    sum_total_acheived = 0
    
    # if range_start:
    #     range_start = datetime.strptime(range_start, "%Y-%m-%d")
    #     range_end = datetime.strptime(range_end, "%Y-%m-%d")

    appointment_checkout = AppointmentService.objects.filter(
        appointment_status = 'Done',
        member__id = employee_id,
        created_at__gte =  range_start ,
        created_at__lte = range_end
        ).values_list('total_price', flat=True)
    sum_total_acheived += sum(appointment_checkout)


    targets = StaffTarget.objects.filter(
        # is_deleted=False,
        employee__id = employee_id,
        created_at__gte =  range_start ,
        created_at__lte = range_end
        )
    targets.values_list('service_target', flat=True)
    targets.values_list('retail_target', flat=True)
    
    service_targets = ServiceOrder.objects.filter(
        member__id = employee_id,
        created_at__gte =  range_start ,
        created_at__lte = range_end
    ).values_list('service_target', flat=True)
    all_service_targets += sum(service_targets)

    retail_targets = ProductOrder.objects.filter(
        member__id = employee_id,
        created_at__gte =  range_start ,
        created_at__lte = range_end
    ).values_list('retail_targets', flat=True)
    all_retail_targets += sum(retail_targets)
    
    voucher_targets = VoucherOrder.objects.filter(
        member__id = employee_id,
        created_at__gte =  range_start ,
        created_at__lte = range_end
    ).values_list('voucher_targets', flat=True)
    all_voucher_targets += sum(voucher_targets)

    membership_targets = MemberShipOrder.objects.filter(
        member__id = employee_id,
        created_at__gte =  range_start ,
        created_at__lte = range_end
    ).values_list('membership_targets', flat=True)
    all_membership_targets += sum(membership_targets)

    sum_total_set = sum([retail_targets,service_targets])

    # all_service_targets = targets.values_list('service_targets', flat=True)
    # print(all_service_targets)
    # sum_service_targets = sum(all_service_targets)

    # all_retail_target = targets.values_list('retail_targets', flat=True)
    # print(all_retail_target)
    # sum_retail_target = sum(all_retail_target)

    # sum_total_set = sum([sum_retail_target,sum_service_targets])
    
    all_achieved_voucher_target = voucher_targets.values_list('total_price', flat=True)
    print(all_achieved_voucher_target)
    sum_acheived_voucher_target = sum(all_achieved_voucher_target)

    all_acheived_service_target = service_targets.values_list('total_price', flat=True)
    print(all_acheived_service_target)
    sum_acheived_service_target = sum(all_acheived_service_target)

    all_acheived_retail_target = targets.values_list('total_price', flat=True)
    print(all_acheived_retail_target)
    sum_acheived_retail_target = sum(all_acheived_retail_target)

    all_acheived_membership_target = membership_targets.values_list('total_price', flat=True)
    print(all_acheived_membership_target)
    sum_acheived_membership_target = sum(all_acheived_membership_target)

    all_acheived_voucher_target = voucher_targets.values_list('total_price', flat=True)
    print(all_acheived_voucher_target)
    sum_acheived_voucher_target = sum(all_acheived_voucher_target)

    sum_total_acheived=sum([sum_acheived_voucher_target,sum_acheived_membership_target,sum_retail_target,sum_service_targets,])

    return Response(
            {
                'status' : 200,
                'status_code' : '200',
                'response' : {
                    'message' : 'Employee Id recieved',
                    'error_message' : None,
                    'employee_id' : employee_id,

                    'set' : {
                        'service' : sum_service_targets,
                        'retail' : sum_retail_target,
                        'total' : sum_total_set
                    },
                    'acheived' : {
                        'membership' : sum_acheived_membership_target,
                        'voucher' : sum_acheived_voucher_target,
                        'service' : sum_acheived_service_target,
                        'retail' : sum_acheived_retail_target,
                        'total' : sum_total_acheived
                    }
                }
            },
            status=status.HTTP_200_OK
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_total_tips(request):
    employee_id = request.GET.get('employee_id', None)
    range_start =  request.GET.get('range_start', None)
    range_end = request.GET.get('range_end', None)
    total_tips = 0
    
    if range_start:
        range_start = datetime.strptime(range_start, "%Y-%m-%d")
        range_end = datetime.strptime(range_end, "%Y-%m-%d")
    
        checkout_order = Checkout.objects.filter(
            is_deleted=False,
            member__id = employee_id,
            created_at__gte =  range_start ,
            created_at__lte = range_end
            ).values_list('tip', flat=True)
        total_tips += sum(checkout_order)
        
        appointment_checkout = AppointmentCheckout.objects.filter(
            appointment_service__appointment_status = 'Done',
            member__id = employee_id,
            created_at__gte =  range_start ,
            created_at__lte = range_end
            ).values_list('tip', flat=True)
        total_tips += sum(appointment_checkout)
        
    else:
        checkout_order = Checkout.objects.filter(
            is_deleted=False,
            member__id = employee_id,
            ).values_list('tip', flat=True)
        total_tips += sum(checkout_order)

        appointment_checkout = AppointmentCheckout.objects.filter(
            appointment_service__appointment_status = 'Done',
            member__id = employee_id,
            ).values_list('tip', flat=True)
        total_tips += sum(appointment_checkout)
    
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Sale Orders',
                'error_message' : None,
                'sales' : total_tips
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_total_comission(request):
    employee_id = request.GET.get('employee_id', None)
    range_start =  request.GET.get('range_start', None)
    range_end = request.GET.get('range_end', None)
    sum_total_commision = 0
    total_service_comission = 0
    total_product_comission = 0
    total_voucher_comission = 0
    

    if range_start:
        range_start = datetime.strptime(range_start, "%Y-%m-%d")#.date()
        range_end = datetime.strptime(range_end, "%Y-%m-%d")#

        service_commission = Checkout.objects.filter(
            is_deleted=False,
            member__id = employee_id,
            created_at__gte =  range_start ,
            created_at__lte = range_end
            ).values_list('service_commission', flat=True)
        service_commission = [i for i in service_commission if i]
        total_service_comission += sum(service_commission)

        product_commission = Checkout.objects.filter(
            is_deleted=False,
            member__id = employee_id,
            created_at__gte =  range_start ,
            created_at__lte = range_end
            ).values_list('product_commission', flat=True)
        product_commission = [i for i in product_commission if i]
        total_product_comission += sum(product_commission)

        voucher_commission = Checkout.objects.filter(
            is_deleted=False,
            member__id = employee_id,
            created_at__gte =  range_start ,
            created_at__lte = range_end
            ).values_list('voucher_commission', flat=True)
        voucher_commission = [i for i in voucher_commission if i]
        total_voucher_comission += sum(voucher_commission)
        # sum_total_commision = sum([total_service_comission,total_product_comission,total_voucher_comission])
        
    else:
        service_commission = Checkout.objects.filter(
            is_deleted=False,
            member__id = employee_id,
            ).values_list('service_commission', flat=True)
        service_commission = [i for i in service_commission if i]
        total_service_comission += sum(service_commission)

        product_commission = Checkout.objects.filter(
            is_deleted=False,
            member__id = employee_id,
            ).values_list('product_commission', flat=True)
        product_commission = [i for i in product_commission if i]
        total_product_comission += sum(product_commission)

        voucher_commission = Checkout.objects.filter(
            is_deleted=False,
            member__id = employee_id,
            ).values_list('voucher_commission', flat=True)
        voucher_commission = [i for i in voucher_commission if i]
        total_voucher_comission += sum(voucher_commission)
    sum_total_commision = sum([total_service_comission,total_product_comission,total_voucher_comission])
    
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Commision Orders',
                'error_message' : None,
                'total commsion' : sum_total_commision,
                'Service': total_service_comission,
                'Retail' : total_product_comission,
                'Voucher' : total_voucher_comission,
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_total_sales_device(request):
    employee_id = request.GET.get('employee_id', None)
    total_price = 0
    
    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    checkout_orders = Checkout.objects.filter(
        is_deleted=False, 
        member__id=employee_id,
    ).values_list('created_at__month', flat=True)


    apps_checkouts = AppointmentCheckout.objects.filter(
        is_deleted=False, 
        member__id=employee_id,
    ).values_list('created_at__month', flat=True)
    checkout_orders = list(checkout_orders)
    apps_checkouts = list(apps_checkouts)
    
    checkout_orders_total = Checkout.objects.filter(
        is_deleted=False, 
        member__id=employee_id,
    )   
    
    apps_checkouts_total = AppointmentCheckout.objects.filter(
        is_deleted=False, 
        member__id=employee_id,
    )
    
    for price in checkout_orders_total:
        total_price += int(price.total_service_price or 0)
        total_price += int(price.total_product_price or 0)
        total_price += int(price.total_voucher_price or 0)
        total_price += int(price.total_membership_price or 0)
    
    for price in apps_checkouts_total:
        total_price += int(price.total_price or 0)

    dashboard_data = []
    for index, month in enumerate(months):
        i = index + 1
        count = checkout_orders.count(i)
        count_app = apps_checkouts.count(i)
        
        #total_sales += count + count_app

        dashboard_data.append({
            'month' : month,
            'count' : count + count_app
        })

    return Response(
        {
            'status': 200,
            'status_code': '200',
            'response': {
                'message': 'Graph for mobile',
                'error_message': None,
                'dashboard': dashboard_data,
                'total_sales': total_price
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_dashboard_target_overview_update(request):
    employee_id = request.GET.get('employee_id', None)
    
    range_start =  request.GET.get('range_start', '1990-01-01')
    range_end = request.GET.get('range_end', '2050-12-20')
    
    service_target = 0
    retail_target = 0
    service_sale = 0
    retail_sale = 0
    
    if not all([employee_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required',
                    'fields' : [
                        'employee_id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try: 
        employee = Employee.objects.get(id=employee_id, is_deleted=False)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_EMPLOYEE_4025,
                    'status_code_text' : 'INVALID_EMPLOYEE_4025',
                    'response' : {
                        'message' : 'Employee Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
    if range_start:
        range_start = datetime.strptime(range_start, "%Y-%m-%d")
        range_end = datetime.strptime(range_end, "%Y-%m-%d")
        
        targets = StaffTarget.objects.filter(
            # is_deleted=False,
            employee = employee,
            created_at__gte =  range_start ,
            created_at__lte = range_end
            )
        for tar in targets:
            service_target += int(tar.service_target)
            retail_target += int(tar.retail_target)
        
        appointment_checkout = AppointmentService.objects.filter(
            appointment_status = 'Done',
            member = employee,
            created_at__gte =  range_start ,
            created_at__lte = range_end
            ).values_list('total_price', flat=True)
        service_sale += sum(appointment_checkout)
        
        service_order_sale = ServiceOrder.objects.filter(
            member = employee,
            created_at__gte =  range_start ,
            created_at__lte = range_end
        )#.values_list('service_target', flat=True)
        for ser in service_order_sale:
            
            service_sale += int(ser.checkout.total_service_price or 0)

        retail_order_sale = ProductOrder.objects.filter(
            member = employee,
            created_at__gte =  range_start ,
            created_at__lte = range_end
        )#.values_list('retail_targets', flat=True)
        for pro in retail_order_sale:
            retail_sale += int(pro.checkout.total_product_price or 0)
    else:
        targets = StaffTarget.objects.filter(
            # is_deleted=False,
            employee = employee,
            )
        for tar in targets:
            service_target += int(tar.service_target)
            retail_target += int(tar.retail_target)
        
        appointment_checkout = AppointmentService.objects.filter(
            appointment_status = 'Done',
            member = employee,
            ).values_list('total_price', flat=True)
        service_sale += sum(appointment_checkout)
        
        service_order_sale = ServiceOrder.objects.filter(
            member = employee,
        )
        for ser in service_order_sale:
            service_sale += int(ser.checkout.total_service_price or 0)

        retail_order_sale = ProductOrder.objects.filter(
            member = employee,
        )
        for pro in retail_order_sale:
            retail_sale += int(pro.checkout.total_product_price or 0)
        
    total_targets = service_target + retail_target
    total_sale = service_sale + retail_sale
    
    return Response(
            {
                'status' : 200,
                'status_code' : '200',
                'response' : {
                    'message' : 'Employee Id recieved',
                    'error_message' : None,
                    'employee_id' : employee_id,

                    'set' : {
                        'service' : service_target,
                        'retail' : retail_target,
                        'total' : total_targets
                    },
                    'acheived' : {
                        'service' : service_sale,
                        'retail' : retail_sale,
                        'total' : total_sale
                    }
                }
            },
            status=status.HTTP_200_OK
        )