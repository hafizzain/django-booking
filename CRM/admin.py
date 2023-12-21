from django.contrib import admin

# Register your models here.

from .models import Campaign, Segment


admin.site.register(Campaign)
admin.site.register(Segment)