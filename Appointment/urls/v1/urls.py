from django.urls import path, include
from Appointment.views.v1 import views

urlpatterns = [
    #Appointment
    path('create_appointment/', views.create_appointment),
    path('get_calendar_appointment/', views.get_calendar_appointment),
    path('get_all_appointments/',views.get_all_appointments),
    path('delete_appointment/', views.delete_appointment),
    path('update_appointment/', views.update_appointment)
    
]