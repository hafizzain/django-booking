from django.urls import path, include

from Help import views

urlpatterns = [
   path('add_query/', views.add_query),
   path('get_comment/', views.get_comment),
   path('get_comment_details/', views.get_comment_details),
   path('delete_comment/', views.delete_comment),
   path('update_comment/', views.update_comment),
]