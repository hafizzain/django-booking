from django.urls import path, include

from  Reports.views.v1 import views

urlpatterns = [
    path('get_reports_staff_target/', views.get_reports_staff_target),
    path('get_commission_reports_by_staff/', views.get_commission_reports_by_staff),
    #path('get_commission_reports_by_staff/', views.get_commission_reports_by_staff),
    
]