
from django.urls import path, include

from Product.views.v1 import views

urlpatterns = [
    # Category Paths 
    path('get_categories/', views.get_categories),
    path('add_category/', views.add_category),

    # Brand Paths 
    path('get_brands/', views.get_brands),
    path('add_brand/', views.add_brand),

    # Products Paths 
    path('add_product/', views.add_product),
    path('update_product/', views.update_product),
    path('get_products/', views.get_products),
    path('delete_product/', views.get_products),

]
