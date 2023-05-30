from django.urls import path, include
from Translations import views

urlpatterns = [
   path('add_data/', views.add_data),
   path('get_data/', views.get_data),
]

