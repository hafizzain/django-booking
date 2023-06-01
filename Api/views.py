from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

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

   try:
      g = GeoIP2()
      location = g.city(ip)
      location_country = location["country_code"]
   except:
      location_country = 'pk'

   return Response({
      'country_code' : location_country,
   })

    
def EmailTemplate(request):
   
   context={'user_name': 'Abdullah',
             'otp': '7891',
             'email': 'user_otp.user.email',
             
             }
   
   #return render(request, "AppointmentEmail/add_appointment.html", context = {'user_name': 'Abdullah' , 'email': 'abc@user_otp.user.email',  'otp': '7891', })
   # return render(request, "Sales/quick_sales_staff.html", {'name': 'member_id','location':'location', 'sale_type': 'ids', 'invoice': 'invoice', 'date': 'date','time': 'current_time', 'client': 'client'})
   return render(request, "AppointmentEmail/new_appointment_n.html", {'name': 'member_id','location':'location', 'sale_type': 'ids', 'invoice': 'invoice', 'date': 'date','time': 'current_time', 'client': 'client','service': 'service','duration': 'duration','phone': 'phone','email': 'email',})