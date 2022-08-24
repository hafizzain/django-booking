from django.urls import path, include

from Employee.views.v1 import views
 
urlpatterns = [
    
    #Employee Data
     path('get_employees/', views.get_Employees),
     path('create_employe/', views.create_Employ)
     
 ]