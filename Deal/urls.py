from django.urls import path, include

from . import views


urlpatterns = [
    # Employee
    path('create_deal/', views.create_deal),
    
]
