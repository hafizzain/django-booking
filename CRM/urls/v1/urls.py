from django.urls import path, include
from CRM.views.v1.views import *
from Client.views.v1.views import get_client_dropdown

urlpatterns = [
    path('segment-list/', SegmentAPIView.as_view()),
    path('segment/<str:pk>/', SegmentAPIView.as_view()),
    path('segment-create/', SegmentAPIView.as_view()),
    path('segment-update/<str:pk>/', SegmentAPIView.as_view()),
    path('segment-delete/<str:pk>/', SegmentAPIView.as_view()),
    path('campaign-list/', CampaignsAPIView.as_view()),
    path('campaign/<str:pk>/', CampaignsAPIView.as_view()),
    path('campaign-create/', CampaignsAPIView.as_view()),
    path('campaign-update/<str:pk>/', CampaignsAPIView.as_view()),
    path('campaign-delete/<str:pk>/', CampaignsAPIView.as_view()),
    path('client-filter/', get_client_dropdown),
    path('segment-dropdown/', SegmentDropdownAPIView.as_view()),
]