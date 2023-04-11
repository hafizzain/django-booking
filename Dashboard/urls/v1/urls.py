from django.urls import path, include

from Dashboard.views.v1 import views

urlpatterns = [
    path('get_busines_client_appointment/', views.get_busines_client_appointment),
    path('get_dashboard_day_wise/', views.get_dashboard_day_wise),
    
    #clients
    path('get_appointments_client/', views.get_appointments_client),
    path('get_dashboard_targets/', views.get_dashboard_targets),
    path('get_acheived_target_report/', views.get_acheived_target_report),
    path('get_dashboard_target_overview/', views.get_dashboard_target_overview_update),
    path('get_total_comission/', views.get_total_comission),
    path('get_total_tips/', views.get_total_tips),
    path('get_total_sales_device/', views.get_total_sales_device),
    path('get_dashboard_footfalls/', views.get_dashboard_footfalls),

    

]