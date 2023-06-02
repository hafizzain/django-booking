
from django.urls import path, include
from . import views as insightViews
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', insightViews.DashboardPage, name='DashboardPage'),
    path('exception/', insightViews.ExceptionPage, name='ExceptionPage'),
    path('exception-detail/', insightViews.ExceptionDetailPage, name='ExceptionDetailPage'),
    path('language/', insightViews.LanguagePage, name='LanguagePage'),
    path('language/section/', insightViews.LanguageSectionPage, name='LanguageSectionPage'),
    path('language/section-detail', insightViews.LanguageSectionDetailPage, name='LanguageSectionDetailPage'),
]
