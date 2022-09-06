from django.urls import path, include

from Client.views.v1 import views

urlpatterns = [
    #Client
   path('create_client/',views.create_client), 
   path('get_client/',views.get_client),
   path('update_client/', views.update_client),
   path('delete_client/', views.delete_client),
   path('get_single_client/', views.get_single_client),
   
   #Client_Group
   path('create_client_group/',views.create_client_group),
   path('get_client_group/', views.get_client_group),
   path('update_client_group/', views.update_client_group),
   path('delete_client_group/', views.delete_client_group),
   
   #Subscription
   path('create_subscription/', views.create_subscription),
   path('get_subscription/', views.get_subscription),
   path('delete_subscription/', views.delete_subscription),
   

]