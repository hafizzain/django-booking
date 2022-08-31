from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
import json

from NStyle.Constants import StatusCodes

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_client(request):
    user = request.user  
    
    full_name= request.data.get('full_name', None)
    employee_id= request.data.get('employee_id', None)
    
    email= request.data.get('email', None)
    image = request.data.get('image', None)
    business_id= request.data.get('business', None)  
    mobile_number= request.data.get('mobile_number', None)    
    dob= request.data.get('dob', None)
    gender = request.data.get('gender' , 'Male')
    
    postal_code= request.data.get('postal_code' , None)
    address= request.data.get('address' , None)
    joining_date = request.data.get('joining_date', None)
    to_present = request.data.get('to_present', False)
    ending_date= request.data.get('ending_date',None)   
