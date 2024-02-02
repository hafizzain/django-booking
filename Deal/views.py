from django.shortcuts import render


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
# Create your views here.

from Deal.models import Deal, DealCategory
from Deal.serializers import DealSerializer


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
        {'name' : 'Fixed Amount Discount Deal', 'id' : 'Fixed Amount Discount Deal'},
        {'name' : 'Percentage Discount Deal', 'id' : 'Percentage Discount Deal'},
        {'name' : 'Buy one or more item get one or more free/discount', 'id' : 'Buy one or more item get one or more free/discount'},
        {'name' : 'Complimentary Voucher', 'id' : 'Complimentary Voucher'},
        {'name' : 'Custom Package', 'id' : 'Custom Package'},
        {'name' : 'Get free item when user purchase specific items in given period', 'id' : 'Get free item when user purchase specific items in given period'},
        {'name' : 'Spend some amount and get some item free', 'id' : 'Spend some amount and get some item free'},
        {'name' : 'Fixed price items deal', 'id' : 'Fixed price items deal'},
    ]})

@api_view(['GET'])
def get_deal_category(request):
    categories = DealCategory.objects.all().values('id', 'name')
    return Response({
        'data' : list(categories)
    })
@api_view(['POST'])
def create_deal(request):

    serialized = DealSerializer(data=request.data)
    if serialized.is_valid():
        serialized.save()
        return Response(serialized.data, status.HTTP_201_CREATED)

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