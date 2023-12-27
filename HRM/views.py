from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import filters
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import *
from .serializers import *


# Create your views here.

class HolidayApiView(APIView):
    permission_classes = [IsAuthenticated]
    
    queryset = Holiday.objects.select_related('business', 'location')
    serializer = HolidaySerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'start_date', 'end_date']
    
    def get(self, request, pk=None):
        
        if pk is not None:
            holiday = get_object_or_404(Holiday, id=pk)
            serializer = HolidaySerializer(holiday)
            data = {
                    "success": True,
                    "status_code" : 200,
                    "response" : {
                        "message" : "Holiday get Successfully",
                        "error_message" : None,
                        "data" : serializer.data
                    }
                }
            return Response(data, status=status.HTTP_200_OK)
        else:
            filtered_queryset = Holiday.objects.all() \
                            .order_by('-created_at')
            
            