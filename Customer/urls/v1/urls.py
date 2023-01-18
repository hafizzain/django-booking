
from django.urls import path, include

from  Customer.views.v1 import views

urlpatterns = [
    path('create_client_business/', views.create_client_business),
    path('customer_verify_otp/', views.customer_verify_otp),
    path('customer_login/', views.customer_login),
    path('get_client_appointment/', views.get_client_appointment),
    
    #Get Client Id
    path('get_client_detail/', views.get_client_detail),    
    
    #Cancel Appointment
    path('cancel_appointment_client/', views.cancel_appointment_client),
    path('update_appointment_client/', views.update_appointment_client),
    
    #Generate ID 
    path('generate_id_client/', views.generate_id),
    
]