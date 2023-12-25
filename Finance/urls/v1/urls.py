from django.urls import path, include
from Finance.views.v1 import views

urlpatterns = [
    path('refunds/', views.RefundAPIView.as_view(), name='refunds'),
]

