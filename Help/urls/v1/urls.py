from django.urls import path, include

from Help import views

urlpatterns = [
   path('add_query/', views.add_query),
   path('get_comment/', views.get_comment),
]