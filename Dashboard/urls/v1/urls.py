from django.urls import path, include

from Dashboard.views.v1 import views

urlpatterns = [
    path('get_busines_client_appointment/', views.get_busines_client_appointment),
    path('get_dashboard_day_wise/', views.get_dashboard_day_wise),
]