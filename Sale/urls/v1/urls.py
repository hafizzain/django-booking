from django.urls import path, include

from Sale.views.v1 import views

urlpatterns = [
    path('create_service/',views.create_service),
    path('get_service/',views.get_service),
    path('delete_service/',views.delete_service),
    path('update_service/',views.update_service),
    
    #Order Sale
    path('create_sale_order/', views.create_sale_order),
    
    path('get_product_orders/', views.get_product_orders),
    path('get_service_orders/', views.get_service_orders),
    path('get_membership_orders/', views.get_membership_orders),
    path('get_voucher_orders/', views.get_voucher_orders),
    
    path('get_all_sale_orders/', views.get_all_sale_orders),
    path('get_total_revenue/', views.get_total_revenue),
    
    #Service Group
    path('create_servicegroup/', views.create_servicegroup),
    path('get_servicegroup/', views.get_servicegroup),
    path('delete_servicegroup/', views.delete_servicegroup),
    path('update_servicegroup/', views.update_servicegroup),
    
    #CheckOut
    path('get_sale_checkout/', views.get_sale_checkout),
]