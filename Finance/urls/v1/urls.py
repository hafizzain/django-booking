from django.urls import path, include
from Finance.views.v1 import views

urlpatterns = [
    path('refunds/', views.RefundAPIView.as_view(), name='refunds'),
    path('get-all-refunds/', views.RefundAPIView.as_view(),name='get-all-refunds'),
    path('get-all-refund-coupons/', views.RefundedCoupons.as_view(), name='get-all-refund-coupons')
]

