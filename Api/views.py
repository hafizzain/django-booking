from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
#import geoip2.database
from django.contrib.gis.geoip2 import GeoIP2
    
# Create your views here.
@api_view(['GET'])
@permission_classes([AllowAny])
def country_code(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:

       ip = x_forwarded_for.split(',')[0]

    else:

       ip = request.META.get('REMOTE_ADDR')
       
    g = GeoIP2()
    location = g.city(ip)
    location_country = location["country_code"]
    if location_country is not None:
          return Response({
           'status' : 404,
            'error_message' : 'Country not in database'
        })
      
    return Response({
        'country_code' : location_country,
    })