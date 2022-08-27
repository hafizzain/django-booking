from django.urls import path, include

from Employee.views.v1 import views

urlpatterns = [
    #Employee
    path('get_employees/', views.get_Employees),
    path('create_employee/', views.create_employee),
    path('delete_employee/', views.delete_employee),
    path('update_employee/', views.update_employee),
    

    #Staff GROUP URLS 
    path('create_staff_group/', views.create_staff_group),
    path('get_staff_group/', views.get_staff_group),
    path('update_staff_group/', views.update_staff_group),
    path('delete_staff_group/', views.delete_staff_group),
    
    #Attendence
    path('create_attendence/', views.create_attendence),
    path('update_attendence/', views.update_attendence),

]