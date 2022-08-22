from django.contrib import admin

from .models import Profile, UserLanguage

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    def username(self, obj):
        try:
            return str(obj.user.username)
        except:
            return 'N/A'
    
    list_display = ['id', 'username']



@admin.register(UserLanguage)
class UserLanguageAdmin(admin.ModelAdmin):
    list_display = ['id', 'language_name', 'is_default']

    def language_name(self, obj):
        try:
            return str(obj.language.name)
        except:
            return 'N/A'