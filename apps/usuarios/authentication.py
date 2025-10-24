"""
SKYNET - Autenticación JWT Personalizada
"""

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions

User = get_user_model()


class JWTAuthentication(authentication.BaseAuthentication):
    """
    Autenticación JWT personalizada para Django REST Framework
    """
    authentication_header_prefix = 'Bearer'

    def authenticate(self, request):
        """
        Autentica la request usando JWT token
        """
        request.user = None

        # Obtener el header de autorización
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            return None

        if len(auth_header) == 1:
            # Token inválido, no debe tener espacios
            return None

        elif len(auth_header) > 2:
            # Token inválido, no debe tener más de dos elementos
            return None

        # Decode del prefix y token
        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            # El prefix del token no coincide
            return None

        # Intentar autenticar con las credenciales proporcionadas
        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        """
        Intenta autenticar las credenciales dadas.
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
        except jwt.InvalidTokenError:
            msg = 'Token de autenticación inválido.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get(pk=payload['user_id'])
        except User.DoesNotExist:
            msg = 'No se encontró el usuario correspondiente al token.'
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = 'La cuenta del usuario ha sido desactivada.'
            raise exceptions.AuthenticationFailed(msg)

        return (user, token)
