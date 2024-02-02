from django.urls import path, include

from . import views


urlpatterns = [
    path('create_deal/', views.create_deal),
    path('get_all_deals/', views.get_all_deals),
    path('get_single_deal/<str:deal_id>/', views.get_single_deal),
    path('get_deal_category/', views.get_deal_category),

    path('get_deal_audience_choices/', views.get_deal_audience_choices),
    path('get_deal_type_choices/', views.get_deal_type_choices),
    path('get_redeemable_channels/', views.get_redeemable_channels),
    path('get_deal_validity/', views.get_deal_validity),

    
]
