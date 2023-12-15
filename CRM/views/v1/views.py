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

from Client.models import Client
from Business.models import Business
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
            if no_pagination:
                segment = Segment.objects.all().filter(is_deleted=False)
                serializer = SegmentSerializer(segment, many=True)
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
                segment = Segment.objects.all().filter(is_deleted=False)
                paginator = self.pagination_class()
                result_page = paginator.paginate_queryset(segment, request)
                serializer = SegmentSerializer(result_page, many=True)
                data = {
                        'count': paginator.page.paginator.count,
                        'next': paginator.get_next_link(),
                        'previous': paginator.get_previous_link(),
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
        return self.update_segment(request, pk)
    
    def update_segment(self, request, pk):
        segment = get_object_or_404(id=pk)
        serializer = SegmentSerializer(segment, data=request.data)
        if not segment.is_static():
            if serializer.is_valid():
                serializer.save()
                data = {
                    "success": True,
                    "status_code" : 200,
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
    def destroy(self, request, pk):
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


class CampaignsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    page_size = 10
    
    def get(self, request , pk=None):
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
            campaigns = Campaign.objects.all().filter(is_deleted=False)
            serialized = CampaignsSerializer(campaigns, many=True)
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
          
    @transaction.atomic
    def post(self, request):
        serializer = CampaignsSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            data = {
                    "success": True,
                    "status_code" : 200,
                    "response" : {
                        "message" : "campaign created successfully",
                        "error_message" : None,
                        "data" : serializer.data
                    }
            }
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:   
            data = {
                    "success": False,
                    "status_code" : 400,
                    "response" : {
                        "message" : "campaign not created",
                        "error_message" : serializer.errors,
                        "data" : None
                    }
                }
            return Response(data, status=status.HTTP_400_BAD_REQUEST) 

    @transaction.atomic
    def put(self, request, pk):
        return self.update_campaign(request, pk)
      
    def update_campaign(self, request, pk):
        campaign = get_object_or_404(Campaign,id=pk)
        serializer = CampaignsSerializer(campaign, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                    "success": True,
                    "status_code" : 200,
                    "response" : {
                        "message" : "campaign updated successfully",
                        "error_message" : None,
                        "data" : serializer.data
                    }
                }
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:    
            data = {
                    "success": False,
                    "status_code" : 400,
                    "response" : {
                        "message" : "campaign not updated",
                        "error_message" : serializer.errors,
                        "data" : None
                    }
                }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        
    @transaction.atomic   
    def destroy(self, request, pk):
        campaign = get_object_or_404(Campaign, id=pk)
        campaign.is_deleted = True
        campaign.save() 
        data = {
                "success": True,
                "status_code" : 200,
                "response" : {
                    "message" : "campaign deleted successfully",
                    "error_message" : None,
                    "data" : None
                }
            }
        return Response(data, status=status.HTTP_200_OK)

        
class RunCampaign(APIView):
    def check_campaign(self,request,pk=None):
        campaign = get_object_or_404(Campaign, id=pk)
        serialized = CampaignsSerializer(campaign)
        if campaign.is_start_date() and campaign.is_end_date():
            if campaign.is_email():
                email = list(Campaign.objects \
                        .filter(id=pk) \
                        .values_list(
                            'segment__client__email',
                        )
                    )
                content = Campaign.objects \
                        .filter(id=pk) \
                        .values_list(
                            'content',
                        )
                title = Campaign.objects \
                        .filter(id=pk) \
                        .values_list(
                            'title',
                        )
                email_campaign = EmailMultiAlternatives(
                                title,
                                content,
                                settings.EMAIL_HOST_USER,
                                to = [email],                           
                            )
                email_campaign.send()