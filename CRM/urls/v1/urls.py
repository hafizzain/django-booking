from django.urls import path, include
from CRM.views.v1.views import *
from Client.views.v1.views import get_client_dropdown


urlpatterns = [
    path('segment-list/', Segment.as_view()),
    path('segment/<str:id>/', Segment.as_view()),
    path('segment-create', Segment.as_view()),
    path('segment-update/<str:id>/update/', Segment.as_view()),
    path('segment-delete/<str:id>/delete/', Segment.as_view()),
    path('campaing-list/', Campaigns.as_view()),
    path('campaing/<str:id>/', Campaigns.as_view()),
    path('campaing-create', Campaigns.as_view()),
    path('campaing-update/<str:id>/update/', Campaigns.as_view()),
    path('campaing-delete/<str:id>/delete/', Campaigns.as_view()),
    path('client-filter/', get_client_dropdown)
   
]