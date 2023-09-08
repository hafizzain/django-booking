from django.apps import AppConfig


class HelpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Help'

    def ready(self):
        import Help.signals