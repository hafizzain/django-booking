from django.urls import path, include

from TragetControl.views.v1 import views

urlpatterns = [
    #Target Staff
    path('get_stafftarget/', views.get_stafftarget),
    path('create_stafftarget/', views.create_stafftarget),
    path('delete_stafftarget/', views.delete_stafftarget),
    path('update_stafftarget/', views.update_stafftarget),
    path('copy_stafftarget/', views.copy_stafftarget),
    
    #Store Target
    path('get_storetarget/', views.get_storetarget),
    path('create_storetarget/', views.create_storetarget),
    path('delete_storetarget/', views.delete_storetarget),
    path('update_storetarget/', views.update_storetarget),
    
    #Service Target
    path('create_servicetarget/', views.create_servicetarget),
    path('get_servicetarget/', views.get_servicetarget),
    path('delete_servicetarget/', views.delete_servicetarget),
    path('update_servicetarget/', views.update_servicetarget),
    path('copy_servicetarget/', views.copy_servicetarget),
    
    #Retail Target
    path('create_retailtarget/', views.create_retailtarget),
    path('get_retailtarget/', views.get_retailtarget),
    path('delete_retailtarget/', views.delete_retailtarget),
    path('update_retailtarget/', views.update_retailtarget),
    path('copy_retailtarget/', views.copy_retailtarget),
]