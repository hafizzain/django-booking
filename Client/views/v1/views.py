from datetime import date, datetime
from threading import Thread

from Order.models import VoucherOrder, Vouchers, MemberShipOrder, Membership

from Client.Constants.Add_Employe import add_client
from Employee.Constants.Add_Employe import add_employee
from Promotions.models import ServiceDurationForSpecificTime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from Service.models import Service
from Business.models import Business, BusinessAddress
from Product.models import Product
from Utility.models import Country, Currency, ExceptionRecord, Language, State, City
from Client.models import Client, ClientGroup, ClientPackageValidation, ClientPromotions, CurrencyPriceMembership, DiscountMembership, LoyaltyPoints, Subscription , Rewards , Promotion , Membership , Vouchers, ClientLoyaltyPoint, LoyaltyPointLogs,VoucherCurrencyPrice
from Client.serializers import ClientSerializer, ClientGroupSerializer, LoyaltyPointsSerializer, SubscriptionSerializer , RewardSerializer , PromotionSerializer , MembershipSerializer , VoucherSerializer, ClientLoyaltyPointSerializer, CustomerLoyaltyPointsLogsSerializer, CustomerDetailedLoyaltyPointsLogsSerializer, ClientVouchersSerializer, ClientMembershipsSerializer
from Utility.models import NstyleFile

