from django.contrib import admin

# Register your models here.

from .models import Campaign, Segment


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'content', 'start_date', 'end_date', 'campaign_type', 'segment', 'user']
    search_fields = ['title', 'content']
    ordering = ['id']
    
@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'segment_type', 'description', 'user', 'business']
    search_fields = ['name', 'description']
    ordering = ['id']