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
]