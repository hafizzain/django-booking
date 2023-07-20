from django.urls import path, include
from MultiLanguage import views

urlpatterns = [
   path('add_language/', views.add_language),
   path('add_section/', views.add_section, name="add_section"),
   path('add_labels/', views.add_labels),
   path('get_data/', views.get_data),
   path('add_invocieTranslation/', views.add_invoiceTranslation),
]

