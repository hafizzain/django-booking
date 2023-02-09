from django.urls import path, include

from Dashboard.views.v1 import views

urlpatterns = [
    path('get_busines_client_appointment/', views.get_busines_client_appointment),
    path('get_dashboard_day_wise/', views.get_dashboard_day_wise),
    
    #clients
    path('get_appointments_client/', views.get_appointments_client),
    path('get_dashboard_targets/', views.get_dashboard_targets),

]