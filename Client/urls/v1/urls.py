from django.urls import path, include

from Client.views.v1 import views

urlpatterns = [
    #Client
   path('create_client/',views.create_client), 
   path('get_client/',views.get_client),
   path('update_client/', views.update_client),
   path('delete_client/', views.delete_client),
   path('get_single_client/', views.get_single_client),
   path('import_client/', views.import_client),
   
   #Client_Group
   path('create_client_group/',views.create_client_group),
   path('get_client_group/', views.get_client_group),
   path('update_client_group/', views.update_client_group),
   path('delete_client_group/', views.delete_client_group),
   
   #Subscription
   path('create_subscription/', views.create_subscription),
   path('get_subscription/', views.get_subscription),
   path('delete_subscription/', views.delete_subscription),
   path('update_subscription/', views.update_subscription),
   
   #Rewards
   path('create_rewards/', views.create_rewards),
   path('get_rewards/', views.get_rewards),
   path('delete_rewards/', views.delete_rewards),
   path('update_rewards/', views.update_rewards),
   
   #Promotion
   path('create_promotion/', views.create_promotion),
   path('get_promotion/', views.get_promotion),
   path('delete_promotion/', views.delete_promotion),
   path('update_promotion/', views.update_promotion),
   
   #Membership
   path('create_memberships/', views.create_memberships),
   path('get_memberships/', views.get_memberships),
   path('delete_memberships/', views.delete_memberships),
   path('update_memberships/', views.update_memberships),
   
   #Vouchers
   path('create_vouchers/', views.create_vouchers),
   path('get_vouchers/', views.get_vouchers),
   path('delete_vouchers/', views.delete_vouchers),
   path('update_vouchers/', views.update_vouchers),
   
   #Generate ID 
   path('generate_id/', views.generate_id),
   
]