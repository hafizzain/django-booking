from django.urls import path, include

from Client.views.v1 import views

urlpatterns = [
   path('create_client/',views.create_client), 
   path('get_client/',views.get_client),
   path('update_client/', views.update_client),
   path('delete_client/', views.delete_client),

]