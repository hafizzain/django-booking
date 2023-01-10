
from django.urls import path, include

from  Customer.views.v1 import views

urlpatterns = [
    path('create_client_business/', views.create_client_business),
    path('customer_verify_otp/', views.customer_verify_otp),
    path('customer_login/', views.customer_login),
    path('get_client_appointment/', views.get_client_appointment),
]