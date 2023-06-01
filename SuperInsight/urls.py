
from django.urls import path, include


from . import views as insightViews

urlpatterns = [
    path('admin/', insightViews.DashboardPage),
]