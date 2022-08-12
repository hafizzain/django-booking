


from django.urls import path, include

from Business.views.v1 import views

urlpatterns = [
    path('get_business_types/', views.get_business_types),
    # path('create_user_business/', views.create_user_business),
    path('get_business/', views.get_business),
    path('get_business_by_domain/', views.get_business_by_domain),
    path('update_business/', views.update_business),

    # Business Theme URLs 
    path('get_business_theme/', views.get_business_theme),
    path('update_business_theme/', views.update_business_theme),


    # Business Location URLs 
    path('<str:business_id>/get_business_locations/', views.get_business_locations),
    path('add_business_location/', views.add_business_location),
    path('delete_location/', views.delete_location),
    path('update_location/', views.update_location),

    # Language URLs 
    
    path('add_business_language/', views.add_business_language),
]
