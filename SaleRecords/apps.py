from django.apps import AppConfig


class SalerecordsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'SaleRecords'
    
    def ready(self):
        import SaleRecords.signals
