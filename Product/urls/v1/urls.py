
from django.urls import path, include

from Product.views.v1 import views

urlpatterns = [
    # Category Paths 
    path('get_categories/', views.get_categories),
    path('add_category/', views.add_category),
    path('update_category/', views.update_category),
    path('delete_category/', views.delete_category),

    # Brand Paths 
    path('get_brands/', views.get_brands),
    path('add_brand/', views.add_brand),
    path('update_brand/', views.update_brand),
    path('delete_brand/', views.delete_brand),

    # Products Paths 
    path('add_product/', views.add_product),
    path('update_product/', views.update_product),
    path('get_products/', views.get_products),
    path('delete_product/', views.delete_product),
    path('search_product/', views.search_product),

    # Stocks Path 
    path('get_stocks/', views.get_stocks),
    path('delete_stock/', views.delete_stock),
    path('filter_stock/', views.filter_stock),
]
