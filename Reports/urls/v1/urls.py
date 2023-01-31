from django.urls import path, include

from  Reports.views.v1 import views

urlpatterns = [
    path('get_reports_staff_target/', views.get_reports_staff_target),
    path('get_commission_reports_by_staff/', views.get_commission_reports_by_staff),
    path('get_store_target_report/', views.get_store_target_report),
    
    path('get_commission_reports_by_commission_details/', views.get_commission_reports_by_commission_details),
    
    path('get_service_target_report/', views.get_service_target_report),
    #path('get_retail_target_report/', views.get_retail_target_report),
    
]