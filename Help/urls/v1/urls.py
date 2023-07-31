from django.urls import path, include

from Help import views

urlpatterns = [
   # path('add_query/', views.add_query),
   path('get_comment/', views.get_comment),
   path('get_comment_details/', views.get_comment_details),
   # path('delete_comment/', views.delete_comment),
   # path('update_comment/', views.update_comment),
   path('view_content/', views.view_content, name='view_content'),
   path('add_content/', views.add_content),
   path('add_topic_content/', views.add_topic_content),
   path('view_topic_content/', views.view_topic_content),

]