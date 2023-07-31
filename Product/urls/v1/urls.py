
from django.urls import path, include

from Product.views.v1 import views, insights

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
    path('search_brand/', views.search_brand),
    path('import_brand/', views.import_brand),
    

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

    #Export CSV files
    path('export_csv/', views.export_csv, name='export_csv'),
    path('import_product/', views.import_product, name='import_product'),
    path('import_category/', views.import_category),
    # path('UploadFileView/', views.UploadFileView, )
    
    #Order Stocks
    path('create_orderstock/', views.create_orderstock),
    path('get_orderstock/', views.get_orderstock),
    path('update_orderstock/', views.update_orderstock),
    path('delete_orderstock/', views.delete_orderstock),
    
    #Update stockproduct order
    path('update_orderstockproduct/', views.update_orderstockproduct),    

    path('add_product_consumption/', views.add_product_consumption),
    path('get_product_consumptions/', views.get_product_consumptions),
    path('update_product_consumptions/', views.update_product_consumptions),
    path('delete_product_consumption/', views.delete_product_consumptions),
    

    path('add_product_stock_transfer/', views.add_product_stock_transfer),
    path('get_product_stock_transfers/', views.get_product_stock_transfers),
    path('delete_product_stock_transfer/', views.delete_product_stock_transfer),
    path('update_product_stock_transfer/', views.update_product_stock_transfer),
    
    #Inventory Reports
    path('get_product_stock_report/', views.get_product_stock_report),

    # Insights 
    path('get_filtered_insight_products/', insights.FilteredInsightProducts.as_view()),
    path('get_filtered_insight_chart_products/', insights.get_filtered_chat_products),
    
    #Testing Api
    path('get_test_api/', views.get_test_api)
]
