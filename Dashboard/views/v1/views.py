from django.conf import settings
from operator import ge
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from Appointment.models import AppointmentCheckout
from NStyle.Constants import StatusCodes
from Business.models import Business, BusinessAddress

@api_view(['GET'])
@permission_classes([AllowAny])
def get_busines_client_appointment(request):
    business_id = request.data.get('business', None)
    
    if not all([business_id]):
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
    print(business_id)
    try:
        business_address = BusinessAddress.objects.get(id=business_id)
    except Exception as err:
            return Response(
            {
                    'status' : False,
                    # 'error_message' : str(err),
                    'status_code' : StatusCodes.BUSINESS_NOT_FOUND_4015,
                    'response' : {
                    'message' : 'Business not found',
                }
            }
        )
        
    #orders_price = Order.objects.aggregate(Total= Sum('total_price'))
    total_revenue = 0
    appointments_count = 0
    appointment = AppointmentCheckout.objects.filter(business_address = business_address)
    for order in appointment:
        appointments_count +=1
        if order.total_price is not None:
            total_revenue += order.total_price
    
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'Total Revenue',
                'error_message' : None,
                'revenue' : total_revenue,
                'appointments_count': appointments_count
            }
        },
        status=status.HTTP_200_OK
    )
    
