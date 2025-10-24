"""
SKYNET - Configuración de la app usuarios
"""

from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.usuarios'
    verbose_name = 'Usuarios'

    def ready(self):
        """
        Importar señales cuando la app esté lista
        """
        try:
            import apps.usuarios.signals
        except ImportError:
            pass
