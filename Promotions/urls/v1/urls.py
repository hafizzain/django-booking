from django.urls import path, include

from  Promotions.views.v1 import views

urlpatterns = [
    #Flatordirect
    path('create_directorflat/', views.create_directorflat),
    path('get_directorflat/', views.get_directorflat),
    path('delete_directorflat/', views.delete_directorflat),
    path('update_directorflat/', views.update_directorflat),
    
    #Specific Group Category
    path('create_directorflat/', views.create_specificgroupdiscount),
    path('create_directorflat/', views.update_specificgroupdiscount),
    path('delete_specificgroupdiscount/', views.delete_specificgroupdiscount),
    
    #PurchaseDiscount
    path('create_purchasediscount/', views.create_purchasediscount),
    
]