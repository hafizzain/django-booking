from django.urls import path, include
from Appointment.views.v1 import views

urlpatterns = [
    #Appointment
    path('create_appointment/', views.create_appointment),
    path('get_calendar_appointment/', views.get_calendar_appointment),
    path('get_all_appointments/',views.get_all_appointments),
    path('get_today_appointments/', views.get_today_appointments),
    path('get_single_appointments/', views.get_single_appointments),
    path('get_appointments_service/', views.get_appointments_service),
    
    path('get_appointments_device/', views.get_appointments_device),

    path('service_appointment_count/', views.service_appointment_count),
    
    #path('get_single_appointment/', views.get_single_appointment),
    
    path('delete_appointment/', views.delete_appointment),
    path('update_appointment/', views.update_appointment),
    path('update_appointment_service/', views.update_appointment_service),
    #path('update_appointment_device/', views.update_appointment_device),
    
    #block time
    path('create_blockTime/', views.create_blockTime),
    path('update_block_time/', views.update_blocktime),
    path('delete_block_time/', views.delete_block_time),
    #checkout
    path('create_checkout/', views.create_checkout),
    
    #Service Employee
    path('get_service_employee/', views.get_service_employee),
    path('get_employees_for_selected_service/', views.get_employees_for_selected_service),
    
    #Search by client 
    path('get_client_sale/', views.get_client_sale),
    
    #Create Client Book Appointment
    path('create_appointment_client/', views.create_appointment_client),
    
    #Employee Check Availabilty
    path('get_employee_check_time/', views.get_employee_check_time),
    path('get_employee_check_availability_lsit/', views.get_employee_check_availability_lsit),
]