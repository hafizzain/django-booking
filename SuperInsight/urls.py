
from django.urls import path, include
from . import views as insightViews
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', insightViews.DashboardPage),
]

urlpatterns+= static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
urlpatterns+= static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)