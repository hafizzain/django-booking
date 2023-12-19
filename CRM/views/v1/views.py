import json
from threading import Thread
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from rest_framework.authentication import SessionAuthentication

from CRM.models import *
from CRM.serializers import *
from NStyle.Constants import StatusCodes
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from Notification.notification_processor import NotificationProcessor
from Utility.models import NstyleFile


class SegmentAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    page_size = 10
    
    queryset = Segment.objects.prefetch_related('client') \
                            .select_related('user', 'business') \
                            .filter(is_deleted=False) \
                            .order_by('-created_at')
                            
    serializer_class = SegmentSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'segment_type', 'is_active']
    
    def get(self, request , pk=None):
        no_pagination = request.GET.get('no_pagination', None)
        
        if pk is not None:
            segment = get_object_or_404(Segment, id=pk)
            serializer = SegmentSerializer(segment)
            data = {
                    "success": True,
                    "status_code" : 200,
                    "response" : {
                        "message" : "Segment get Successfully",
                        "error_message" : None,
                        "data" : serializer.data
                    }
                }
            return Response(data, status=status.HTTP_200_OK)
        else:
            filtered_queryset = Segment.objects.all() \
                            .filter(is_deleted=False) \
                            .order_by('-created_at')
                            
            name = self.request.query_params.get('search_text', None)
            if name:
                filtered_queryset = filtered_queryset.filter(name__icontains=name)

            segment_type = self.request.query_params.get('segment_type', None)
            if segment_type:
                filtered_queryset = filtered_queryset.filter(segment_type=segment_type)

            is_active = self.request.query_params.get('is_active', None)
            if is_active:
                filtered_queryset = filtered_queryset.filter(is_active=is_active)
              
            if no_pagination:
                serializer = SegmentSerializer(filtered_queryset, many=True)
                data = {
                        "success": True,
                        "status_code" : 200,
                        "response" : {
                            "message" : "Segment get Successfully",
                            "error_message" : None,
                            "data" : serializer.data
                        }
                    }
                return Response(data, status=status.HTTP_200_OK)
            else:
                paginator = self.pagination_class()
                result_page = paginator.paginate_queryset(filtered_queryset, request)
                serializer = SegmentSerializer(result_page, many=True)
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
                            "message" : "Segment get Successfully",
                            "error_message" : None,
                            "data" : serializer.data
                        }
                    }
                return Response(data, status=status.HTTP_200_OK)
             
    @transaction.atomic       
    def post(self, request):
        user = request.user
        request.data['user'] = user.id
        name = request.data.get('name', None)
        
        if Segment.objects.filter(name=name, is_deleted=False).exists():
            data = {
                    "success": False,
                    "status_code" : 200,
                    "response" : {
                        "message" : "Segment with this name already exist",
                        "error_message" : None,
                        "data" : None
                    }
                }
            return Response(data, status=status.HTTP_200_OK)
        
        serializer = SegmentSerializer(data=request.data,
                                       context={'request': request})
        if serializer.is_valid():
            serializer.save()
            data = {
                    "status" : True,
                    "status_code" : 201,
                    "response" : {
                        "message" : "Segment created successfully",
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
                        "message" : "Segment not created",
                        "error_message" : serializer.errors,
                        "data" : None
                    }
                }
            return Response(data, status=status.HTTP_400_BAD_REQUEST) 

    @transaction.atomic
    def put(self, request, pk):
        segment = get_object_or_404(Segment, id=pk)
        serializer = SegmentSerializer(segment, data=request.data)
        if not segment.is_static():
            if serializer.is_valid():
                serializer.save()
                data = {
                    "success": True,
                    "status_code" : 201,
                    "response" : {
                        "message" : "Segment updated successfully",
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
                            "message" : "Segment not updated",
                            "error_message" : serializer.errors,
                            "data" : None
                        }
                    }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
                data = {
                        "success": False,
                        "status_code" : 400,
                        "response" : {
                            "message" : "Segment not updated",
                            "error_message" : "Segment type is static",
                            "data" : None
                        }
                    }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def delete(self, request, pk):
        segment = get_object_or_404(Segment, id=pk)
        segment.is_deleted = True
        segment.save() 
        data = {
                "success": True,
                "status_code" : 200,
                "response" : {
                    "message" : "Segment deleted successfully",
                    "error_message" : None,
                    "data" : None
                }
            }
        return Response(data, status=status.HTTP_200_OK)


class SegmentDropdownAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    page_size = 10
    
    queryset = Segment.objects.prefetch_related('client') \
                            .select_related('user', 'business') \
                            .filter(is_deleted=False) \
                            .order_by('-created_at')
    
    serializer_class = SegmentDropdownSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name']
    
    def get(self, request):
        is_search = False
        filtered_queryset = Segment.objects.filter(is_deleted=False) \
                            .order_by('-created_at')
                            
        name = self.request.query_params.get('search_text', None)
        if name:
            filtered_queryset = filtered_queryset.filter(name__icontains=name)
            is_search = True
            
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(filtered_queryset, request)
        serializer = SegmentDropdownSerializer(result_page, many=True)
        data = {
                
                'count': paginator.page.paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'current_page': paginator.page.number,
                'per_page': self.page_size,
                'total_pages': paginator.page.paginator.num_pages,
                "success": True,
                "status_code" : 200,
                'is_search': is_search,
                "response" : {
                    "message" : "Segment get Successfully",
                    "error_message" : None,
                    "data" : serializer.data,
                    
                }
            }
        return Response(data, status=status.HTTP_200_OK)
                        

