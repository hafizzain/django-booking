from django.shortcuts import render


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
# Create your views here.


def create_deal(request):
    return Response({
        'message' : 'Invalid Data'
    }, status.HTTP_400_BAD_REQUEST)