from django.contrib import admin
from .models import *

@admin.register(HelpContent)
class HelpContentAdmin(admin.ModelAdmin):
    list_display = ['id', 'content', 'parent_comment', 'created_at']