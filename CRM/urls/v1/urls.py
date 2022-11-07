from django.urls import path, include

from CRM.views.v1 import views

urlpatterns = [
    #Segment
    path('create_segment/', views.create_segment),
    path('get_segment/', views.get_segment),
    path('delete_segment/', views.delete_segment),
    path('update_segment/', views.update_segment),
]