from django.urls import path, include

from Service.views.v1 import views

urlpatterns = [
    #Employee
    path('get_services/', views.get_services),
]