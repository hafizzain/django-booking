from django.urls import path, include

from  Promotions.views.v1 import views

urlpatterns = [
    path('create_directorflat/', views.create_directorflat),
    path('get_directorflat/', views.get_directorflat),
]