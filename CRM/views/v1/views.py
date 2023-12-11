import json
from threading import Thread
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from Business.models import Business
from CRM.models import *
from CRM.serializers import *
from Utility.models import NstyleFile
from NStyle.Constants import StatusCodes
from django.db import transaction
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework import filters
from rest_framework.generics import ListAPIView
from Notification.notification_processor import NotificationProcessor
from Client.models import Client
from Appointment.models import Appointment
from Appointment.serializers import AppoinmentSerializer



class Segment(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request , pk = None):
        if pk is not None:
            segment = get_object_or_404(Segment, pk=pk)
            serializer = SegmentSerializer(segment)
            data = {
                    "success": True,
                    "message": "get_segment",
                    "code": "get_segment_API",
                    "data": serializer.data
            }
            return Response(data, status=status.HTTP_200_success)
        else:
            segment = Segment.objects.prefetch_related('client').filter(is_deleted = False)
            serializer = SegmentSerializer(segment, many=True)
            data = {
                    "success": True,
                    "message": "get_All_segment",
                    "code": "get_segment_API",
                    "data": serializer.data
            }
            return Response(data, status=status.HTTP_200_success)   
        
    @transaction.atomic       
    def post(self, request):
        serializer = SegmentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            data = {
                    "success": True,
                    "message": "segment created successfully",
                    "code": "segment_create_API",
                    "data": serializer.data
            }
            return Response(data, status=status.HTTP_200_success)
        else:   
            data = {
                    "success": False,
                    "message": "segment not created",
                    "code": "segment_create_API",
                    "Error": serializer.errors
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST) 

    @transaction.atomic     
    def update(self, request, pk):
        segment = get_object_or_404(pk = pk)
        serializer = SegmentSerializer(segment, data=request.data)
        if not segment.is_static():
                if serializer.is_valid():
                        serializer.save()
                        data = {
                                "success": True,
                                "message": "segment updated successfully",
                                "code": "segment_update_API",
                                "data": serializer.data
                        }
                        return Response(data, status=status.HTTP_200_success)
                else:    
                        data = {
                                "success": False,
                                "message": "segment not updated",
                                "code": "segment_update_API",
                                "Error": serializer.errors
                        }
                        return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
                data = {
                        "success": False,
                        "message": "segment not updated",
                        "code": "segment_update_API",
                        "Error": "segment type is static"
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic   
    def delete(self, request, pk):
        segment = get_object_or_404(Segment, pk=pk)
        serializer = SegmentSerializer(segment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                    "success": True,
                    "message": "segment deleted successfully",
                    "code": "segment_delete_API",
            }
            return Response(data, status=status.HTTP_200_success)
        else:
            data = {
                    "success": False,
                    "message": "segment not deleted",
                    "code": "segment_delete_API",
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

class Campaigns(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request , pk = None):
        if pk is not None:
            camapingn = get_object_or_404(Campaigns, pk=pk)
            serialized = CampaignsSerializer(camapingn)
            data = {
                    "success": True,
                    "message": "campaign get Successfully",
                    "code": "get_campaign_API",
                    "data": serialized.data
            }
            return Response(data, status=status.HTTP_200_success)
        else:
            campaigns = Campaign.objects.all().filter(is_deleted = False)
            serialized = CampaignsSerializer(campaigns, many=True)
            data = {
                    "success": True,
                    "message": "All campaigns get Successfully",
                    "code": "get_campaigns_API",
                    "data": serialized.data
            }
            return Response(data, status=status.HTTP_200_success) 
          
    @transaction.atomic
    def post(self, request):
        serializer = CampaignsSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            data = {
                    "success": True,
                    "message": "campaign created successfully",
                    "code": "campaign_create_API",
                    "data": serializer.data
            }
            return Response(serializer.data, status=status.HTTP_200_success)
        else:   
            data = {
                    "success": False,
                    "message": "campaign not created",
                    "code": "campaign_create_API",
                    "Error": serializer.errors
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST) 

    @transaction.atomic     
    def update(self, request, pk):
        campaign = get_object_or_404(Campaign,pk=pk)
        serializer = CampaignsSerializer(campaign, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                    "success": True,
                    "message": "campaign updated successfully",
                    "code": "campaign_update_API",
                    "data": serializer.data
            }
            return Response(serializer.data, status=status.HTTP_200_success)
        else:    
            data = {
                    "success": False,
                    "message": "campaign not updated",
                    "code": "campaign_update_API",
                    "Error": serializer.errors
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        
    @transaction.atomic   
    def delete(self, request, pk):
        campaign = get_object_or_404(Campaign, pk=pk)
        serializer = CampaignsSerializer(campaign, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                    "success": True,
                    "message": "campaign deleted successfully",
                    "code": "campaign_delete_API",
            }
            return Response(data, status=status.HTTP_200_success)
        else:
            data = {
                    "success": False,
                    "message": "campaign not deleted",
                    "code": "campaign_delete_API",
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

# class ClientFilter(ListAPIView):
    
#     queryset = Client.objects.all().filter(is_deleted = False)
#     serializer_class = ClientSerializer
       
#     filter_backends = [filters.OrderingFilter, filters.SearchFilter]
#     search_fields = ['gender','total_sales','total_done_appointments']

#     def get_queryset(self):
#         queryset = Client.objects.all().filter(is_deleted = False)

#         gender = self.request.query_params.get('gender', None)
#         if gender:
#             queryset = queryset.filter(gender = gender)
            
#         total_sales = self.request.query_params.get('total_sales', None)
#         if total_sales:
#                 queryset = queryset.filter(total_sales = total_sales)
                
#         total_done_appointments = self.request.query_params.get('total_done_appointments')
#         if total_done_appointments:
#                 queryset = queryset.filter(total_done_appointments = total_done_appointments)
        
#         data = {
#                     "success": True,
#                     "message": "Client Filter successfully",
#                     "code": "client_filter_API",
#                     "data": queryset
#             }
#         return Response(data, status=status.HTTP_200_success)

        
# class AppointmentFilter(ListAPIView):
        
#         queryset = Appointment.objects.all().filter(is_deleted = False)
#         serializer_class = AppoinmentSerializer
#         filter_backends = [filters.OrderingFilter, filters.SearchFilter]
#         search_fields = ['created_at ','clint']
        
#         def get_queryset(self):
#                 queryset = Appointment.objects.all().filter(is_deleted = False)

#                 start_date = self.request.query_params.get('start_date')
#                 end_date = self.request.query_params.get('end_date')
#                 if start_date and end_date:
#                         date_range_filter = Q(created_at__gte=start_date, created_at__lte=end_date)
#                         queryset = queryset.filter(date_range_filter)
#                 return queryset

# class RunCampaigns():
#     def get_target_client_emails(self, request, pk=None):
#         campaigns = get_object_or_404(Campaign, pk=pk)
#         serialized = CampaignsSerializer(campaigns)
        
#         if campaigns.is_email():
#             target_client_emails = campaigns.segment.client.values_list('email', flat=True)
            
#         elif campaigns.is_appnotifaction():
#             users = 
#             title = campaigns.objects.values('title')
#             body = campaigns.content.values('content')
            
#             NotificationProcessor.send_notifications_to_users(users, title, body, request_user=request.user)

