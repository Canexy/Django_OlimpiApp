from django.apps import AppConfig


class RegisterParConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'register_par'

    def ready(self):
            # Importa e registra las señales
            from . import signals