import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from Employee.models import Employee
from NStyle.Constants import StatusCodes
from rest_framework import status
from Business.models import Business, BusinessAddress
from TragetControl.models import StaffTarget, StoreTarget, TierStoreTarget
from TragetControl.serializers import StaffTargetSerializers, StoreTargetSerializers


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
    )
    
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
    
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_storetarget(request):
    store_target = StoreTarget.objects.all().order_by('-created_at')   
    serializer = StoreTargetSerializers(store_target, many = True,context={'request' : request})
    
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
        
        tier_store =  TierStoreTarget.objects.create(
            storetarget = store_target,
            month = month,
            service_target = service_target,
            retail_target = retail_target,
            voucher_target = voucher_target,
            membership_target = membership_target,
            
        )
        if is_primary is not None:
            tier_store.is_primary = True
        else:
            tier_store.is_primary = False
        tier_store.save()
        
    serializer = StoreTargetSerializers(store_target, context={'request' : request})
    
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
            
        
        