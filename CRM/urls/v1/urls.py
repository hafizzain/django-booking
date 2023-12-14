from django.urls import path, include
from CRM.views.v1.views import *
from Client.views.v1.views import get_client_dropdown

urlpatterns = [
    path('segment-list/', Segment.as_view()),
    path('segment/<str:id>/', Segment.as_view()),
    path('segment-create', Segment.as_view()),
    path('segment-update/<str:id>/', Segment.as_view()),
    path('segment-delete/<str:id>/', Segment.as_view()),
    path('campaign-list/', Campaigns.as_view()),
    path('campaign/<str:id>/', Campaigns.as_view()),
    path('campaign-create', Campaigns.as_view()),
    path('campaign-update/<str:id>/', Campaigns.as_view()),
    path('campaign-delete/<str:id>/', Campaigns.as_view()),
    path('client-filter/', get_client_dropdown)
   
]