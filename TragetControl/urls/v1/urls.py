from django.urls import path, include

from TragetControl.views.v1 import views

urlpatterns = [
    #Target Staff
    path('get_single_employee/', views.get_single_employee),

]