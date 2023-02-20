from django.conf import settings
from operator import ge
from Order.models import Checkout, ProductOrder,VoucherOrder,MemberShipOrder,ServiceOrder,Order
# from TragetControl.models import TierStoreTarget

from Utility.Constants.Data.months import  FIXED_MONTHS,MONTHS
from Dashboard.serializers import EmployeeDashboradSerializer
from Employee.models import Employee,CategoryCommission,CommissionSchemeSetting
from TragetControl.models import StaffTarget
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from Appointment.models import Appointment, AppointmentCheckout
from Client.models import Client
from NStyle.Constants import StatusCodes
from Business.models import Business, BusinessAddress
from Product.models import ProductStock

from datetime import datetime
from datetime import timedelta

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
    revenue = 0
    appointment = 0
        
    #client_count = Client.objects.filter(client_appointments__business_address__id = business_id).prefetch_related('client_appointments__business_address')
    client_count = Client.objects.prefetch_related('client_appointments__business_address').filter(client_appointments__business_address__id = business_id).count()
 
    # checkouts = AppointmentCheckout.objects.filter(business_address__id = business_id).values_list('total_price', flat=True)
    # check = [int(ck) for ck in checkouts]
    # checkouts = sum(check)
    if duration is not None:
        today = datetime.today()
        day = today - timedelta(days=int(duration))
        checkouts = AppointmentCheckout.objects.filter(business_address__id = business_id, created_at__gte = day)
    else:
        checkouts = AppointmentCheckout.objects.filter(business_address__id = business_id)
    for check in checkouts:
        appointment +=1
        if check.total_price is not None:
            revenue += check.total_price

    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'Total Revenue',
                'error_message' : None,
                'revenue' : revenue,
                'client_count': client_count,
                'appointments_count': appointment,
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
                        # 'start_month',
                        # 'start_year',
                        # 'end_month',
                        # 'end_year',
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
    start_month =  request.GET.get('start_month', None)
    end_month = request.GET.get('end_month', None)
    start_year = request.GET.get('start_year', '1900-01-01')
    end_year = request.GET.get('end_year', '3000-12-30')

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

    # service_target = StaffTarget.objects.filter(employee = employee_id)
    # retail_target = StaffTarget.objects.filter(employee = employee_id)
    # voucher_targets = TierStoreTarget.objects.filter(voucher_target = 'voucher_target')
    # membership_targets = TierStoreTarget.objects.filter(membership_target = 'membership_target')
                    
    achieved_target_member = ProductOrder.objects.filter(member = employee_id)

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

    service_targets = ServiceOrder.objects.filter(
        service = employee_id,
        
    )
    membership_targets = MemberShipOrder.objects.filter(
        membership = employee_id,
        
    )
    voucher_targets = VoucherOrder.objects.filter(
        voucher = employee_id,
        
    )
    





    all_service_targets = targets.values_list('service_target', flat=True)
    print(all_service_targets)
    sum_service_targets = sum(all_service_targets)

    all_retail_target = targets.values_list('retail_target', flat=True)
    print(all_retail_target)
    sum_retail_target = sum(all_retail_target)

    
    sum_total_set=sum([sum_retail_target,sum_service_targets])
    
    all_achieved_voucher_target = voucher_targets.values_list('voucher', flat=True)
    print(all_achieved_voucher_target)
    sum_acheived_voucher_target = sum(all_achieved_voucher_target)

    all_acheived_service_target = service_targets.values_list('service', flat=True)
    print(all_acheived_service_target)
    sum_acheived_service_target = sum(all_acheived_service_target)

    all_acheived_retail_target = targets.values_list('retail_target', flat=True)
    print(all_acheived_retail_target)
    sum_acheived_retail_target = sum(all_acheived_retail_target)

    all_acheived_membership_target = membership_targets.values_list('membership', flat=True)
    print(all_acheived_membership_target)
    sum_acheived_membership_target = sum(all_acheived_membership_target)

    all_acheived_voucher_target = voucher_targets.values_list('voucher', flat=True)
    print(all_acheived_voucher_target)
    sum_acheived_voucher_target = sum(all_acheived_voucher_target)

    sum_total_acheived=sum([sum_acheived_voucher_target,sum_acheived_membership_target,sum_retail_target,sum_service_targets,])

    # v1=0
    # v2=0
    # m1=0
    # m2=0
    # s1=0
    # s2=0
    # r1=0
    # r2=0

    # for target in targets :
    #     v1 = target.voucher_target.acheived_target.count()
    #     v2 = target.voucher_target.total_set.count()
    #     m1 = target.membership_target.acheived_target.count()
    #     m2 = target.membership_target.total_set.count()
    #     s1 = target.service_target.acheived_target.count()
    #     s2 = target.service_target.total_set.count()
    #     r1 = target.retail_target.acheived_target.count()
    #     r2 = target.retail_target.total_set.count()
        
    return Response(
            {
                'status' : 200,
                'status_code' : '200',
                'response' : {
                    'message' : 'Employee Id recieved',
                    'error_message' : None,
                    'employee_id' : employee_id,
                    # 'total_set' : sum_total_set,
                    # 'achieved_target' : sum_acheived_target,

                    # 'service_target_set' : sum_service_targets,
                    # 'service_target_acheived' : sum_acheived_service_target,

                    # 'retail_target_set' : sum_retail_target,
                    # 'retail_target_acheived' : sum_acheived_retail_target,

                    # 'voucher_target_set' : sum_voucher_target,
                    # 'voucher_target_acheived' : sum_acheived_voucher_target,

                    # 'membership_target_set' : sum_membership_target,
                    # 'membership_target_acheived' : sum_acheived_membership_target,
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

# @api_view(['GET'])
# @permission_classes([AllowAny])
# def get_total_comission(request):
    
#     employee_id = request.GET.get('employee_id', None)
#     # start_month =  request.GET.get('start_month', None)
#     # end_month = request.GET.get('end_month', None)
#     # start_year = request.GET.get('start_year', '1900-01-01')
#     # end_year = request.GET.get('end_year', '3000-12-30')
    

#     if not all([employee_id ]):
#         return Response(
#             {
#                 'status' : False,
#                 'status_code' : StatusCodes.MISSING_FIELDS_4001,
#                 'status_code_text' : 'MISSING_FIELDS_4001',
#                 'response' : {
#                     'message' : 'Invalid Data!',
#                     'error_message' : 'All fields are required',
#                     'fields' : [
#                         'employee_id',
#                     ]
#                 }
#             },
#             status=status.HTTP_400_BAD_REQUEST
#         )
    
#     try: 
#         employee = Employee.objects.get(id=employee_id, is_deleted=False)
#     except Exception as err:
#         return Response(
#                 {
#                     'status' : False,
#                     'status_code' : StatusCodes.INVALID_EMPLOYEE_4025,
#                     'status_code_text' : 'INVALID_EMPLOYEE_4025',
#                     'response' : {
#                         'message' : 'Employee Not Found',
#                         'error_message' : str(err),
#                     }
#                 },
#                 status=status.HTTP_404_NOT_FOUND
#             )
#     service=0
#     retail=0
#     voucher=0

#     services = Checkout.objects.filter(
#         service_commission = employee_id, 
#     )
#     retails = Checkout.objects.filter(
#         product_commission = employee_id, 
#     )
#     vouchers = Checkout.objects.filter(
#         voucher_commission = employee_id, 
#     )

#     service_comission = services.values_list('category_comission', flat=True)
#     print(service_comission)
#     sum_service_comission = sum(service_comission)

#     retail_comission = retails.values_list('category_comission', flat=True)
#     print(retail_comission)
#     sum_retail_comission = sum(retail_comission)

#     voucher_comission = vouchers.values_list('category_comission', flat=True)
#     print(voucher_comission)
#     sum_voucher_comission = sum(voucher_comission)

#     sum_total_commision=sum([sum_voucher_comission,sum_retail_comission,sum_service_comission])

    
#     return Response(
#             {
#                 'status' : 200,
#                 'status_code' : '200',
#                 'response' : {
#                     'message' : 'Employee Id recieved',
#                     'error_message' : None,
#                     'employee_id' : employee_id,
#                     'total_commision' : sum_total_commision,
#                     'service_comission' : sum_service_comission,
#                     'retail_comission' : sum_retail_comission,
#                     'voucher_comission' : sum_voucher_comission,
                    
#                 }
#             },
#             status=status.HTTP_200_OK
#         )

    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_total_tips(request):
    employee_id = request.GET.get('employee_id', None)
    range_start =  request.GET.get('range_start', None)
    range_end = request.GET.get('range_end', None)
    total_tips = 0
    
    if range_start:
        range_start = datetime.strptime(range_start, "%Y-%m-%d")#.date()
        range_end = datetime.strptime(range_end, "%Y-%m-%d")#
    
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
            # created_at__gte =  range_start ,
            # created_at__lte = range_end
            ).values_list('tip', flat=True)
        total_tips += sum(checkout_order)

        appointment_checkout = AppointmentCheckout.objects.filter(
            appointment_service__appointment_status = 'Done',
            member__id = employee_id,
            # created_at__gte =  range_start,
            # created_at__lte = range_end
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
        total_service_comission += sum(service_commission)

        product_commission = Checkout.objects.filter(
            is_deleted=False,
            member__id = employee_id,
            created_at__gte =  range_start ,
            created_at__lte = range_end
            ).values_list('product_commission', flat=True)
        total_product_comission += sum(product_commission)

        voucher_commission = Checkout.objects.filter(
            is_deleted=False,
            member__id = employee_id,
            created_at__gte =  range_start ,
            created_at__lte = range_end
            ).values_list('voucher_commission', flat=True)
        total_voucher_comission += sum(voucher_commission)
        
        

        sum_total_commision = sum([total_service_comission,total_product_comission,total_voucher_comission])


        
    else:
        service_commission = Checkout.objects.filter(
            is_deleted=False,
            member__id = employee_id,
            # created_at__gte =  range_start ,
            # created_at__lte = range_end
            ).values_list('service_commission', flat=True)
        total_service_comission += sum(service_commission)

        product_commission = Checkout.objects.filter(
            is_deleted=False,
            member__id = employee_id,
            # created_at__gte =  range_start ,
            # created_at__lte = range_end
            ).values_list('product_commission', flat=True)
        total_product_comission += sum(product_commission)

        voucher_commission = Checkout.objects.filter(
            is_deleted=False,
            member__id = employee_id,
            # created_at__gte =  range_start ,
            # created_at__lte = range_end
            ).values_list('voucher_commission', flat=True)
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
def get_total_sales(request):
    employee_id = request.GET.get('employee_id', None)
    # range_start =  request.GET.get('range_start', None)
    # range_end = request.GET.get('range_end', None)
    start_month = request.GET.get('start_month', None)
    end_month = request.GET.get('end_month', None)
    sum_total_sales = 0
    total_service_sales = 0
    total_membership_sales = 0
    total_voucher_sales = 0
    order=0
    sale_jan = 0
    sale_feb = 0
    sale_mar = 0
    sale_apr = 0
    sale_may = 0
    sale_jun = 0
    sale_july = 0
    sale_aug = 0
    sale_sep = 0
    sale_oct = 0
    sale_nov = 0
    sale_dec = 0
    
    if start_month is not None and end_month is not None :

        start_index = FIXED_MONTHS.index(start_month) # 1
        end_index = FIXED_MONTHS.index(end_month) # 9
        fix_months = FIXED_MONTHS[start_index : end_index]

        service_sales = ServiceOrder.objects.filter(
            is_deleted=False,
            service = employee_id,
            # created_at__gte =  range_start ,
            # created_at__lte = range_end
            month__in = fix_months,
            ).values_list('service', flat=True)
        total_service_sales += sum(service_sales)

        membership_sales = MemberShipOrder.objects.filter(
            is_deleted=False,
            membership = employee_id,
            # created_at__gte =  range_start ,
            # created_at__lte = range_end
            month__in = fix_months,
            ).values_list('membership', flat=True)
        total_membership_sales += sum(membership_sales)

        voucher_sales = VoucherOrder.objects.filter(
            is_deleted=False,
            voucher = employee_id,
            # created_at__gte =  range_start ,
            # created_at__lte = range_end
            month__in = fix_months,
            ).values_list('voucher', flat=True)
        total_voucher_sales += sum(voucher_sales)

        sum_total_sales = sum([total_service_sales,total_membership_sales,total_voucher_sales])

        
    else:

        service_sales = ServiceOrder.objects.filter(
            is_deleted=False,
            service = employee_id,
            ).values_list('service', flat=True)
        total_service_sales += sum(service_sales)

        membership_sales = MemberShipOrder.objects.filter(
            is_deleted=False,
            membership = employee_id,
            ).values_list('membership', flat=True)
        total_membership_sales += sum(membership_sales)

        voucher_sales = VoucherOrder.objects.filter(
            is_deleted=False,
            voucher = employee_id,
            ).values_list('voucher', flat=True)
        total_voucher_sales += sum(voucher_sales)
        
        sum_total_sales = sum([total_service_sales,total_membership_sales,total_voucher_sales])
            
            
        # fix_months = FIXED_MONTHS.count()
        # print(fix_months)

    orders = Order.objects.filter(is_deleted=False)
    for order in orders:
        create_at = str(order.created_at)
        
        sale_jan = int(create_at.split(" ")[0].split("-")[1])
        sale_feb = int(create_at.split(" ")[0].split("-")[1])
        sale_mar = int(create_at.split(" ")[0].split("-")[1])
        sale_apr = int(create_at.split(" ")[0].split("-")[1])
        sale_may = int(create_at.split(" ")[0].split("-")[1])
        sale_jun = int(create_at.split(" ")[0].split("-")[1])
        sale_july = int(create_at.split(" ")[0].split("-")[1])
        sale_aug = int(create_at.split(" ")[0].split("-")[1])
        sale_sep = int(create_at.split(" ")[0].split("-")[1])
        sale_oct = int(create_at.split(" ")[0].split("-")[1])
        sale_nov = int(create_at.split(" ")[0].split("-")[1])
        sale_dec = int(create_at.split(" ")[0].split("-")[1])

        if( sale_jan == 0 ):
            
            data['sale_jan'] +=1
            MONTHS[0]['sales'] = data['sale_jan']
            
        if( sale_feb == 1 ):
            
            data['sale_feb'] +=1
            MONTHS[1]['sales'] = data['sale_feb']
            
        if( sale_mar == 2 ):
           
            data['sale_mar'] +=1
            MONTHS[2]['sales'] = data['sale_mar']
            
        if( sale_apr == 3 ):
            
            data['sale_apr'] +=1
            MONTHS[3]['sales'] = data['sale_apr']
            
        if( sale_may == 4 ):
            
            data['sale_may'] +=1
            MONTHS[4]['sales'] = data['sale_may']
            
        if( sale_jun == 5 ):
            
            data['sale_jun'] +=1
            MONTHS[5]['sales'] = data['sale_jun']
        if( sale_july == 6 ):
            
            data['sale_july'] +=1
            MONTHS[6]['sales'] = data['sale_july']
            
        if( sale_aug == 7 ):
            
            data['sale_aug'] +=1
            MONTHS[7]['sales'] = data['sale_aug']
        if( sale_sep == 8 ):
            
            data['sale_sep'] +=1
            MONTHS[8]['sales'] = data['sale_sep']
        if( sale_oct == 9 ):
            
            data['sale_oct'] +=1
            MONTHS[9]['sales'] = data['sale_oct']
        if( sale_nov == 10 ):
            
            data['sale_nov'] +=1
            MONTHS[10]['sales'] = data['sale_nov']
        if( sale_dec == 11 ):
            
            data['sale_dec'] +=1
            MONTHS[11]['sales'] = data['sale_dec']

    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Sale Orders',
                'error_message' : None,
                'total_sales' : sum_total_sales,
                # 'dashboard': MONTHS,
                # 'start_months' : fix_months,
                'data' : {
                    'january' : sale_jan,
                    'feburary' : sale_feb,
                    'march' : sale_mar,
                    'april' : sale_apr,
                    'may' : sale_may,
                    'june' : sale_jun,
                    'july' : sale_july,
                    'august' : sale_aug,
                    'september' : sale_sep,
                    'octuber' : sale_oct,
                    'november' : sale_nov,
                    'december' : sale_dec,
                }
            }
        },
        status=status.HTTP_200_OK
    )
    