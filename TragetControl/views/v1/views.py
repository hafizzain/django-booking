from datetime import datetime
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from Employee.models import Employee, StaffGroup
from NStyle.Constants import StatusCodes
from rest_framework import status
from Business.models import Business, BusinessAddress
from Product.models import Brand
from Service.models import ServiceGroup
from TragetControl.models import RetailTarget, ServiceTarget, StaffTarget, StoreTarget, TierStoreTarget
from TragetControl.serializers import GETStoreTargetSerializers, RetailTargetSerializers, ServiceTargetSerializers, StaffTargetSerializers, StoreTargetSerializers
from Utility.models import ExceptionRecord


@api_view(['GET'])
@permission_classes([AllowAny])
def get_stafftarget(request):
    staff_target = StaffTarget.objects.all().order_by('-created_at')   
    serializer = StaffTargetSerializers(staff_target, many = True,context={'request' : request})
    
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Staff Target',
                'error_message' : None,
                'stafftarget' : serializer.data
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_stafftarget(request):
    user= request.user
    business = request.data.get('business', None)
    employee = request.data.get('employee', None)
    
    month = request.data.get('month', None)
    service_target = request.data.get('service_target', None)
    retail_target = request.data.get('retail_target', None)
    year = request.data.get('year', None)
    
    if not all([business,employee,month, service_target, retail_target]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                          'business',
                          'employee',
                          'month', 
                          'service_target',
                          'retail_target',
                            ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business_id=Business.objects.get(id=business)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response' : {
                    'message' : 'Business not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    try:
        employee_id=Employee.objects.get(id=employee)
    except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_EMPLOYEE_4025,
                    'response' : {
                    'message' : 'Employee not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
    staff_target = StaffTarget.objects.create(
        user = user,
        business = business_id,
        employee = employee_id,
        month = month,
        service_target = service_target,
        retail_target = retail_target,
       # year=year,
    )
    date_string =  f'{year} {month} 01'
    c_year = datetime.strptime(date_string, '%Y %B %d')
    staff_target.year = c_year
    staff_target.save()
    
    
    serializers= StaffTargetSerializers(staff_target, context={'request' : request})
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Staff Target Created Successfully!',
                    'error_message' : None,
                    'stafftarget' : serializers.data,
                }
            },
            status=status.HTTP_201_CREATED
        ) 

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_stafftarget(request):
    stafftarget_id = request.data.get('id', None)
    if stafftarget_id is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required!',
                    'fields' : [
                        'id'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        staff_target = StaffTarget.objects.get(id=stafftarget_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Staff Target ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    staff_target.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Staff Target delete successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_stafftarget(request):
    stafftarget_id = request.data.get('id', None)
    employee = request.data.get('employee', None)
    year = request.data.get('year', None)
    month = request.data.get('month', None)
    if stafftarget_id is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required!',
                    'fields' : [
                        'id'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        staff_target = StaffTarget.objects.get(id=stafftarget_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Staff Target ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        employee_id=Employee.objects.get(id=employee)
    except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_EMPLOYEE_4025,
                    'response' : {
                    'message' : 'Employee not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    staff_target.employee = employee_id
    
    try:
        request.data._mutable = True
    except:
        pass
    date_string =  f'{year} {month} 01'
    c_year = datetime.strptime(date_string, '%Y %B %d')
    request.data['year'] = c_year
    staff_target.year = c_year
    print(c_year)
    staff_target.save()
    
    serializer = StaffTargetSerializers(staff_target, data=request.data, partial=True, context={'request' : request})
    serializer.year = c_year
    if not serializer.is_valid():
        return Response(
                {
            'status' : False,
            'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
            'response' : {
                'message' : 'Staff Target Serializer Invalid',
                'error_message' : serializer.errors,
            }
        },
        status=status.HTTP_404_NOT_FOUND
        )
    serializer.save()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Update Satff Target Successfully',
                'error_message' : None,
                'stafftarget' : serializer.data
            }
        },
        status=status.HTTP_200_OK
        )
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def copy_stafftarget(request):
    user = request.user
    from_year = request.data.get('from_year', None)
    from_month = request.data.get('from_month', None)
    to_year = request.data.get('to_year', None)
    to_month = request.data.get('to_month', None)
    
    if not all([from_month, to_month]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'from_month',
                        'to_month',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        ) 
    staff_target = StaffTarget.objects.filter(month__icontains = from_month, year__icontains = from_year ) #years__icontains = from_year )
    for staff in staff_target:
        
        try:
            business_id=Business.objects.get(id=str(staff.business))
        except Exception as err:
            return Response(
                    {
                        'status' : False,
                        'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                        'response' : {
                        'message' : 'Business not found',
                        'error_message' : str(err),
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        try:
            employee_id=Employee.objects.get(id=str(staff.employee))
        except Exception as err:
                return Response(
                    {
                        'status' : False,
                        'status_code' : StatusCodes.INVALID_EMPLOYEE_4025,
                        'response' : {
                        'message' : 'Employee not found',
                        'error_message' : str(err),
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        staff_target = StaffTarget.objects.create(
                user = staff.user,
                business = business_id,
                employee = employee_id,
                month = to_month,
                service_target = staff.service_target,
                retail_target = staff.retail_target,
        )
        date_string =  f'{to_year} {to_month} 01'
        c_year = datetime.strptime(date_string, '%Y %B %d')
        staff_target.year = c_year
        staff_target.save()
    
    staff_target = StaffTarget.objects.all().order_by('-created_at')   
    serializer = StaffTargetSerializers(staff_target, many = True,context={'request' : request})
    
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'Target copied successfully',
                'error_message' : None,
                'stafftarget' : serializer.data
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_storetarget(request):
    store_target = StoreTarget.objects.all().order_by('-created_at').distinct()
    serializer = GETStoreTargetSerializers(store_target, many = True,context={'request' : request})
    
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Store Target',
                'error_message' : None,
                'storetarget' : serializer.data
            }
        },
        status=status.HTTP_200_OK
    ) 

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_storetarget(request):
    user= request.user
    business = request.data.get('business', None)
        
    location = request.data.get('location', None)
    store_tier = request.data.get('store_tier', None)
    
    if not all([business, location, ]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                          'business',
                          'location',
                            ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business_id = Business.objects.get(id = business)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response' : {
                    'message' : 'Business not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    try:
        location_id = BusinessAddress.objects.get( id = location)
    except:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : 'OBJECT_NOT_FOUND',
                'response' : {
                    'message' : 'Location Not found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    store_target = StoreTarget.objects.create(
        user = user,
        business = business_id ,
        location = location_id ,
        
    )
    
    if type(store_tier) == str:
        store_tier = store_tier.replace("'" , '"')
        store_tier = json.loads(store_tier)

    elif type(store_tier) == list:
        pass
    
    for tier in store_tier:
        month = tier.get('month', None)
        service_target = tier.get('service_target', None)
        retail_target = tier.get('retail_target', None)
        voucher_target = tier.get('voucher_target', None)
        membership_target = tier.get('membership_target', None)
        is_primary = tier.get('is_primary', None)
        year = tier.get('year', None)

        
        tier_store =  TierStoreTarget.objects.create(
            storetarget = store_target,
            month = month,
            service_target = service_target,
            retail_target = retail_target,
            voucher_target = voucher_target,
            membership_target = membership_target,
            
        )
        date_string =  f'{year} {month} 01'
        c_year = datetime.strptime(date_string, '%Y %B %d')
        tier_store.year = c_year
        tier_store.save()
        
        if is_primary == 'True':
            tier_store.is_primary = True
        else:
            tier_store.is_primary = False
        tier_store.save()
        
    serializer = StoreTargetSerializers(store_target, context={'request' : request})
    
    return Response(
        {
            'status' : True,
            'status_code' : '201',
            'response' : {
                'message' : 'Store Target Successfully!',
                'error_message' : None,
                'storetarget' : serializer.data
            }
        },
        status=status.HTTP_201_CREATED
    ) 


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_storetarget(request):
    stafftarget_id = request.data.get('id', None)
    if stafftarget_id is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required!',
                    'fields' : [
                        'id'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        staff_target = StoreTarget.objects.get(id=stafftarget_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Store Target ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    staff_target.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Store Target delete successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_storetarget(request):            
    store_target = request.data.get('id', None)
    
    location = request.data.get('location', None)
    store_tier = request.data.get('store_tier', None)
    
    if store_target is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required!',
                    'fields' : [
                        'id'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        ) 
    try:
        staff_target = StoreTarget.objects.get(id= store_target)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Store Target ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        location_id = BusinessAddress.objects.get( id = location)
        staff_target.location = location_id
        staff_target.save()
    except:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : 'OBJECT_NOT_FOUND',
                'response' : {
                    'message' : 'Location Not found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    if type(store_tier) == str:
        store_tier = store_tier.replace("'" , '"')
        store_tier = json.loads(store_tier)

    elif type(store_tier) == list:
        pass
    
    for tier in store_tier:
        id = tier.get('id', None)
        
        month = tier.get('month', None)
        service_target = tier.get('service_target', None)
        retail_target = tier.get('retail_target', None)
        voucher_target = tier.get('voucher_target', None)
        membership_target = tier.get('membership_target', None)
        is_primary = tier.get('is_primary', None)
        year = tier.get('year', None)
        
        if id is not None:
            try:
                tierstore = TierStoreTarget.objects.get(id = id)
                tierstore.month = month
                tierstore.service_target = service_target
                tierstore.retail_target = retail_target
                tierstore.voucher_target = voucher_target
                tierstore.membership_target = membership_target
                
                if is_primary == 'true':
                    tierstore.is_primary = True
                else:
                    tierstore.is_primary = False 
                    
                date_string =  f'{year} {month} 01'
                c_year = datetime.strptime(date_string, '%Y %B %d')
                tierstore.year = c_year
                tierstore.save()
                
                tierstore.save()
            except Exception as err:
                ExceptionRecord.objects.create(
                    text = f"Update tier store target {str(err)}"
                )
            
        else:
            tier =  TierStoreTarget.objects.create(
                storetarget = staff_target,
                month = month,
                service_target = service_target,
                retail_target = retail_target,
                voucher_target = voucher_target,
                membership_target = membership_target,
                
            )
            date_str =  f'{year} {month} 01'
            c_year = datetime.strptime(date_str, '%Y %B %d')
            tierstore.year = c_year
            tierstore.save()
            if is_primary == 'true':
                tier.is_primary = True
            else:
                tier.is_primary = False
            tier.save()
    
    serializer = StoreTargetSerializers(staff_target, context={'request' : request})
    
    return Response(
        {
            'status' : True,
            'status_code' : '200',
            'response' : {
                'message' : 'Store Target updated Successfully!',
                'error_message' : None,
                'storetarget' : serializer.data
            }
        },
        status=status.HTTP_200_OK
    )    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_servicetarget(request):
    user= request.user
    business = request.data.get('business', None)
    location = request.data.get('location', None)
    
    service_group = request.data.get('service_group', None)
    month = request.data.get('month', None)
    service_target = request.data.get('service_target', None)
    year = request.data.get('year', None)

    
    if not all([business, month, service_group, service_target]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                          'business',
                          'employee',
                          'month', 
                          'service_target',
                          'retail_target',
                            ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business_id=Business.objects.get(id=business)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response' : {
                    'message' : 'Business not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    try:
        location_id = BusinessAddress.objects.get( id = location)
    except:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : 'OBJECT_NOT_FOUND',
                'response' : {
                    'message' : 'Location Not found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        service_group_id = ServiceGroup.objects.get(id=service_group)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Service group ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    service_target = ServiceTarget.objects.create(
        user = user,
        business = business_id,
        location = location_id,
        month = month,
        service_target = service_target,
        service_group = service_group_id,
    )
    date_string =  f'{year} {month} 01'
    c_year = datetime.strptime(date_string, '%Y %B %d')
    service_target.year = c_year
    service_target.save()
    serializers= ServiceTargetSerializers(service_target, context={'request' : request})
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Service Target Created Successfully!',
                    'error_message' : None,
                    'servicetarget' : serializers.data,
                }
            },
            status=status.HTTP_201_CREATED
        ) 

@api_view(['GET'])
@permission_classes([AllowAny])
def get_servicetarget(request):
    service_target = ServiceTarget.objects.all().order_by('-created_at').distinct()
    serializer = ServiceTargetSerializers(service_target, many = True,context={'request' : request})
    
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Service Target',
                'error_message' : None,
                'servicetarget' : serializer.data
            }
        },
        status=status.HTTP_200_OK
    ) 
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_servicetarget(request):
    servicetarget_id = request.data.get('id', None)
    if servicetarget_id is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required!',
                    'fields' : [
                        'id'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        service_target = ServiceTarget.objects.get(id=servicetarget_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Service Target ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    service_target.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Service Target deleted successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_servicetarget(request):
    servicetarget_id = request.data.get('id', None)
    location = request.data.get('location', None)
    
    service_group = request.data.get('service_group', None)
    year = request.data.get('year', None)
    month = request.data.get('month', None)
    
    if servicetarget_id is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required!',
                    'fields' : [
                        'id'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        service_target = ServiceTarget.objects.get(id=servicetarget_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Service Target ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    try:
        location_id = BusinessAddress.objects.get( id = location)
        service_target.location = location_id
        service_target.save()
        
    except:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : 'OBJECT_NOT_FOUND',
                'response' : {
                    'message' : 'Location Not found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        service_group_id = ServiceGroup.objects.get(id=service_group)
        service_target.service_group = service_group_id
        service_target.save()
        
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Service group ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    try:
        request.data._mutable = True
    except:
        pass
    date_string =  f'{year} {month} 01'
    c_year = datetime.strptime(date_string, '%Y %B %d')
    request.data['year'] = c_year
    service_target.year = c_year
    service_target.save()
    
    serializers= ServiceTargetSerializers(service_target,data=request.data, partial=True, context={'request' : request} )
    if not serializers.is_valid():
        return Response(
                {
            'status' : False,
            'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
            'response' : {
                'message' : 'Service Target Serializer Invalid',
                'error_message' : 'Error on update Service Target',
            }
        },
        status=status.HTTP_404_NOT_FOUND
        )
    serializers.save()
    return Response(
        {
            'status' : True,
            'status_code' : '200',
            'response' : {
                'message' : 'Service Target updated Successfully!',
                'error_message' : None,
                'servicetarget' : serializers.data
            }
        },
        status=status.HTTP_200_OK
    )    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def copy_servicetarget(request):
    user = request.user
    from_year = request.data.get('from_year', None)
    from_month = request.data.get('from_month', None)
    to_year = request.data.get('to_year', None)
    to_month = request.data.get('to_month', None)
    
    
    if not all([from_month, to_month]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'from_month',
                        'to_month',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        ) 
    service_target_id = ServiceTarget.objects.filter(month__icontains = from_month, year__icontains = from_year )
    for service in service_target_id:
        
        try:
            business_id=Business.objects.get(id=str(service.business))
        except Exception as err:
            return Response(
                    {
                        'status' : False,
                        'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                        'response' : {
                        'message' : 'Business not found',
                        'error_message' : str(err),
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        try:
            location_id = BusinessAddress.objects.get( id = service.location.id)
        except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : 404,
                    'status_code_text' : 'OBJECT_NOT_FOUND',
                    'response' : {
                        'message' : 'Location Not found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            service_group_id = ServiceGroup.objects.get(id= service.service_group.id)
        except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : 404,
                    'status_code_text' : '404',
                    'response' : {
                        'message' : 'Invalid Service group ID!',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        servicetarget = ServiceTarget.objects.create(
            user = user,
            business = business_id,
            location = location_id,
            service_group = service_group_id,
            month = to_month,
            service_target = service.service_target,
            
        )
    
        date_string =  f'{to_year} {to_month} 01'
        c_year = datetime.strptime(date_string, '%Y %B %d')
        servicetarget.year = c_year
        servicetarget.save()
    
    service_target = ServiceTarget.objects.all().order_by('-created_at').distinct()
    serializer = ServiceTargetSerializers(service_target, many = True,context={'request' : request})
    
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'Target copied successfully',
                'error_message' : None,
                'servicetarget' : serializer.data
            }
        },
        status=status.HTTP_200_OK
    ) 

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_retailtarget(request):
    user= request.user
    business = request.data.get('business', None)
    location = request.data.get('location', None)
    
    brand = request.data.get('brand', None)
    month = request.data.get('month', None)
    brand_target = request.data.get('brand_target', None)
    year = request.data.get('year', None)

    
    if not all([business, month, brand, brand_target]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                          'business',
                          'employee',
                          'month', 
                          'retail_target',
                            ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business_id=Business.objects.get(id=business)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response' : {
                    'message' : 'Business not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    try:
        location_id = BusinessAddress.objects.get( id = location)
    except:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : 'OBJECT_NOT_FOUND',
                'response' : {
                    'message' : 'Location Not found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    try:
        brand_id = Brand.objects.get( id = brand)
    except:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : 'OBJECT_NOT_FOUND',
                'response' : {
                    'message' : 'Brand Not found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    retail = RetailTarget.objects.create(
        user = user,
        business = business_id,
        location = location_id,
        brand = brand_id,
        month =month,
        brand_target = brand_target,
    )
    date_string =  f'{year} {month} 01'
    c_year = datetime.strptime(date_string, '%Y %B %d')
    retail.year = c_year
    retail.save()
    
    serializers= RetailTargetSerializers(retail, context={'request' : request})
    
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Retail Target Created Successfully!',
                    'error_message' : None,
                    'retailtarget' : serializers.data,
                }
            },
            status=status.HTTP_201_CREATED
        ) 
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_retailtarget(request):
    retail_target = RetailTarget.objects.all().order_by('-created_at').distinct()
    serializer = RetailTargetSerializers(retail_target, many = True,context={'request' : request})
    
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Service Target',
                'error_message' : None,
                'retailtarget' : serializer.data
            }
        },
        status=status.HTTP_200_OK
    ) 

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_retailtarget(request):
    retailtarget_id = request.data.get('id', None)
    if retailtarget_id is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required!',
                    'fields' : [
                        'id'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        retail_target = RetailTarget.objects.get(id=retailtarget_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Retail Target ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    retail_target.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Retail Target delete successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_retailtarget(request):
    retailtarget_id = request.data.get('id', None)
    brand = request.data.get('brand', None)
    year = request.data.get('year', None)
    month = request.data.get('month', None)
    
    if retailtarget_id is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required!',
                    'fields' : [
                        'id'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        retail_target = RetailTarget.objects.get(id=retailtarget_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Retail Target ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    try:
        brand_id = Brand.objects.get( id = brand)
        retail_target.brand = brand_id
        retail_target.save()
    except:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : 'OBJECT_NOT_FOUND',
                'response' : {
                    'message' : 'Brand Not found',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    try:
        request.data._mutable = True
    except:
        pass
    date_string =  f'{year} {month} 01'
    c_year = datetime.strptime(date_string, '%Y %B %d')
    request.data['year'] = c_year
    retail_target.year = c_year
    retail_target.save()
    
    serializer = RetailTargetSerializers(retail_target, data=request.data, partial=True, context={'request' : request})
    if not serializer.is_valid():
        return Response(
                {
            'status' : False,
            'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
            'response' : {
                'message' : 'Retail Target Serializer Invalid',
                'error_message' : 'Error on update Retail Target',
            }
        },
        status=status.HTTP_404_NOT_FOUND
        )
    serializer.save()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Update Retail Target Successfully',
                'error_message' : None,
                'retailtarget' : serializer.data
            }
        },
        status=status.HTTP_200_OK
        )
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def copy_retailtarget(request):
    user = request.user
    from_year = request.data.get('from_year', None)
    from_month = request.data.get('from_month', None)
    to_year = request.data.get('to_year', None)
    to_month = request.data.get('to_month', None)
    
    if not all([from_month, to_month]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'from_month',
                        'to_month',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        ) 
    retail_target_id = RetailTarget.objects.filter(month__icontains = from_month, year__icontains = from_year )
    for retail in retail_target_id:
        try:
            business_id=Business.objects.get(id=str(retail.business))
        except Exception as err:
            return Response(
                    {
                        'status' : False,
                        'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                        'response' : {
                        'message' : 'Business not found',
                        'error_message' : str(err),
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        try:
            location_id = BusinessAddress.objects.get( id = str(retail.location))
        except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : 404,
                    'status_code_text' : 'OBJECT_NOT_FOUND',
                    'response' : {
                        'message' : 'Location Not found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        try:
            brand_id = Brand.objects.get( id = str(retail.brand))
        except:
            return Response(
                {
                    'status' : False,
                    'status_code' : 404,
                    'status_code_text' : 'OBJECT_NOT_FOUND',
                    'response' : {
                        'message' : 'Brand Not found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        retail = RetailTarget.objects.create(
            user = user,
            business = business_id,
            location = location_id,
            brand = brand_id,
            month =to_month,
            brand_target = retail.brand_target,
        )
    
        date_string =  f'{to_year} {to_month} 01'
        c_year = datetime.strptime(date_string, '%Y %B %d')
        retail.year = c_year
        retail.save()
        
    retail_target = RetailTarget.objects.all().order_by('-created_at').distinct()
    serializer = RetailTargetSerializers(retail_target, many = True,context={'request' : request})
    
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'Target copied successfully',
                'error_message' : None,
                'retailtarget' : serializer.data
            }
        },
        status=status.HTTP_200_OK
    ) 