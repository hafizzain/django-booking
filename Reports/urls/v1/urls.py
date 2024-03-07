from django.urls import path, include

from  Reports.views.v1 import views

urlpatterns = [
    path('get_sales_record/', views.get_sales_record),
    path('get_reports_staff_target/', views.get_reports_staff_target),
    path('get_commission_reports_by_staff/', views.get_commission_reports_by_staff),
    path('get_store_target_report/', views.get_store_target_report),
    
    path('get_commission_reports_by_commission_details/', views.get_commission_reports_by_commission_details_updated),    
    path('get_service_target_report/', views.get_service_target_report),
    path('get_retail_target_report/', views.get_retail_target_report),

    path('get_promotions_and_discounts_sales_list', views.get_promotions_and_discounts_sales_list),
    path('get_promotions_and_discounts_sales_detail', views.get_promotions_and_discounts_sales_detail),
    
    path('get_analytics_optimizedsale-record/', views.get_sales_analytics),
    path('get_product_pos_analytics/', views.get_search_result_analytic),
    # path('get_customer_analytics/', views.get_customer_analytics),

    
]