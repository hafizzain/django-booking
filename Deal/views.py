from django.shortcuts import render


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

# Create your views here.

from Deal.models import Deal, DealCategory, RedeemableChannel
from Deal.serializers import DealSerializer

from Product.models import Product

@api_view(['GET'])
def get_deal_audience_choices(request):
    return Response({'data' : [
        {'name' : 'Public', 'id' : 'public'},
        {'name' : 'Pre Set Customer', 'id' : 'pre-set-users'},
    ]})
@api_view(['GET'])
def get_deal_validity(request):
    return Response({'data' : [
        {
            "id": "from-start-to-end-date",
            "name": "From deal start date to end date"
        },
        {
            "id": "days-from-start-date",
            "name": "Days from deal activation date"
        },
        {
            "id": "months-from-start-date",
            "name": "Months from deal activation date"
        },
        {
            "id": "years-from-start-date",
            "name": "Years from deal activation date"
        }
    ]})
@api_view(['GET'])
def get_deal_type_choices(request):
    return Response({'data' : [
        # {'name' : 'Fixed Amount Discount Deal', 'id' : 'Fixed Amount Discount Deal'},
        # {'name' : 'Percentage Discount Deal', 'id' : 'Percentage Discount Deal'},
        # {'name' : 'Buy one or more item get one or more free/discount', 'id' : 'Buy one or more item get one or more free/discount'},
        # {'name' : 'Complimentary Voucher', 'id' : 'Complimentary Voucher'},
        # {'name' : 'Custom Package', 'id' : 'Custom Package'},
        # {'name' : 'Get free item when user purchase specific items in given period', 'id' : 'Get free item when user purchase specific items in given period'},
        # {'name' : 'Spend some amount and get some item free', 'id' : 'Spend some amount and get some item free'},
        # {'name' : 'Fixed price items deal', 'id' : 'Fixed price items deal'},
        {
            "typeId": "A0AAC170420559558891",
            "name": "Fixed Amount Discount Deal",
            "displayName": "Fixed Amount Discount Deal",
            "status": "Active",
            "settingsPageUrlSlug": "fixed-amount-discount-deal"
        },
        {
            "typeId": "A0AAC170490484113323",
            "name": "Percentage Discount Deal",
            "displayName": "Percentage Discount Deal",
            "status": "Active",
            "settingsPageUrlSlug": "percentage-discount-deal"
        },
        {
            "typeId": "A0AAC170490489535155",
            "name": "Buy one or more item get one or more free/discount",
            "displayName": "Buy one or more item get some reward",
            "status": "Active",
            "settingsPageUrlSlug": "buy-some-get-some-free-or-discount"
        },
        {
            "typeId": "A0AAC170490490810243",
            "name": "Complimentary Voucher",
            "displayName": "Complimentary Voucher",
            "status": "Active",
            "settingsPageUrlSlug": "complimentary-voucher"
        },
        {
            "typeId": "A0AAC170490492936083",
            "name": "Custom Package",
            "displayName": "Package Deal",
            "status": "Active",
            "settingsPageUrlSlug": "package"
        },
        {
            "typeId": "A0AAC170490503141048",
            "name": "Get free item when user purchase specific items in given period",
            "displayName": "Get free item upon purchasing specific items",
            "status": "Active",
            "settingsPageUrlSlug": "get-free-on-purchasing-specific-items"
        },
        {
            "typeId": "A0AAC170490506207590",
            "name": "Spend some amount and get some item free",
            "displayName": "Spend some amount and get some item free",
            "status": "Active",
            "settingsPageUrlSlug": "spend-some-amount-get-some-reward"
        },
        {
            "typeId": "A0AAC170490509349974",
            "name": "Fixed price items deal",
            "displayName": "Fixed price items deal",
            "status": "Active",
            "settingsPageUrlSlug": "fixed-price-items-deal"
        }
    ]})
@api_view(['GET'])
def get_redeemable_channels(request):
    channels = RedeemableChannel.objects.all()
    channels = [{"channelId" : channel.id, "name" : channel.name} for channel in channels]

    return Response({'data' : channels})
    # return Response({'data' : 
    # [
    #     {
    #     "channelId": "pos",
    #     "name": "POS"
    #     },
    #     {
    #     "channelId": "mobile-app",
    #     "name": "Mobile App"
    #     },
    #     {
    #     "channelId": "online",
    #     "name": "Online"
    #     }
    #     ]
    # })

@api_view(['GET'])
def get_deal_category(request):
    categories = DealCategory.objects.all().values('id', 'name')
    return Response({
        'data' : list(categories)
    })
@api_view(['POST'])
def create_deal(request):
    try:
        deal = Deal.objects.get(code =request.data.get('code'))
    except:
        pass
    else:
        return Response({
            'message' : 'Deal already exist with this code',
        }, status.HTTP_400_BAD_REQUEST)

    serialized = DealSerializer(data=request.data)
    if serialized.is_valid():
        serialized.save()
        return Response({'message' : 'Deal created sucessfully', 'deal' :  serialized.data}, status.HTTP_201_CREATED)

    return Response({
        'message' : 'Invalid Data',
        'error_messages' : serialized.errors
    }, status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_deal(request, deal_id):
    try:
        deal = Deal.objects.get(id = deal_id)
    except Exception as err:
        return Response({
            'message' : 'Invalid Id',
            'error_message' : str(err)
        }, status.HTTP_404_NOT_FOUND)

    # try:
    #     Deal.objects.get(code =request.data.get('code'))
    # except:
    #     pass
    # else:
    #     return Response({
    #         'message' : 'Deal already exist with this code',
    #     }, status.HTTP_400_BAD_REQUEST)

    serialized = DealSerializer(deal, data=request.data, partial=True)
    if serialized.is_valid():
        serialized.save()
        return Response({'message' : 'Deal updated sucessfully', 'deal' :  serialized.data})

    return Response({
        'message' : 'Invalid Data',
        'error_messages' : serialized.errors
    }, status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_all_deals(request):

    deals = Deal.objects.all()
    data = DealSerializer(deals, many=True).data
    return Response({
        'data' : data,
    })

@api_view(['GET'])
def get_single_deal(request, deal_id):

    try:
        deal = Deal.objects.get(id = deal_id)
    except:
        return Response({
            'message' : 'Deal not found',
        }, status.HTTP_404_NOT_FOUND)

    data = DealSerializer(deal).data
    return Response({**data})


@api_view(['GET'])
def get_products(request):

    products = Product.objects.filter(is_active=True, is_deleted=False, is_blocked=False).values('id', 'name')
    

    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(products, request)
    return paginator.get_paginated_response(result_page)

    return Response({
        "data" : dict(paginator.get_paginated_response(result_page)),
        "response" : {
            "status": "result-found",
            "statusCode": 200,
            "message": "10 records found",
            "data": {
                "page": 0,
                "totalRecords": products.count(),
                "totalPageCount": products.count() / 10,
                "recordsPerPage": 10,
                "list": result_page
            }
        }
    })