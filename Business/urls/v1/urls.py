


from django.urls import path, include

from Business.views.v1 import views

urlpatterns = [
    path('get_business_types/', views.get_business_types),
    # path('create_user_business/', views.create_user_business),
    path('get_business/', views.get_business),
    path('update_business/', views.update_business),
]