@permission_classes([IsAuthenticated])                       
class CampaignsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    page_size = 10
    
    queryset =  Campaign.objects.select_related('user', 'segment') \
                            .order_by('-created_at')
                            
    serializer_class = CampaignsSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'campaign_type', 'is_active']
    
    def get(self, request , pk=None):
        no_pagination = request.GET.get('no_pagination', None)
        
        if pk is not None:
            campaign = get_object_or_404(Campaign, id=pk)
            serialized = CampaignsSerializer(campaign)
            data = {
                    "success": True,
                    "status_code" : 200,
                    "response" : {
                        "message" : "Campaign get Successfully",
                        "error_message" : None,
                        "data" : serialized.data
                    }
                }
            return Response(data, status=status.HTTP_200_OK)
        else:
            query = Q()
            
            title = self.request.query_params.get('search_text', None)
            if title:
                query &= Q(title__icontains=title)
            
            campaign_type = self.request.query_params.get('campaign_type', None)
            if campaign_type:
                query &= Q(campaign_type=campaign_type)
                
            is_active = self.request.query_params.get('is_active', None)
            if is_active:
                query &= Q(is_active=is_active)
            
            filtered_queryset = Campaign.objects.filter(query) \
                            .order_by('-created_at')
            serialized = CampaignsSerializer(filtered_queryset, many=True)    
            if no_pagination:    
                data = {
                        "success": True,
                        "status_code" : 200,
                        "response" : {
                            "message" : "Campaign get Successfully",
                            "error_message" : None,
                            "data" : serialized.data
                        }
                    }
                return Response(data, status=status.HTTP_200_OK) 
            else:
                paginator = self.pagination_class()
                result_page = paginator.paginate_queryset(filtered_queryset, request)
                serializer = CampaignsSerializer(result_page, many=True)
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
                            "message" : "Campaign get Successfully",
                            "error_message" : None,
                            "data" : serializer.data
                        }
                    }
                return Response(data, status=status.HTTP_200_OK)
            
    @transaction.atomic
    def post(self, request):
        user = request.user
        request.data['user'] = user.id
        
        title = request.data.get('title', None)
        if Campaign.objects.filter(title=title, is_deleted=False).exists():
            data = {
                "success": False,
                "status_code": 200,
                "response": {
                    "message": "Campaign with this title already exists",
                    "error_message": None,
                    "data": None
                }
            }
            return Response(data, status=status.HTTP_200_OK)

        # If the campaign with the title does not exist, proceed with creating a new campaign
        serializer = CampaignsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            data = {
                "success": True,
                "status_code": 201,
                "response": {
                    "message": "Campaign created successfully",
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
                    "message": "Campaign not created",
                    "error_message": serializer.errors,
                    "data": None
                }
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def put(self, request, pk):
        campaign = get_object_or_404(Campaign, id=pk)
        serializer = CampaignsSerializer(campaign, data=request.data)
        title = request.data.get('title')
        if Campaign.objects.filter(title=title, id=pk).exists():
            if serializer.is_valid():
                serializer.save()
                data = {
                        "success": True,
                        "status_code" : 201,
                        "response" : {
                            "message" : "Campaign updated successfully",
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
                            "message" : "Campaign not updated",
                            "error_message" : serializer.errors,
                            "data" : None
                        }
                    }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data = {
                    "success": False,
                    "status_code" : 201,
                    "response" : {
                        "message" : "Campaign with this title already exist",
                        "error_message" : None,
                        "data" : None
                    }
                }
            return Response(data, status=status.HTTP_200_OK)
        
    @transaction.atomic   
    def delete(self, request, pk):
        campaign = get_object_or_404(Campaign, id=pk)
        campaign.delete()
        data = {
                "success": True,
                "status_code" : 200,
                "response" : {
                    "message" : "Campaign deleted successfully",
                    "error_message" : None,
                    "data" : None
                }
            }
        return Response(data, status=status.HTTP_200_OK)


# class RunCampaign(APIView):
#     def check_campaign(self,request,pk=None):
#         campaign = get_object_or_404(Campaign, id=pk)
#         serialized = CampaignsSerializer(campaign)
#         if campaign.is_start_date() and campaign.is_past_end_date():
#             if campaign.is_email():
#                 email = list(Campaign.objects \
#                         .filter(id=pk) \
#                         .values_list(
#                             'segment__client__email', flat=True
#                         )
#                     )
#                 content = Campaign.objects \
#                         .filter(id=pk) \
#                         .values(
#                             'content',
#                         )
#                 title = Campaign.objects \
#                         .filter(id=pk) \
#                         .values(
#                             'title',
#                         )
#                 email_campaign = EmailMultiAlternatives(
#                                 title,
#                                 content,
#                                 settings.EMAIL_HOST_USER,
#                                 to = [email],                           
#                             )
#                 email_campaign.send()