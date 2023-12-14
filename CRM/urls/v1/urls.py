from django.urls import path, include
from CRM.views.v1.views import *
from Client.views.v1.views import get_client_dropdown

urlpatterns = [
    path('segment-list/', SegmentAPIView.as_view()),
    path('segment/<str:id>/', SegmentAPIView.as_view()),
    path('segment-create', SegmentAPIView.as_view()),
    path('segment-update/<str:id>/', SegmentAPIView.as_view()),
    path('segment-delete/<str:id>/', SegmentAPIView.as_view()),
    path('campaign-list/', CampaignsAPIView.as_view()),
    path('campaign/<str:id>/', CampaignsAPIView.as_view()),
    path('campaign-create', CampaignsAPIView.as_view()),
    path('campaign-update/<str:id>/', CampaignsAPIView.as_view()),
    path('campaign-delete/<str:id>/', CampaignsAPIView.as_view()),
    path('client-filter/', get_client_dropdown)
   
]