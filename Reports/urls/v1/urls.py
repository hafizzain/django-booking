from django.urls import path, include

from  Reports.views.v1 import views

urlpatterns = [
    path('get_reports_staff_target/', views.get_reports_staff_target),
]