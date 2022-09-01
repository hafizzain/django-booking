from django.urls import path, include

from Client.views.v1 import views

urlpatterns = [
   path('create_client/',views.create_client)
]