import json
from django.core import serializers
from NStyle.Constants import StatusCodes
from django.core.paginator import Paginator

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_client(request):
    client_csv = request.data.get('file', None)
    user= request.user
    business_id = request.data.get('business', None)

    file = NstyleFile.objects.create(
        file = client_csv
    )
    tenant_name = str(request.tenant_name).split('.')[0]
    tenant_name = tenant_name.split('-')
    tenant_name = [word[0].upper() for word in tenant_name if word] 
    
    count = Client.objects.all().count()
    count += 1
   
    return_loop = True
    while return_loop:
        if 0 < count <= 9 : 
            count = f'000{count}'
        elif 9 < count <= 99 :
            count = f'00{count}'
        elif 99 < count <= 999:
            count = f'0{count}'
        new_id =f'{tenant_name}-CLI-{count}'
        
        try:
            Client.objects.get(employee_id=new_id)
            count += 1
        except:
            return_loop = False
            break
    
    client_unique_id = f'{" ".join(tenant_name)}-{new_id}'
    
    with open( file.file.path , 'r', encoding='utf-8') as imp_file:
        for index, row in enumerate(imp_file):
            if index == 0:
                continue
            row = row.split(',')
            row = row
            
            if len(row) < 7:
                continue
            
            name= row[0].strip('"')
            email = row[1].strip('"')
            client_id = row[2].strip('"')
            mobile_number = row[3].strip('"')
            gender = row[4].strip('"')
            address = row[5].strip('"')
            active = row[6].replace('\n', '').strip('"') 

            if active == 'Active':
                active = True
            else:
                active = False
            
            try:
                business=Business.objects.get(id=business_id)
            except Exception as err:
                return Response(
                    {
                'status' : True,
                'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text' :'BUSINESS_NOT_FOUND_4015' ,
                'response' : {
                    'message' : 'Business not found!',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
            Client.objects.create(
                user = user,
                business= business,
                full_name = name,
                client_id = client_unique_id,
                email = email,
                gender = gender,
                mobile_number = mobile_number,
                address = address,
                is_active = active
            )
    file.delete()
    return Response({'Status' : 'Success'})

@api_view(['GET'])
@permission_classes([AllowAny])
def get_single_client(request):
    client_id = request.GET.get('client_id', None)
    if not all([client_id]):
        return Response(
        {
            'status' : False,
            'status_code' : StatusCodes.MISSING_FIELDS_4001,
            'status_code_text' : 'MISSING_FIELDS_4001',
            'response' : {
                'message' : 'Invalid Data!',
                'error_message' : 'Client id are required',
                'fields' : [
                    'client_id',
                ]
            }
        },
        status=status.HTTP_400_BAD_REQUEST
        )
        
    try:
        client = Client.objects.get(id=client_id, is_deleted=False, is_blocked=False)
    except Exception as err:
        return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_CLIENT_4032,
                    'status_code_text' : 'INVALID_CLIENT_4032',
                    'response' : {
                        'message' : 'Client Not Found',
                        'error_message' : str(err),
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
    seralized = ClientSerializer(client, context={'request' : request})
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'Single client',
                'error_message' : None,
                'client' : seralized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_client(request):
    all_client=Client.objects.filter(is_deleted=False, is_blocked=False).order_by('-created_at').distinct()
    all_client_count=all_client.count()

    page_count = all_client_count / 20
    if page_count > int(page_count):
        page_count = int(page_count) + 1

    paginator = Paginator(all_client, 20)
    page_number = request.GET.get("page") 
    all_client = paginator.get_page(page_number)
    serialized = ClientSerializer(all_client, many=True,  context={'request' : request})
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Client',
                'count':all_client_count,
                'pages':page_count,
                'per_page_result':20,
                'error_message' : None,
                'client' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_id(request):
    tenant_name = request.tenant_name
    tenant_name = tenant_name.split('-')
    tenant_name = [word[0] for word in tenant_name]
    print(tenant_name)
    ''.join(tenant_name)
    count = Client.objects.all().count()
    count += 1
   
    return_loop = True
    while return_loop:
        if 0 < count <= 9 : 
            count = f'000{count}'
        elif 9 < count <= 99 :
            count = f'00{count}'
        elif 99 < count <= 999:
            count = f'0{count}'
        new_id =f'{tenant_name}-CLI-{count}'
        
        try:
            Client.objects.get(employee_id=new_id)
            count += 1
        except:
            return_loop = False
            break
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'Generated ID',
                'error_message' : None,
                'id' : new_id
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_client(request):
    user = request.user  
    business_id= request.data.get('business', None) 
    
    full_name= request.data.get('full_name', None)
    image = request.data.get('image', None)
    client_id= request.data.get('client_id' ,None)
    
    email= request.data.get('email', None)
    mobile_number= request.data.get('mobile_number', None)    
    
    dob= request.data.get('dob', None)
    gender = request.data.get('gender' , 'Male')
    
    about_us = request.data.get('about_us' , 'Community')
    marketing = request.data.get('marketing' , 'opt_in')
    customer_note = request.data.get('customer_note' , '')
    
    postal_code= request.data.get('postal_code' , None)
    address= request.data.get('address' , None)
    card_number= request.data.get('card_number' , None)
    is_active = True if request.data.get('is_active', None) is not None else False
    
    city= request.data.get('city', None)
    state= request.data.get('state', None)
    country= request.data.get('country', None)
    languages= request.data.get('language', None)
    errors = []
    
    if not all([business_id, client_id, full_name ,gender  , languages]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'All fields are required.',
                    'fields' : [
                        'business_id',
                        'client_id',
                        'full_name',
                        'gender', 
                        'languages',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        business=Business.objects.get(id=business_id)
    except Exception as err:
        return Response(
            {
                'status' : True,
                'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                'status_code_text' :'BUSINESS_NOT_FOUND_4015' ,
                'response' : {
                    'message' : 'Business not found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        if country is not None:
            country = Country.objects.get(id=country)
        if state is not None:
            state= State.objects.get(id=state)
        if city is not None:
            city = City.objects.get(id=city)
    except Exception as err:
        return Response(
            {
                'status' : True,
                'status_code' : StatusCodes.INVALID_COUNTRY_STATE_CITY_4021,
                'status_code_text' :'INVALID_COUNTRY_STATE_CITY_4021' ,
                'response' : {
                    'message' : 'Invalid Country, State, City not found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    

    
    if languages is not None:
        language_id = Language.objects.get(id=languages)
    else:
        return Response(
            {
                'status' : True,
                'status_code_text' :'languages_NOT_FOUND' ,
                'response' : {
                    'message' : 'Languages not found!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if email is not None:
        try:
            client = Client.objects.get(email__iexact = email)
            return Response(
                        {
                            'status' : False,
                            'status_code' : 404,
                            'status_code_text' : '404',
                            'response' : {
                                'message' : f'Client Already exist with this {email}!',
                                'error_message' : None,
                            }
                        },
                status=status.HTTP_404_NOT_FOUND
                    )
        except Exception as err:
            pass

    if  mobile_number is not None:
        try:
            employe_mobile = Client.objects.get(mobile_number = mobile_number)
            #if employe_mobile:
            return Response(
                        {
                            'status' : False,
                            'status_code' : 404,
                            'status_code_text' : '404',
                            'response' : {
                                'message' : f'Client Already exist with this {mobile_number}!',
                                'error_message' : None, 
                            }
                        },
            status=status.HTTP_404_NOT_FOUND
                    )
        except Exception as err:
            ExceptionRecord.objects.create(
                text = f'error on create client {str(err)}'
            )
            errors.append(f'clients errors {str(err)} mobile_number {mobile_number}')
    
    client=Client.objects.create(
        user=user,
        business=business,
        full_name = full_name,
        image= image,
        client_id=client_id,
        mobile_number=mobile_number,
        dob=dob,
        gender= gender,
        country= country,
        state = state,
        city = city,
        postal_code= postal_code,
        card_number= card_number,
        is_active = is_active,

        #New requirement
        customer_note = customer_note, 
        language = language_id,
        about_us =  about_us,
    )

    if address is not None:
        client.address = address

    if email is not None:
        client.email = email

    client.save()

    serialized= ClientSerializer(client, context={'request' : request})
    template = 'Client'
    try:
        thrd = Thread(target=add_client, args=[full_name, email , template, business.business_name,])
        thrd.start()
    except Exception as err:
        pass
    return Response(
        {
            'status' : True,
            'status_code' : 201,
            'response' : {
                'message' : 'Client Added!',
                'error_message' : errors,
                'client' : serialized.data
            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_client(request): 
    # sourcery skip: avoid-builtin-shadow
        id = request.data.get('id', None)
        if id is None:
            return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'Client ID is required',
                    'fields' : [
                        'id',
                    ]
                }
            },
             status=status.HTTP_400_BAD_REQUEST
           )
        try:
            client = Client.objects.get(id=id)
        except Exception as err:
              return Response(
             {
                    'status' : False,
                    'status_code' : StatusCodes.INVALID_CLIENT_4032,
                    'status_code_text' : 'INVALID_CLIENT_4032',
                    'response' : {
                        'message' : 'Client Not Found',
                        'error_message' : str(err),
                    }
                },
                   status=status.HTTP_404_NOT_FOUND
              )
        image=request.data.get('image',None)
        phone_number=request.data.get('mobile_number',None)
        if phone_number is not None:
            client.mobile_number = phone_number
        else :
            client.mobile_number = None
        
        client.is_active = True  if request.data.get('image',None) is not None else False

        if image is not None:
            client.image=image
        
        postal_code = request.data.get('postal_code' , None)
        if postal_code is None:
            client.postal_code = ''

        client.save()
        
        serialized= ClientSerializer(client, data=request.data, partial=True, context={'request' : request})
        if serialized.is_valid():
            serialized.save()
            
            return Response(
            {
                'status' : True,
                'status_code' : 200,
                'response' : {
                    'message' : 'Client Updated Successfully!',
                    'error_message' : None,
                    'client' : serialized.data
                }
            },
            status=status.HTTP_200_OK
           )
        else:
              return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.INVALID_CLIENT_4032,
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : str(serialized.errors),
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        
        
        
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_client(request):
    client_id = request.data.get('client_id', None)
    if client_id is None:
     return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required.',
                    'fields' : [
                        'client_id'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
          
    try:
        client = Client.objects.get(id=client_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Client ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    client_staff = ClientGroup.objects.filter(client = client)
    for cl_grp in client_staff:
        cl_grp.client.remove(client)
        cl_grp.save()
            
    #client.is_deleted = True
    client.delete()
    client.save()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Client deleted successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )
    
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_client_group(request):
    all_client_group= ClientGroup.objects.all().order_by('-created_at')
    all_client_group_count= all_client_group.count()

    page_count = all_client_group_count / 20
    if page_count > int(page_count):
        page_count = int(page_count) + 1

    paginator = Paginator(all_client_group, 20)
    page_number = request.GET.get("page") 
    all_client_group = paginator.get_page(page_number)

    serialized = ClientGroupSerializer(all_client_group, many=True,  context={'request' : request})
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Client Group',
                'count':all_client_group_count,
                'pages':page_count,
                'per_page_result':20,
                'error_message' : None,
                'clientsgroup' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_client_group(request):
    user = request.user     
    business_id= request.data.get('business', None)
        
    email= request.data.get('email', None)    
    name = request.data.get('name', None)
    client = request.data.get('client', None)
        
    is_active= request.data.get('is_active' , True)
    
    if not all([ business_id, name, client ]):
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
                          'client',
                          'email', 
                          'name',
                            ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
             business=Business.objects.get(id=business_id)
    except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response' : {
                    'message' : 'Business not found',
                    'error_message' : str(err),
                }
                }
            )
    if is_active is not None:
           #     is_active= json.loads(is_active)
        is_active = True
    else: 
        is_active = False
    client_group=ClientGroup.objects.create(
        user=user,
        business=business,
        name= name,
        email= email,
        is_active= is_active,
    )
    client_error = []
    if type(client) == str:
        client = json.loads(client)

    elif type(client) == list:
            pass
        
    for usr in client:
        try:
            employe = Client.objects.get(id=usr)  
            client_group.client.add(employe)
        except Exception as err:
            client_error.append(str(err))
                
    client_group.save()
    serialized=ClientGroupSerializer(client_group, context={'request' : request})
       
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Client Group Create!',
                    'error_message' : None,
                    'ClientGroup' : serialized.data,
                    'client_errors' : client_error,
                }
            },
            status=status.HTTP_201_CREATED
        ) 
    

   
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_client_group(request):
    client_group_id = request.data.get('client_group_id', None)
    if client_group_id is None: 
        return Response(
        {
            'status' : False,
            'status_code' : StatusCodes.MISSING_FIELDS_4001,
            'status_code_text' : 'MISSING_FIELDS_4001',
            'response' : {
                'message' : 'Invalid Data!',
                'error_message' : 'Client Group ID are required.',
                'fields' : [
                    'client_group_id'                         
                ]
            }
        },
        status=status.HTTP_400_BAD_REQUEST
        )
    try:
        client_group = ClientGroup.objects.get(id=client_group_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.INVIALID_CLIENT_GROUP_4033,
                'status_code_text' : 'INVIALID_CLIENT_GROUP_4033',
                'response' : {
                    'message' : 'Client Group Not Found',
                    'error_message' : str(err),
                }
            },
                status=status.HTTP_404_NOT_FOUND
        )
    client_error = []
    client=request.data.get('client', None)
    print(type(client))
    if client is not None:
        if type(client) == str:
            client = json.loads(client)
        elif type(client) == list:
            pass
        client_group.client.clear()
        for usr in client:
            try:
               employe = Client.objects.get(id=usr)  
               #print(employe)
               client_group.client.add(employe)
               
            except Exception as err:
                client_error.append(str(err))
                
        client_group.save()
        
    
    try:
        request.data._mutable = True
        del request.data['client']
    except Exception as err:
        pass
    
    serializer = ClientGroupSerializer(client_group,context={'request' : request} , data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(
                {
            'status' : False,
            'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
            'response' : {
                'message' : 'Client Group Serializer Invalid',
                #'error_message' : 'Invalid Data!' ,
                'error_message' : str(serializer.errors),
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
            'message' : 'Update Client Group Successfully',
            'error_message' : None,
            'ClientGroupUpdate' : serializer.data
            }
        },
    status=status.HTTP_200_OK
    )
    
    

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_client_group(request):
    client_group_id = request.data.get('client_group_id', None)
    if client_group_id is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required.',
                    'fields' : [
                        'client_group_id'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
          
    try:
        client_group = ClientGroup.objects.get(id=client_group_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Employee ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    client_group.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Client Group deleted successful',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_subscription(request):
    user= request.user
    business= request.data.get('business', None)
    
    subscription_type = request.data.get('subscription_type',None)
    name= request.data.get('name', None)
    product = request.data.get('product', None)
    service_id= request.data.get('service', None)
    days= request.data.get('days',None)
    select_amount = request.data.get('select_amount', None)
    services_count= request.data.get('services', 0)
    products_count= request.data.get('products', 0)
    price= request.data.get('price', None)
    
    is_active= request.data.get('is_active', None)
    
    if not all([business, name, days ,select_amount , price]): #or (subscription_type is not None and subscription_type == 'Product' and product is None) or (subscription_type is not None and subscription_type == 'Service'  and service_id is None):
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
                          'name',
                          'product',
                          'days', 
                          'select_amount', 
                          'services_count', 
                          'price', 
                        ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
             business=Business.objects.get(id=business)
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
            
    
    if is_active is not None:
        is_active = True
    else: 
        is_active = False
            
    client_subscription= Subscription.objects.create(
        user =user,
        business=business, 
        name= name,
        days=days,
        select_amount=select_amount,
        price=price,
        subscription_type = subscription_type,
        is_active= is_active,

    )
    # if subscription_type == 'Product':
    #     try:
    #         product=Product.objects.get(id=product)
    #     except Exception as err:
    #         return Response(
    #             {
    #                 'status' : False,
    #                 'status_code' : StatusCodes.PRODUCT_NOT_FOUND_4037,
    #                 'response' : {
    #                 'message' : 'Product not found',
    #                 'error_message' : str(err),
    #                 }
    #             },
    #             status=status.HTTP_400_BAD_REQUEST
    #         ) 
    #     client_subscription.product = product
    #     client_subscription.products_count = products_count

    # else:
    #     try:
    #         service=Service.objects.get(id=service_id)
    #     except Exception as err:
    #         return Response(
    #             {
    #                 'status' : False,
    #                 'status_code' : StatusCodes.SERVICE_NOT_FOUND_4035,
    #                 'response' : {
    #                 'message' : 'Service not found',
    #                 'error_message' : str(err),
    #                 }
    #             },
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
            
    #     client_subscription.service = service
    #     client_subscription.services_count = services_count

    
    # client_subscription.save()
        
    
    serialized = SubscriptionSerializer(client_subscription, context={'request' : request})
       
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'New Subscription Created!',
                    'error_message' : None,
                    'subscription' : serialized.data,
                }
            },
            status=status.HTTP_201_CREATED
        ) 
 
            
            
@api_view(['GET'])
@permission_classes([AllowAny])
def get_subscription(request):
    all_subscription= Subscription.objects.all().order_by('-created_at')
    serialized = SubscriptionSerializer(all_subscription, many=True)
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Subscription!',
                'error_message' : None,
                'subscription' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_subscription(request):
    subsciption_id = request.data.get('subsciption_id', None)
    if subsciption_id is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required.',
                    'fields' : [
                        'subsciption_id'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
          
    try:
        subsciption = Subscription.objects.get(id=subsciption_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Subscription ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    subsciption.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Subscription deleted successful',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )
    

    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_subscription(request):
    subscription_id = request.data.get('id', None)
    if subscription_id is None: 
        return Response(
        {
            'status' : False,
            'status_code' : StatusCodes.MISSING_FIELDS_4001,
            'status_code_text' : 'MISSING_FIELDS_4001',
            'response' : {
                'message' : 'Invalid Data!',
                'error_message' : 'Subscription ID are required.',
                'fields' : [
                    'id'                         
                ]
            }
        },
        status=status.HTTP_400_BAD_REQUEST
        )
    try:
        subscription = Subscription.objects.get(id=subscription_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.INVALID_SUBSCRIPTION_ID_4031,
                'status_code_text' : 'INVALID_SUBSCRIPTION_ID_4031',
                'response' : {
                    'message' : 'Subscription Not Found',
                    'error_message' : str(err),
                }
            },
                status=status.HTTP_404_NOT_FOUND
        )
    serializer = SubscriptionSerializer(subscription, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(
                {
            'status' : False,
            'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
            'response' : {
                'message' : 'Subscription Serializer Invalid',
                'error_message' : str(serializer.errors),
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
                'message' : 'Update Subscription Successfully',
                'error_message' : None,
                'subscription' : serializer.data
            }
        },
        status=status.HTTP_200_OK
        )
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_rewards(request):
    user = request.user
    business = request.data.get('business', None)
    
    name = request.data.get('name', None)
    service_id = request.data.get('service', None)
    product_id = request.data.get('product', None)
    
    reward_type= request.data.get('reward_type', None)
    reward_value = request.data.get('reward_value', None)
    reward_point = request.data.get('reward_point', None)
    
    total_points = request.data.get('total_points', None)
    discount = request.data.get('discount', None)
    
    if not all([business , name , reward_value , reward_type , reward_point , total_points, discount ]):
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
                          'name',
                          'reward_type',
                          'Service/Product' ,
                          'reward_point', 
                          'total_points',
                          'discount'
                            ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business=Business.objects.get(id=business)
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
  
            
    rewards = Rewards(
        user = user,
        business=business, 
        name=name,
        reward_value=reward_value,
        reward_point=reward_point,
        total_points = total_points,
        discount = discount,
        reward_type = reward_type,
    )
    
    if reward_type == 'Product':
        try:
            product=Product.objects.get(id=product_id)
        except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.PRODUCT_NOT_FOUND_4037,
                    'response' : {
                    'message' : 'Product not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        rewards.product = product
        rewards.save()
            
    elif reward_type == 'Service':
        try:
            service=Service.objects.get(id=service_id)
        except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.SERVICE_NOT_FOUND_4035,
                    'response' : {
                    'message' : 'Service not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        rewards.service = service
        rewards.save()
    else :
        return Response(
                {
                    'status' : False,
                    'response' : {
                    'message' : 'Invalid Reward Type',
                    'error_message' : 'Reward Type',
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
    serialized = RewardSerializer(rewards)
       
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Rewards Create!',
                    'error_message' : None,
                    'rewards' : serialized.data,
                }
            },
            status=status.HTTP_201_CREATED
        ) 
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_rewards(request):
    all_rewards= Rewards.objects.all().order_by('-created_at')
    serialized = RewardSerializer(all_rewards, many=True)
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Rewards',
                'error_message' : None,
                'rewards' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_rewards(request):
    rewards_id = request.data.get('rewards_id', None)
    if rewards_id is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required!',
                    'fields' : [
                        'rewards_id'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
          
    try:
        rewards = Rewards.objects.get(id=rewards_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Rewards ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    rewards.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Rewards deleted successful',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )
   
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_rewards(request):
    rewards_id = request.data.get('id', None)
    reward_type = request.data.get('reward_type', None)
    product= request.data.get('product', None)
    service = request.data.get('service',None)
    
    if rewards_id is None: 
        return Response(
        {
            'status' : False,
            'status_code' : StatusCodes.MISSING_FIELDS_4001,
            'status_code_text' : 'MISSING_FIELDS_4001',
            'response' : {
                'message' : 'Invalid Data!',
                'error_message' : 'Subscription ID are required.',
                'fields' : [
                    'id'                         
                ]
            }
        },
        status=status.HTTP_400_BAD_REQUEST
        )
    try:
        reward = Rewards.objects.get(id=rewards_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                #'status_code' : StatusCodes.INVALID_SUBSCRIPTION_ID_4031,
                'status_code_text' : 'INVALID_REWARD_ID',
                'response' : {
                    'message' : 'Reward Not Found',
                    'error_message' : str(err),
                }
            },
                status=status.HTTP_404_NOT_FOUND
        )
    if reward_type == 'Product':
        try:
            product_id=Product.objects.get(id=product)
        except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.PRODUCT_NOT_FOUND_4037,
                    'response' : {
                    'message' : 'Product not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        reward.product = product_id
        reward.service = None
        reward.save()
    elif reward_type == 'Service':
        try:
            service_id=Service.objects.get(id=service)
        except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.SERVICE_NOT_FOUND_4035,
                    'response' : {
                    'message' : 'Service not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        reward.service= service_id
        reward.product = None
        reward.save()    
        
    serializer = RewardSerializer(reward, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(
                {
            'status' : False,
            'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
            'response' : {
                'message' : 'Reward Serializer Invalid',
                'error_message' : str(err),
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
                'message' : 'Update Rewward Successfully',
                'error_message' : None,
                'reward' : serializer.data
            }
        },
        status=status.HTTP_200_OK
        )
    
   
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_promotion(request):
    user = request.user
    
    business = request.data.get('business', None)
    promotion_type = request.data.get('promotion_type', None)
    
    name = request.data.get('name', None)
    purchases = request.data.get('no_of_purchases', None)
    
    service  = request.data.get('service', None)
    product_id = request.data.get('product', None)
    
    discount = request.data.get('discount', None)
    valid_till = request.data.get('valid_till', None)
    
    if not all([business, name,promotion_type,purchases, valid_till, discount]):
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
                          'name',
                          'promotion_type',
                          'purchases',
                          'discount_product',
                          'discount_service', 
                          'discount', 
                          'valid_till', 

                            ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business=Business.objects.get(id=business)
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
    promotion = Promotion(
        user = user,
        business = business,
        promotion_type = promotion_type,
        purchases = purchases,
        discount = discount,
        valid_til = valid_till,
        name = name,
    )
    if promotion_type == 'Product':
        try:
            product=Product.objects.get(id=product_id)
        except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.PRODUCT_NOT_FOUND_4037,
                    'response' : {
                    'message' : 'Product not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        promotion.product = product
        promotion.save()
    else:
        try:
            service=Service.objects.get(id=service)
        except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.SERVICE_NOT_FOUND_4035,
                    'response' : {
                    'message' : 'Service not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        promotion.service= service
        promotion.save()    
    
    serialized = PromotionSerializer(promotion)
       
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Promotion Created Successfully!',
                    'error_message' : None,
                    'promotion' : serialized.data,
                }
            },
            status=status.HTTP_201_CREATED
        ) 

@api_view(['GET'])
@permission_classes([AllowAny])
def get_promotion(request):
    all_promotion= Promotion.objects.all().order_by('-created_at')
    serialized = PromotionSerializer(all_promotion, many=True)
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Promotion',
                'error_message' : None,
                'promotion' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_promotion(request):
    promotion_id = request.data.get('promotion_id', None)
    if promotion_id is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required!',
                    'fields' : [
                        'promotion_id'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
          
    try:
       promotion = Promotion.objects.get(id=promotion_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Promotion ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    promotion.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Promotion deleted successful',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )
    
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_promotion(request):
    promotion_id = request.data.get('id', None)
    promotion_type = request.data.get('promotion_type', None)
    product = request.data.get('product', None)
    service = request.data.get('service', None)
    if promotion_id is None: 
        return Response(
        {
            'status' : False,
            'status_code' : StatusCodes.MISSING_FIELDS_4001,
            'status_code_text' : 'MISSING_FIELDS_4001',
            'response' : {
                'message' : 'Invalid Data!',
                'error_message' : 'Promotion ID are required.',
                'fields' : [
                    'id'                         
                ]
            }
        },
        status=status.HTTP_400_BAD_REQUEST
        )
    try:
        promotion = Promotion.objects.get(id=promotion_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                #'status_code' : StatusCodes.INVALID_SUBSCRIPTION_ID_4031,
                'status_code_text' : 'INVALID_PROMOTION_ID',
                'response' : {
                    'message' : 'Promotion Not Found',
                    'error_message' : str(err),
                }
            },
                status=status.HTTP_404_NOT_FOUND
        )
        
    if promotion_type == 'Product':
        try:
            product_id=Product.objects.get(id=product)
        except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.PRODUCT_NOT_FOUND_4037,
                    'response' : {
                    'message' : 'Product not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        promotion.product = product_id
        promotion.service = None
        promotion.save()
    elif promotion_type == 'Service':
        try:
            service_id=Service.objects.get(id=service)
        except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.SERVICE_NOT_FOUND_4035,
                    'response' : {
                    'message' : 'Service not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        promotion.service= service_id
        promotion.product = None
        promotion.save()    
    serializer = PromotionSerializer(promotion, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(
                {
            'status' : False,
            'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
            'response' : {
                'message' : 'Promotion Serializer Invalid',
                'error_message' : str(serializer.errors),
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
                'message' : 'Update Promotion Successfully',
                'error_message' : None,
                'promotion' : serializer.data
            }
        },
        status=status.HTTP_200_OK
        )
        

    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_memberships(request):
    user = request.user
    business = request.data.get('business', None)
    name = request.data.get('name', None)
    
    description = request.data.get('description', None)
    terms_condition = request.data.get('term_condition', None)
    
    color = request.data.get('color', None)
    
    services = request.data.get('services', None)
    products = request.data.get('products',None)
    
    #membership_type = request.data.get('membership_type',None)
    #total_number = request.data.get('total_number',None)
    
    #percentage = request.data.get('session', None)
    valid_for = request.data.get('valid_for', None)
    #validity = request.data.get('validity', None)
    #months = request.data.get('months',None)
    price = request.data.get('price',None)
    tax_rate = request.data.get('tax_rate',None)
    discount = request.data.get('discount',None)
    currency_membership_price = request.data.get('currency_membership_price',None)#CurrencyPriceMembership
    
    if not all([business, name , valid_for, ]):
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
                          'name',
                          'validity',
                          'valid_for', 
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        business=Business.objects.get(id=business)
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
            
    membership_cr = Membership.objects.create(
        user = user,
        business=business, 
        name= name,
        #membership=membership_type,
        valid_for = valid_for,
        #validity = validity,
        # price = price,
        # tax_rate = tax_rate,
        #total_number = total_number,
        
        #New Require
        description = description,
        #color = color,
        term_condition = terms_condition,
        
        discount = discount,
        
    )
    if currency_membership_price is not None:
        if type(currency_membership_price) == str:
            currency_membership_price = currency_membership_price.replace("'" , '"')
            currency_membership_price = json.loads(services)
        else:
            pass
        for ser in currency_membership_price:
            curency = ser['currency']
            price = ser['price']
            
            try:
                currency_id = Currency.objects.get(id=curency)
            except Exception as err:
                return Response(
                    {
                        'status' : False,
                        'response' : {
                        'message' : 'Currency not found',
                        'error_message' : str(err),
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            services_obj = CurrencyPriceMembership.objects.create(
                membership = membership_cr,
                currency = currency_id,
                price = price,
            )
    if services is not None:
        if type(services) == str:
            services = services.replace("'" , '"')
            services = json.loads(services)
        else:
            pass
        for ser in services:
            percentage = ser.get('percentage', 0)
            duration = ser.get('duration', '7 Days')
            servic = ser['service']
            
            try:
                service_id=Service.objects.get(id=servic)
            except Exception as err:
                return Response(
                    {
                        'status' : False,
                        'status_code' : StatusCodes.SERVICE_NOT_FOUND_4035,
                        'response' : {
                        'message' : 'Service not found',
                        'error_message' : str(err),
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            services_obj = DiscountMembership.objects.create(
                membership = membership_cr,
                percentage =percentage,
                duration =duration,
                service = service_id
            )
    if products is not None:
        if type(products) == str:
            products = products.replace("'" , '"')
            products = json.loads(products)
        else:
            pass
        for pro in products:
            
            percentage = pro.get('percentage', 0)
            product = pro['product']
            duration = pro.get('duration', '7 Days')
            
            try:
                product_id=Product.objects.get(id=product)
            except Exception as err:
                return Response(
                    {
                        'status' : False,
                        'status_code' : StatusCodes.PRODUCT_NOT_FOUND_4037,
                        'response' : {
                        'message' : 'Product not found',
                        'error_message' : str(err),
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            services_obj = DiscountMembership.objects.create(
                membership = membership_cr,
                percentage =percentage,
                product = product_id,
                duration =duration,
            )
            
    serialized = MembershipSerializer(membership_cr)
       
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Membership Create!',
                    'error_message' : None,
                    'membership' : serialized.data,
                }
            },
            status=status.HTTP_201_CREATED
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_memberships(request):
    all_memberships= Membership.objects.all().order_by('-created_at')
    all_memberships_count = all_memberships.count()
    
    page_count = all_memberships_count / 20
    if page_count > int(page_count):
        page_count = int(page_count) + 1

    paginator = Paginator(all_memberships, 20)
    page_number = request.GET.get("page") 
    all_memberships = paginator.get_page(page_number)

    serialized = MembershipSerializer(all_memberships, many=True)
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Membership',
                'count':all_memberships_count,
                'pages':page_count,
                'per_page_result':20,
                'error_message' : None,
                'membership' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_memberships(request):
    memberships_id = request.data.get('memberships_id', None)
    if memberships_id is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required!',
                    'fields' : [
                        'memberships_id'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
          
    try:
        memberships = Membership.objects.get(id=memberships_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Membership ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    memberships.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Membership deleted successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_memberships(request):
    id = request.data.get('id', None)
    service = request.data.get('service', None)
    product = request.data.get('product',None)
    membership_type = request.data.get('membership_type',None)
    currency_membership = request.data.get('currency_membership',None)
    
    if id is None: 
        return Response(
        {
            'status' : False,
            'status_code' : StatusCodes.MISSING_FIELDS_4001,
            'status_code_text' : 'MISSING_FIELDS_4001',
            'response' : {
                'message' : 'Invalid Data!',
                'error_message' : 'Membership ID are required.',
                'fields' : [
                    'id'                         
                ]
            }
        },
        status=status.HTTP_400_BAD_REQUEST
        )
    try:
        membership = Membership.objects.get(id=id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code_text' : 'INVALID_MEMBERSHIP_ID',
                'response' : {
                    'message' : 'Membership Not Found',
                    'error_message' : str(err),
                }
            },
                status=status.HTTP_404_NOT_FOUND
        )
    if membership_type == 'Product':
        try:
            product_id=Product.objects.get(id=product)
        except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.PRODUCT_NOT_FOUND_4037,
                    'response' : {
                    'message' : 'Product not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        membership.product = product_id
        membership.service = None
        membership.save()
    elif membership_type == 'Service':
        try:
            service_id=Service.objects.get(id=service)
        except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.SERVICE_NOT_FOUND_4035,
                    'response' : {
                    'message' : 'Service not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        membership.service= service_id
        membership.product = None
        membership.save()
     
    if currency_membership:  
        if type(currency_membership) == str:
            currency_membership = currency_membership.replace("'" , '"')
            currency_membership = json.loads(currency_membership)

        elif type(currency_membership) == list:
            pass 
        
        for curr in currency_membership:
            currency = curr.get('currency', None)
            id = curr.get('id', None)
            #membership = curr.get('membership', None)
            price = curr.get('price', None)
            try:
                currency_id = Currency.objects.get(id=currency)
            except Exception as err:
                pass
            if id is not None:
                try:
                    currency_price = CurrencyPriceMembership.objects.get(id=id)
                except Exception as err:
                    pass
                
                currency_price.price = price
                currency_price.save()
            
            elif currency_id is not None: 
                try:
                    currency_price = CurrencyPriceMembership.objects.get(currency=currency_id)
                    currency_price.price = price
                    currency_price.save()
                except Exception as err:
                    #pass
                    services_obj = CurrencyPriceMembership.objects.create(
                        membership = membership,
                        currency = currency_id,
                        price = price,
                    )                
                
                
    serializer = MembershipSerializer(membership, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(
                {
            'status' : False,
            'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
            'response' : {
                'message' : 'Membership Serializer Invalid',
                'error_message' : str(serializer.errors),
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
                'message' : 'Update Membership Successfully',
                'error_message' : None,
                'membership' : serializer.data
            }
        },
        status=status.HTTP_200_OK
        )
       
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_vouchers(request):
    user = request.user
    business_id = request.data.get('business', None)
    
    name = request.data.get('name', None)
    value = request.data.get('value', None)
    voucher_type= request.data.get('voucher_type', None)
    
    #valid_for = request.data.get('valid_for', None)
    validity= request.data.get('validity', None)
    
    sales = request.data.get('sales', None)
    price = request.data.get('price', None)

    currency_voucher_price = request.data.get('currency_voucher_price',None)
    discount_percentage = request.data.get('discount_percentage',None)

    if not all([business_id , discount_percentage,name ,sales, voucher_type, validity]):
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
                          'name',
                          'value',
                          'voucher_type' ,
                          'sales',
                        #   'price', 
                          'validity',
                          'discount_percentage',
                            ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business=Business.objects.get(id=business_id)
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
    
    # if valid_for.lower() == 'days':
    #     days= days
    # else:
    #     months = months
        
    voucher = Vouchers.objects.create(
        user = user,
        business = business, 
        name = name,
        #value = value,
        validity=validity,
        voucher_type=voucher_type,
        #valid_for = valid_for,
        sales = sales,
        discount_percentage = discount_percentage,
        # price = price,  
        # 
        # discount = discount,  
        
    )
    if currency_voucher_price is not None:
        if type(currency_voucher_price) == str:
            currency_voucher_price = currency_voucher_price.replace("'" , '"')
            currency_voucher_price = json.loads(currency_voucher_price)
        else:
            pass
        for ser in currency_voucher_price:
            curency = ser['currency']
            price = ser['price']
            
            try:
                currency_id = Currency.objects.get(id=curency)
            except Exception as err:
                return Response(
                    {
                        'status' : False,
                        'response' : {
                        'message' : 'Currency not found',
                        'error_message' : str(err),
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            voucher_obj = VoucherCurrencyPrice.objects.create(
                voucher = voucher,
                currency = currency_id,
                price = price,
            )
            # voucher_obj.save()
    # voucher.days = days
    # voucher.months = months
    # voucher.save()
    # if voucher_type is not None:
    #     if type(voucher_type) == str:
    #         voucher_type = voucher_type.replace("'" , '"')
    #         voucher_type = json.loads(voucher_type)
    #     else:
    #         pass
    #     for ser in voucher_type:
    #         percentage = ser.get('percentage', 0)
    #         try:
    #             voucher_type=Vouchers.objects.get(id=voucher_type)
    #         except Exception as err:
    #             return Response(
    #                 {
    #                     'status' : False,
    #                     'status_code' : StatusCodes.SERVICE_NOT_FOUND_4035,
    #                     'response' : {
    #                     'message' : 'percentage not found',
    #                     'error_message' : str(err),
    #                     }
    #                 },
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
    #         percentage_obj = DiscountMembership.objects.create(
    #             percentage =percentage
    #         )
    serialized = VoucherSerializer(voucher)
       
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Voucher Create!',
                    'error_message' : None,
                    'voucher' : serialized.data,
                }
            },
            status=status.HTTP_201_CREATED
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_vouchers(request):
    all_voucher= Vouchers.objects.all().order_by('-created_at')
    all_voucher_count= all_voucher.count()

    page_count = all_voucher_count / 20
    if page_count > int(page_count):
        page_count = int(page_count) + 1

    paginator = Paginator(all_voucher, 20)
    page_number = request.GET.get("page") 
    all_voucher = paginator.get_page(page_number)

    serialized = VoucherSerializer(all_voucher, many=True)
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Voucher',
                'count':all_voucher_count,
                'pages':page_count,
                'per_page_result':20,
                'error_message' : None,
                'vouchers' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_vouchers(request):
    vouchers_id = request.data.get('id', None)
    if vouchers_id is None: 
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
        voucher = Vouchers.objects.get(id=vouchers_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid Voucher ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    voucher.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Voucher deleted successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_vouchers(request):
    id = request.data.get('id', None)
    currency_voucher = request.data.get('currency_voucher',None)

    if id is None: 
        return Response(
        {
            'status' : False,
            'status_code' : StatusCodes.MISSING_FIELDS_4001,
            'status_code_text' : 'MISSING_FIELDS_4001',
            'response' : {
                'message' : 'Invalid Data!',
                'error_message' : 'Voucher ID are required.',
                'fields' : [
                    'id'                         
                ]
            }
        },
        status=status.HTTP_400_BAD_REQUEST
        )
    try:
        vouchers = Vouchers.objects.get(id=id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code_text' : 'INVALID_VOUCHER_ID',
                'response' : {
                    'message' : 'Voucher Not Found',
                    'error_message' : str(err),
                }
            },
                status=status.HTTP_404_NOT_FOUND
        )

    if currency_voucher:  
        if type(currency_voucher) == str:
            currency_voucher = currency_voucher.replace("'" , '"')
            currency_voucher = json.loads(currency_voucher)

        elif type(currency_voucher) == list:
            pass 
        
        for curr in currency_voucher:
            currency = curr.get('currency', None)
            id = curr.get('id', None)
            price = curr.get('price', None)
            try:
                currency_id = Currency.objects.get(id=currency)
            except Exception as err:
                pass
            if id is not None:
                try:
                    currency_price = VoucherCurrencyPrice.objects.get(id=id)
                except Exception as err:
                    pass
                
                currency_price.price = price
                currency_price.save()
            
            elif currency_id is not None: 
                try:
                    currency_price = VoucherCurrencyPrice.objects.get(currency=currency_id)
                    currency_price.price = price
                    currency_price.save()
                except Exception as err:
                    #pass
                    services_obj = VoucherCurrencyPrice.objects.create(
                        voucher = vouchers,
                        currency = currency_id,
                        price = price,
                    )
    serializer = VoucherSerializer(vouchers, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(
                {
            'status' : False,
            'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
            'response' : {
                'message' : 'Voucher Serializer Invalid',
                'error_message' : str(serializer.errors),
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
                'message' : 'Update Voucher Successfully',
                'error_message' : None,
                'voucher' : serializer.data
            }
        },
        status=status.HTTP_200_OK
        )
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_loyalty(request):
    user = request.user
    business_id = request.data.get('business', None)
    name = request.data.get('name', None)
    # loyaltytype = request.data.get('loyaltytype', None)
    amount_spend = request.data.get('amount_spend', None)
    number_points = request.data.get('number_points', None)
    earn_points = request.data.get('earn_points', None)
    location = request.data.get('location', None)
    total_earn_from_points = request.data.get('total_earn_from_points', None)
    
    if not all([business_id , name ,amount_spend, number_points, earn_points]):
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
                          'name',
                        #   'loyaltytype',
                          'amount_spend' ,
                          'number_points',
                          'earn_points', 
                            ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business=Business.objects.get(id=business_id)
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
    
    if location is not None:
        try:
            business_address = BusinessAddress.objects.get(id=location)
        except Exception as err:
            return Response(
            {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response' : {
                    'message' : 'Location not found',
                }
            }
        )
    
    loyalty = LoyaltyPoints.objects.create(
        user = user,
        business = business,
        name =name,
        # loyaltytype = loyaltytype,
        amount_spend = amount_spend,
        number_points = number_points,
        earn_points = earn_points,
        total_earn_from_points = total_earn_from_points,
        location = business_address,
    )
    
    serialized = LoyaltyPointsSerializer(loyalty)
       
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'You have added a loyalty point',
                    'error_message' : None,
                    'loyalty' : serialized.data,
                }
            },
            status=status.HTTP_201_CREATED
        )
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_loyalty(request):
    all_loyalty= LoyaltyPoints.objects.filter(is_deleted = False).order_by('-created_at')
    serialized = LoyaltyPointsSerializer(all_loyalty, many= True)
       
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Loyalty',
                'error_message' : None,
                'loyalty' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    

@api_view(['GET'])
@permission_classes([AllowAny])
def get_client_available_loyalty_points(request):
    location_id = request.GET.get('location_id', None)
    client_id = request.GET.get('client_id', None)

    try:
        loyalty_point = LoyaltyPoints.objects.get(
            location__id = location_id,
            is_active = True,
            is_deleted = False
        )
    except Exception as error:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'response' : {
                    'message' : 'No Loyalty point found on this location',
                    'error_message' : str(error),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        client_loyalty_points = ClientLoyaltyPoint.objects.get(
            is_active = True,
            is_deleted = False,
            location__id = location_id,
            client__id = client_id,
            loyalty_points = loyalty_point
        )
    except Exception as error:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'response' : {
                    'message' : 'No Loyalty point found on this location against this Client',
                    'error_message' : str(error),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    data = ClientLoyaltyPointSerializer(client_loyalty_points).data
       
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Client Available Loyalty Points',
                'error_message' : None,
                'client_loyalty_points' : data
            }
        },
        status=status.HTTP_200_OK
    )



@api_view(['GET'])
@permission_classes([AllowAny])
def get_client_all_vouchers(request):
    location_id = request.GET.get('location_id', None)
    client_id = request.GET.get('client_id', None)

    try:
        client_vouchers = VoucherOrder.objects.filter(
            location__id = location_id,
            client__id = client_id,
        )
    except Exception as error:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'response' : {
                    'message' : 'No Vouchers is found on this location against this Client',
                    'error_message' : str(error),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    serialized = ClientVouchersSerializer(client_vouchers, many=True)
       
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Client Available Vouchers',
                'error_message' : None,
                'client_vouchers' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_client_all_memberships(request):
    location_id = request.GET.get('location_id', None)
    client_id = request.GET.get('client_id', None)

    try:
        client_membership = MemberShipOrder.objects.filter(
            location__id = location_id,
            client__id = client_id,
        )
    except Exception as error:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'response' : {
                    'message' : 'No Membership is found on this location against this Client',
                    'error_message' : str(error),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    serialized = ClientMembershipsSerializer(client_membership, many=True)
       
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'response' : {
                'message' : 'Client Available Memberships',
                'error_message' : None,
                'client_memberships' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_loyalty(request):
    loyalty_id = request.data.get('id', None)
    if loyalty_id is None: 
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
        loyalty = LoyaltyPoints.objects.get(id=loyalty_id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code' : 404,
                'status_code_text' : '404',
                'response' : {
                    'message' : 'Invalid loyalty ID!',
                    'error_message' : str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    loyalty.delete()
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Loyalty deleted successfully',
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )
    
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_loyalty(request):
    id = request.data.get('id', None)
    location = request.data.get('location', None)
    if id is None: 
        return Response(
        {
            'status' : False,
            'status_code' : StatusCodes.MISSING_FIELDS_4001,
            'status_code_text' : 'MISSING_FIELDS_4001',
            'response' : {
                'message' : 'Invalid Data!',
                'error_message' : 'ID are required.',
                'fields' : [
                    'id'                         
                ]
            }
        },
        status=status.HTTP_400_BAD_REQUEST
        )
    try:
        loyalty = LoyaltyPoints.objects.get(id=id)
    except Exception as err:
        return Response(
            {
                'status' : False,
                'status_code_text' : 'INVALID_LOYALTY_ID',
                'response' : {
                    'message' : 'Loyalty Not Found',
                    'error_message' : str(err),
                }
            },
                status=status.HTTP_404_NOT_FOUND
        )
        
    if location is not None:
        try:
            business_address = BusinessAddress.objects.get(id=location)
            loyalty.location = business_address
            loyalty.save()
        except Exception as err:
            return Response(
            {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response' : {
                    'message' : 'Location not found',
                }
            }
        )
        
    serializer = LoyaltyPointsSerializer(loyalty, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(
                {
            'status' : False,
            'status_code' : StatusCodes.SERIALIZER_INVALID_4024,
            'response' : {
                'message' : 'Loyalty Serializer Invalid',
                'error_message' : str(serializer.errors),
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
                'message' : 'Update loyalty Successfully',
                'error_message' : None,
                'voucher' : serializer.data
            }
        },
        status=status.HTTP_200_OK
        )
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_complimentary(request):
    client = request.GET.get('client', None)
    complimentary = request.GET.get('complimentary', None)
    if client is None: 
       return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required!',
                    'fields' : [
                        'client'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
       
    client = ClientPromotions.objects.filter(
        client__id =client, 
        complimentary__id =complimentary, 
        
        ).count()
    
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Client total Count',
                'count': client,
                'error_message' : None
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_client_package(request):
    client = request.GET.get('client', None)
    package = request.GET.get('package', None)
    package_service = request.GET.get('package_service', None)
    
    Error = []
    service_diff= []
    
    if client and package is None: 
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required!',
                    'fields' : [
                        'client'                         
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        client_validation = ClientPackageValidation.objects.get(
            client__id=client, 
            serviceduration__id=package_service,
            package__id = package
            )
    except Exception as err:
        Error.append(str(err))
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Client Validation not found ID!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    try:
        service_pac = ServiceDurationForSpecificTime.objects.get(id=package_service)
    except Exception as err:
        Error.append(str(err))
        return Response(
            {
                'status': False,
                'status_code': 404,
                'status_code_text': '404',
                'response': {
                    'message': 'Service Duration not found ID!',
                    'error_message': str(err),
                }
            },
            status=status.HTTP_404_NOT_FOUND
        )
    client_validation_te = client_validation.due_date
    current_date = date.today()
    if current_date <= client_validation_te:
        try:
            is_expired = False
            client_service = list(client_validation.service.all().values_list('id', flat=True))
            client_service_str = [str(uuid) for uuid in client_service]
            pac_service = list(service_pac.service.all().values_list('id', flat=True))
            pac_service_str = [str(uuid) for uuid in pac_service]
            
            service_diff = list(set(client_service_str) - set(pac_service_str)) + list(set(pac_service_str) - set(client_service_str))
        except Exception as err:
            Error.append(str(err))
            return Response(
                {
                    'status': False,
                    'status_code': 500,
                    'status_code_text': '500',
                    'response': {
                        'message': 'Error getting non-common elements!',
                        'error_message': str(err),
                    }
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:
        is_expired = True
    
    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Remain Service',
                'Service': service_diff,
                'error_message' : None,
                'Errors': Error,
                'is_expired':is_expired
            }
        },
        status=status.HTTP_200_OK
    )



@api_view(['GET'])
@permission_classes([AllowAny])
def get_customers_loyalty_points_logs(request):
    location_id = request.GET.get('location_id', None)
    customer_id = request.GET.get('customer_id',None)

    start_date = request.GET.get('start_date', '2020-01-01')
    end_date = request.GET.get('end_date', datetime.now().strftime('%Y-%m-%d'))

    if not all([location_id]):
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required!',
                    'fields' : [
                        'location_id',
                        'customer_id',                     
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    queries = {}
    if customer_id is not None:
        queries['client__id'] = customer_id

    customers_points = ClientLoyaltyPoint.objects.filter(
        location__id = location_id,
        created_at__date__range = (start_date, end_date),
        is_active = True,
        is_deleted = False,
        **queries
    ).order_by('-created_at')

    data = CustomerLoyaltyPointsLogsSerializer(customers_points, many=True).data

    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Loyalty Points Logs',
                'error_message' : None,
                'data' : data,
                'start_date' : start_date,
                'end_date' : end_date,
            }
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_customer_detailed_loyalty_points(request):
    location_id = request.GET.get('location_id', None)
    client_id = request.GET.get('customer_id', None)

    start_date = request.GET.get('start_date', '2020-01-01')
    end_date = request.GET.get('end_date', datetime.now().strftime('%Y-%m-%d'))


    if not all([location_id]):
        # client_id
        return Response(
            {
                'status' : False,
                'status_code' : StatusCodes.MISSING_FIELDS_4001,
                'status_code_text' : 'MISSING_FIELDS_4001',
                'response' : {
                    'message' : 'Invalid Data!',
                    'error_message' : 'fields are required!',
                    'fields' : [
                        'location_id',
                        'customer_id',
                    ]
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    clients_list = []
    if client_id is not None:
        clients_list.append(client_id)

    customers_points = LoyaltyPointLogs.objects.select_related(
        'location',
        'client',
        'loyalty',
    ).filter(
        # client__id__in = clients_list,
        location__id = location_id,
        created_at__date__range = (start_date, end_date),
        is_active = True,
        is_deleted = False
    ).order_by('-created_at')

    all_loyality_logs_count= customers_points.count()

    page_count = all_loyality_logs_count / 20
    if page_count > int(page_count):
        page_count = int(page_count) + 1

    paginator = Paginator(customers_points, 20)
    page_number = request.GET.get("page") 
    customers_points = paginator.get_page(page_number)

    data = CustomerDetailedLoyaltyPointsLogsSerializer(customers_points, many=True).data

    return Response(
        {
            'status' : True,
            'status_code' : 200,
            'status_code_text' : '200',
            'response' : {
                'message' : 'Loyalty Points Logs',
                'count':all_loyality_logs_count,
                'pages':page_count,
                'per_page_result':20,
                'error_message' : None,
                'data' : data
            }
        },
        status=status.HTTP_200_OK
    )

# Select Related  => Single Object => (Inside FK + OTO Relaion)
# prefetch related => Many to Many => (MTM + Outside FK)