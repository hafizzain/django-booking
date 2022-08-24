from django.shortcuts import render
from Employee.models import Employee
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from Employee.serializers import EmployeSerializer
from rest_framework import status



# Create your views here.
@api_view(['GET'])
@permission_classes([AllowAny])
def getEmployees(request):
    all_employe= Employee.objects.all()
    serialized = EmployeSerializer(all_employe, many=True)
    return Response(
        {
            'status' : 200,
            'status_code' : '200',
            'response' : {
                'message' : 'All Employee',
                'error_message' : None,
                'Employees' : serialized.data
            }
        },
        status=status.HTTP_200_OK
    )
    
