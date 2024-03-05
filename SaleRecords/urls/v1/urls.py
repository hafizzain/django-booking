from django.urls import path
from SaleRecords.views.v1 import views

urlpatterns = [
    path('checkout/', views.SaleRecordViews.as_view(), name= 'checkout'),
    path('sale-history/', views.SaleRecordViews.as_view(), name = 'sale-history'),
    path('single-sale-record/',views.single_sale_record, name='single-sale-record'),
    path('pay-installment/', views.pay_installment, name = 'pay-installment'),
]