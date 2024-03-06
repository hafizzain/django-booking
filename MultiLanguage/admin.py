from django.contrib import admin
from .models import *

# admin.site.register(Language)
# admin.site.register(Section)
# admin.site.register(Labels)
# admin.site.register(InvoiceTranslation)
# admin.site.register(TranslationLabels)

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['id']
    
@admin.register(Section)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['id']
    
@admin.register(InvoiceTranslation)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['id','taxes','payment_method']