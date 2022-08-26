from django.urls import path, include

from Employee.views.v1 import views

urlpatterns = [
    path('get_employees/', views.get_Employees),
    path('create_employee/', views.create_employee),
    path('delete_employee/', views.delete_employee),

    # Staff GROUP URLS 
    path('get_staff_group/', views.delete_employee),

]