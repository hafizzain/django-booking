from http import client
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from Business.models import Business
from Product.models import Product
from Utility.models import Country, State, City
from Client.models import Client, ClientGroup, Subscription
from Client.serializers import ClientSerializer, ClientGroupSerializer, SubscriptionSerializer


import json

from NStyle.Constants import StatusCodes

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
    serialized = ClientGroupSerializer(all_client_group, many=True)
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
            serialized=ClientGroupSerializer(client_group)
       
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
        for usr in client:
            try:
               employe = Client.objects.get(id=usr)  
               #print(employe)
               client_group.employees.add(employe)
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
    
    name= request.data.get('name', None)
    product= request.data.get('product', None)
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
                }
            )
            
    try:
             product=Product.objects.get(id=product)
    except Exception as err:
            return Response(
                {
                    'status' : False,
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response' : {
                    'message' : 'Product not found',
                    'error_message' : str(err),
                }
                }
            )
            
    client_subscription= Subscription.objects.create(
        user =user,
        business=business, 
        name= name,
        product=product,
        days=days,
        select_amount=select_amount,
        services_count=services_count,
        price=price,
        
        
    )
    if is_active is not None:
        is_active = True
    else: 
        is_active = False
    
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