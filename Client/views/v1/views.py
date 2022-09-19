from http import client
from re import M
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from Service.models import Service
from Business.models import Business
from Product.models import Product
from Utility.models import Country, State, City
from Client.models import Client, ClientGroup, Subscription , Rewards , Promotion , Membership , Vouchers
from Client.serializers import ClientSerializer, ClientGroupSerializer, SubscriptionSerializer , RewardSerializer , PromotionSerializer , MembershipSerializer , VoucherSerializer
from Utility.models import NstyleFile

import json
from NStyle.Constants import StatusCodes

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_client(request):
    client_csv = request.data.get('file', None)
    user= request.user
    business_id = request.data.get('business', None)

    file = NstyleFile.objects.create(
        file = client_csv
    )
    with open( file.file.path , 'r', encoding='utf-8') as imp_file:
        for index, row in enumerate(imp_file):
            if index == 0:
                continue
            row = row.split(',')
            row = row
            
            if len(row) < 6:
                continue
            
            name= row[0].strip('"')
            email = row[1].strip('"')
            client_id = row[2].strip('"')
            gender = row[3].strip('"')
            address = row[4].strip('"')
            active = row[5].replace('\n', '').strip('"') 

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
                client_id = client_id,
                email = email,
                gender = gender,
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
        client = Client.objects.get(id=client_id)
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
    all_client=Client.objects.all().order_by('-created_at')
    serialized = ClientSerializer(all_client, many=True,  context={'request' : request})
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Client',
                'error_message' : None,
                'client' : serialized.data
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
    
    postal_code= request.data.get('postal_code' , None)
    address= request.data.get('address' , None)
    card_number= request.data.get('card_number' , None)
    is_active = True if request.data.get('is_active', None) is not None else False
    
    city= request.data.get('city', None)
    state= request.data.get('state', None)
    country= request.data.get('country', None)
    
    if not all([business_id, client_id, full_name , email ,gender  ,address ]):
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
                        'email',
                        'gender', 
                        'postal_code', 
                        'address' ,
                        'is_active',
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
        
    client=Client.objects.create(
        user=user,
        business=business,
        full_name = full_name,
        image= image,
        client_id=client_id,
        email= email,
        mobile_number=mobile_number,
        dob=dob,
        address=address,
        gender= gender,
        country= country,
        state = state,
        city = city,
        postal_code= postal_code,
        card_number= card_number,
        is_active = is_active
    )
    serialized= ClientSerializer(client, context={'request' : request})
    return Response(
        {
            'status' : True,
            'status_code' : 201,
            'response' : {
                'message' : 'Client Added!',
                'error_message' : None,
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
        client.is_active = True  if request.data.get('image',None) is not None else False

        if image is not None:
            client.image=image

        client.save()
        serialized= ClientSerializer(client, data=request.data, partial=True, context={'request' : request})
        if serialized.is_valid():
           serialized.save()
           return Response(
            {
                'status' : True,
                'status_code' : 200,
                'response' : {
                    'message' : 'Update Client Successfully',
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
    
    client.delete()
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
    serialized = ClientGroupSerializer(all_client_group, many=True,  context={'request' : request})
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Client Group',
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
    product= request.data.get('product', None)
    service_id= request.data.get('service', None)
    days= request.data.get('days',None)
    select_amount = request.data.get('select_amount', None)
    services_count= request.data.get('services_count', None)
    price= request.data.get('price', None)
    
    is_active= request.data.get('is_active', None)
    
    if not all([business, name ,product , days ,select_amount , services_count , price  ]):
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
        services_count=services_count,
        price=price,
        subscription_type = subscription_type,
        is_active= is_active,

    )
    if subscription_type == 'Product':
        try:
            product=Product.objects.get(id=product)
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
        client_subscription.product = product     
    else:
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
            
        client_subscription.service = service
    
    client_subscription.save()
        
    
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
    subscription_id = request.data.get('subscription_id', None)
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
                    'subscription'                         
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
    service = request.data.get('service', None)
    product = request.data.get('product', None)
    
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
    if reward_type == 'Product':
        try:
            product=Product.objects.get(id=product)
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
            
    rewards = Rewards.objects.create(
        user = user,
        business=business, 
        name=name,
        service=service,
        product=product,
        reward_value=reward_value,
        reward_point=reward_point,
        total_points = total_points,
        discount = discount,
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
        attendence = Rewards.objects.get(id=rewards_id)
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
    
    attendence.delete()
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
   
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_promotion(request):
    user = request.user
    business = request.data.get('business', None)
    promotion_type = request.data.get('promotion_type', None)
    
    service  = request.data.get('service', None)
    services = request.data.get('services', None)
    
    product = request.data.get('product', None)
    products = request.data.get('products', None)
    
    discount_product= request.data.get('discount_product', None)
    discount_service = request.data.get('discount_service', None)
    discount = request.data.get('discount', None)
    duration = request.data.get('duration', None)
    
    if not all([business, promotion_type, duration, discount]):
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
                          'promotion_type',
                          'discount_product',
                          'discount_service', 
                          'discount', 
                          'duration', 

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
    if promotion_type == 'Product':
        try:
            product=Product.objects.get(id=product)
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
        try:
            discount_product=Product.objects.get(id=discount_product)
        except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.PRODUCT_NOT_FOUND_4037,
                    'response' : {
                    'message' : 'Discount Product not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
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
            
        try:
            discount_service=Service.objects.get(id=discount_service)
        except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.SERVICE_NOT_FOUND_4035,
                    'response' : {
                    'message' : 'Discount Service not found',
                    'error_message' : str(err),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    promotion = Promotion.objects.create(
        user = user,
        business = business,
        promotion_type = promotion_type,
        service= service,
        services= services,
        product = product,
        products = products,
        discount_service = discount_service,
        discount_product = discount_product,
        discount = discount,
        duration = duration,
    )
    
    serialized = PromotionSerializer(promotion)
       
    return Response(
            {
                'status' : True,
                'status_code' : 201,
                'response' : {
                    'message' : 'Promotion Create!',
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
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_memberships(request):
    user = request.user
    business = request.data.get('business', None)
    name = request.data.get('name', None)
    description = request.data.get('description', None)
    service = request.data.get('service', None)
    session = request.data.get('session', None)
    valid_for = request.data.get('valid_for', None)
    days = request.data.get('days', None)
    months = request.data.get('months',None)
    price = request.data.get('price',None)
    tax_rate = request.data.get('tax_rate',None)
    color = request.data.get('color', None)
    
    if not all([business, name , service, session, valid_for, price, tax_rate]):
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
                          'service',
                          'session', 
                          'valid_for', 
                          'price',
                          'tax_rate'

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
    membership = Membership.objects.create(
        user = user,
        business=business, 
        name= name,
        description= description,
        service = service,
        session = session,
        valid_for = valid_for,
        days = days,
        months = months,
        price = price,
        tax_rate= tax_rate,
        color = color, 
    )
    
    serialized = MembershipSerializer(membership)
       
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
    serialized = MembershipSerializer(all_memberships, many=True)
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Membership',
                'error_message' : None,
                'membership' : serialized.data
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
    
    valid_for = request.data.get('valid_for', None)
    days= request.data.get('days', None)
    months = request.data.get('months', None)
    
    sales = request.data.get('sales', None)
    price = request.data.get('price', None)
    if not all([business_id , name , value ,valid_for,sales, price, voucher_type]):
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
                          'valid_for', 
                          'sales',
                          'price'
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
    
    if valid_for.lower() == 'days':
        days= days
    else:
        months = months
        
    voucher = Vouchers.objects.create(
        user = user,
        business = business, 
        name = name,
        value = value,
        voucher_type=voucher_type,
        valid_for = valid_for,
        sales = sales,
        price = price,     
        
    )
    voucher.days = days
    voucher.months = months
    voucher.save()
    
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
    serialized = VoucherSerializer(all_voucher, many=True)
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Voucher',
                'error_message' : None,
                'vouchers' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )