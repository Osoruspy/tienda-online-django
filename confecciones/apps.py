from django.apps import AppConfig

class ConfeccionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'confecciones'
    verbose_name = 'Confecciones'
    
    def ready(self):
        import confecciones.signals