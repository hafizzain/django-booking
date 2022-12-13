from django.urls import path, include

from TragetControl.views.v1 import views

urlpatterns = [
    #Target Staff
    path('get_stafftarget/', views.get_stafftarget),
    path('create_stafftarget/', views.create_stafftarget),
    path('delete_stafftarget/', views.delete_stafftarget),
    
    #Store Target
    path('get_storetarget/', views.get_storetarget),
    path('create_storetarget/', views.create_storetarget),

    

]