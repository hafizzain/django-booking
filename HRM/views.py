from django.shortcuts import render 
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import filters
from django.shortcuts import get_object_or_404
from django.db.models import Q
from HRM.models import *
from HRM.serializers import *

# Create your views here.

class HolidayApiView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    page_size = 10
    
    queryset = Holiday.objects.select_related('business', 'location')
    serializer_class = HolidaySerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'start_date', 'end_date']
    
    def get(self, request, pk=None):
        no_pagination = request.GET.get('no_pagination', None)
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
            query = Q()
            name = self.request.query_params.get('search_text', None)
            if name:
                query &= Q(name__icontains=name)
            
            start_date = self.request.query_params.get('start_date', None)
            if start_date:
                query &= Q(start_date__gte=start_date)
            
            end_date = self.request.query_params.get('end_date', None)
            if end_date:
                query &= Q(end_date__lte=end_date)
            
            filtered_queryset = Holiday.objects.filter(query) \
                            .order_by('-created_at')
            serializer = HolidaySerializer(filtered_queryset, many=True)

            if no_pagination:
                serializer = HolidaySerializer(filtered_queryset, many=True,
                                               context={'request': request})
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
                paginator = self.pagination_class()
                result_page = paginator.paginate_queryset(filtered_queryset, request)
                serializer = HolidaySerializer(result_page, many=True,
                                               context={'request': request})
                data = {
                        'count': paginator.page.paginator.count,
                        'next': paginator.get_next_link(),
                        'previous': paginator.get_previous_link(),
                        'current_page': paginator.page.number,
                        'per_page': self.page_size,
                        'total_pages': paginator.page.paginator.num_pages,
                        "success": True,
                        "status_code" : 200,
                        "response" : {
                            "message" : "Holiday get Successfully",
                            "error_message" : None,
                            "data" : serializer.data
                        }
                    }
                return Response(data, status=status.HTTP_200_OK)
    
    @transaction.atomic
    def post(self, request):
        user = request.user
        holiday_data = request.data.copy()
        holiday_data['user'] = user.id
        
        if 'is_active' not in holiday_data:     #due to unknown clash 
            holiday_data['is_active'] = True
        # request.data['user'] = user.id
        serializer = HolidaySerializer(data=holiday_data,
                                       context={'request': request})
        if serializer.is_valid():
            serializer.save()
            data = {
                "success": True,
                "status_code": 201,
                "response": {
                    "message": "Holiday created successfully",
                    "error_message": None,
                    "data": serializer.data
                }
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                "success": False,
                "status_code": 400,
                "response": {
                    "message": "Holiday not created",
                    "error_message": serializer.errors,
                    "data": None
                }
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        
    @transaction.atomic
    def patch(self, request, pk):
        holiday = get_object_or_404(Holiday, id=pk)
        request.data.get('user', None)
        serializer = HolidaySerializer(holiday,
                                       data=request.data,
                                       partial=True)
        if serializer.is_valid():
            serializer.save()
            data = {
                    "success": True,
                    "status_code" : 201,
                    "response" : {
                        "message" : "Holiday updated successfully",
                        "error_message" : None,
                        "data" : serializer.data
                    }
                }
            return Response(data, status=status.HTTP_200_OK)
        else:    
            data = {
                    "success": False,
                    "status_code" : 400,
                    "response" : {
                        "message" : "Holiday not updated",
                        "error_message" : serializer.errors,
                        "data" : None
                    }
                }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        
    @transaction.atomic   
    def delete(self, request, pk):
        holiday = get_object_or_404(Holiday, id=pk)
        holiday.delete()
        data = {
                "success": True,
                "status_code" : 200,
                "response" : {
                    "message" : "Holiday deleted successfully",
                    "error_message" : None,
                    "data" : None
                }
            }
        return Response(data, status=status.HTTP_200_OK)