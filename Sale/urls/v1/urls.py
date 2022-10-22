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
    
]