"""
SKYNET - Backend de autenticación personalizado
"""

from django.contrib.auth.backends import BaseBackend
from .models import Usuario


class EmailBackend(BaseBackend):
    """
    Backend de autenticación que usa email en lugar de username
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Autenticar usuario usando email y contraseña
        """
        # Si se pasa email directamente
        email = kwargs.get('email', username)

        if email is None or password is None:
            return None

        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return None

        # Verificar contraseña
        if user.check_password(password):
            return user

        return None

    def get_user(self, user_id):
        """
        Obtener usuario por ID
        """
        try:
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None
