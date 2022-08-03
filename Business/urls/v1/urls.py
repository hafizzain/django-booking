


from django.urls import path, include

from Business.views.v1 import views

urlpatterns = [
    path('get_business_types/', views.get_business_types),
]
