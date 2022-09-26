from django.urls import path, include

from Sale.views.v1 import views

urlpatterns = [
    path('create_service/',views.create_service),
    path('get_service/',views.get_service),
    path('delete_service/',views.delete_service),
    path('update_service/',views.update_service),
]