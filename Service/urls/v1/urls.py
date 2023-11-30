from django.urls import path, include

from Service.views.v1 import views

urlpatterns = [
    #Employee
    path('get_services/', views.get_services),
    path('get_services_dropdown/', views.get_services_dropdown),


]