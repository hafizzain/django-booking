from django.urls import path, include

from  Promotions.views.v1 import views

urlpatterns = [
    #Flatordirect
    path('create_directorflat/', views.create_directorflat),
    path('get_directorflat/', views.get_directorflat),
    path('delete_directorflat/', views.delete_directorflat),
    path('update_directorflat/', views.update_directorflat),
    
    #Specific Group Category
    path('create_specificgroupdiscount/', views.create_specificgroupdiscount),
    path('update_specificgroupdiscount/', views.update_specificgroupdiscount),
    path('delete_specificgroupdiscount/', views.delete_specificgroupdiscount),
    path('get_specificgroupdiscount/', views.get_specificgroupdiscount),
    
    #PurchaseDiscount
    path('get_purchasediscount/', views.get_purchasediscount),
    path('create_purchasediscount/', views.create_purchasediscount),
    path('update_purchasediscount/', views.update_purchasediscount),
    path('delete_purchasediscount/', views.delete_purchasediscount),
    
    #Specific Brand and Service Group
    path('create_specificbrand_discount/', views.create_specificbrand_discount),
    path('delete_specificbrand_discount/', views.delete_specificbrand_discount),
    path('get_specificbrand_discount/', views.get_specificbrand_discount),
    path('update_specificbrand_discount/', views.update_specificbrand_discount),
    
    #Spend and Get Discount
    path('create_spend_discount/', views.create_spend_discount),
    path('update_spend_discount/', views.update_spend_discount),
    path('delete_spend_discount/', views.delete_spend_discount),
    path('get_spend_discount/', views.get_spend_discount),
    
    #Some Amount Discount
    path('create_spend_some_amount/', views.create_spend_some_amount),
    path('update_spend_some_amount/', views.update_spend_some_amount),
    path('delete_spend_some_amount/', views.delete_spend_some_amount),
    path('get_spend_some_amount/', views.get_spend_some_amount),
    
    #Fixed price or in the group
    path('create_fixed_price_service/', views.create_fixed_price_service),
    path('update_fixed_price_service/', views.update_fixed_price_service),
    path('delete_fixed_price_service/', views.delete_fixed_price_service),
]