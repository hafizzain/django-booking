from django.urls import path
from SaleRecords.views.v1 import views

urlpatterns = [
    path('checkout/', views.SaleRecordViews.as_view(), name= 'checkout')
]