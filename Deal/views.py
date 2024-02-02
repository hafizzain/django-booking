from django.shortcuts import render


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
# Create your views here.

from Deal.models import Deal, DealCategory
from Deal.serializers import DealSerializer


def get_deal_audience_choices(request):
    return Response([
        {'name' : 'Public', 'id' : 'public'},
        {'name' : 'Pre Set Customer', 'id' : 'pre-set-users'},
    ])

def get_deal_validity(request):
    return Response([
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
    ])

def get_deal_type_choices(request):
    return Response([
        {'name' : 'Fixed Amount Discount Deal', 'id' : 'Fixed Amount Discount Deal'},
        {'name' : 'Percentage Discount Deal', 'id' : 'Percentage Discount Deal'},
        {'name' : 'Buy one or more item get one or more free/discount', 'id' : 'Buy one or more item get one or more free/discount'},
        {'name' : 'Complimentary Voucher', 'id' : 'Complimentary Voucher'},
        {'name' : 'Custom Package', 'id' : 'Custom Package'},
        {'name' : 'Get free item when user purchase specific items in given period', 'id' : 'Get free item when user purchase specific items in given period'},
        {'name' : 'Spend some amount and get some item free', 'id' : 'Spend some amount and get some item free'},
        {'name' : 'Fixed price items deal', 'id' : 'Fixed price items deal'},
    ])

def get_deal_category(request):
    categories = DealCategory.objects.all().values('id', 'name')
    return Response({
        'data' : list(categories)
    })

def create_deal(request):

    serialized = DealSerializer(data=request.data)
    return Response({
        'message' : 'Invalid Data'
    }, status.HTTP_400_BAD_REQUEST)