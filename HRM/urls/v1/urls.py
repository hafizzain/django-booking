from django.urls import path, include
from HRM.views import *


urlpatterns = [
    path('holiday-list/', HolidayApiView.as_view()),
    path('holiday/<str:pk>/', HolidayApiView.as_view()),
    path('holiday-create/', HolidayApiView.as_view()),
    path('holiday-update/<str:pk>/', HolidayApiView.as_view()),
    path('holiday-delete/<str:pk>/', HolidayApiView.as_view()),   
]