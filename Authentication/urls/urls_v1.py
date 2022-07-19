
from django.urls import path, include

from ..views import views_v1

urlpatterns = [
    path('create_user/', views_v1.create_user )
]
