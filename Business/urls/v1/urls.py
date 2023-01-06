


from django.urls import path, include

from Business.views.v1 import views

urlpatterns = [
    path('get_business_types/', views.get_business_types),
    path('create_user_business/', views.create_user_business),
    path('get_business/', views.get_business),
    path('get_business_by_domain/', views.get_business_by_domain),
    path('update_business/', views.update_business),
    path('update_business_additional_information/', views.update_business_additional_information),

    # Business Theme URLs 
    path('get_business_theme/', views.get_business_theme),
    path('update_business_theme/', views.update_business_theme),


    # Business Location URLs 
    path('<str:business_id>/get_business_locations/', views.get_business_locations),
    path('add_business_location/', views.add_business_location),
    path('delete_location/', views.delete_location),
    path('update_location/', views.update_location),

    # Language URLs 

    path('get_all_languages/', views.get_all_languages),
    path('add_business_language/', views.add_business_language),
    path('update_language/', views.update_language),
    path('get_business_languages/', views.get_business_languages),
    path('delete_languages/', views.delete_languages),

    # NOTIFICATION SETTINGS 
    path('get_business_notification_settings/', views.get_business_notification_settings),
    path('update_business_notification_settings/', views.update_business_notification_settings),

    # Booking settings 
    path('get_business_booking_settings/', views.get_business_booking_settings),
    path('update_business_booking_settings/', views.update_business_booking_settings),

    # Payment 
    path('add_payment_method/', views.add_payment_method),
    path('update_payment_method/', views.update_payment_method),
    path('get_business_payment_methods/', views.get_business_payment_methods),
    path('delete_business_payment_methods/', views.delete_business_payment_methods),

    # Business Tax 
    path('add_business_tax/', views.add_business_tax),
    path('update_business_tax/', views.update_business_tax),
    path('get_business_taxes/', views.get_business_taxes),
    path('delete_business_tax/', views.delete_business_tax),

    # Business Vendor 
    path('add_business_vendor/', views.add_business_vendor),
    path('get_business_vendors/', views.get_business_vendors),
    path('update_business_vendor/', views.update_business_vendor),
    path('delete_business_vendor/', views.delete_business_vendor),
    path('search_business_vendor/', views.search_business_vendor),
    path('import_business_vendor/', views.import_business_vendor),
    
    #Business Domain by user
    path('get_domain_business_address/', views.get_domain_business_address),
    path('get_check_availability/', views.get_check_availability),
    path('get_employee_appointment/', views.get_employee_appointment),
    path('create_client_business/', views.create_client_business),
]