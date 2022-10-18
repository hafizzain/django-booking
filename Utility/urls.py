
from django.urls import path

from . import views as UtilityViews

urlpatterns = [
    path('get_softwares/', UtilityViews.get_softwares),
    path('get_countries/', UtilityViews.get_countries),
    path('get_states/', UtilityViews.get_states),
    path('get_cities/', UtilityViews.get_cities),
    path('get_tenants_product/', UtilityViews.get_tenants_product),
    path('get_all_currencies/', UtilityViews.get_all_currencies),

    path('get_user_locations_data/', UtilityViews.get_user_locations_data),
]
