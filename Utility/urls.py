
from django.urls import path

from . import views as UtilityViews

urlpatterns = [
    path('get_softwares/', UtilityViews.get_softwares),
    path('get_countries/', UtilityViews.get_countries),
    path('get_states/', UtilityViews.get_states),
    path('get_cities/', UtilityViews.get_cities),
]
