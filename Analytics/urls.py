from django.urls import path
from . import views


urlpatterns = [
    path('employee_daily_insights/', views.EmployeeDailyInsightsView.as_view())
]