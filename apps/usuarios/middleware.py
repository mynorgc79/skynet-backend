"""
SKYNET - Middleware JWT personalizado
"""

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin


User = get_user_model()


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware para autenticación JWT personalizado
    """

    def process_request(self, request):
        """
        Procesar la request y verificar el token JWT
        """
        # Obtener el token del header Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

            try:
                # Decodificar el token
                payload = jwt.decode(
                    token, settings.SECRET_KEY, algorithms=['HS256'])

                # Obtener el usuario
                user_id = payload.get('user_id')
                if user_id:
                    try:
                        user = User.objects.get(id=user_id)
                        request.user = user
                    except User.DoesNotExist:
                        pass

            except jwt.ExpiredSignatureError:
                # Token expirado
                pass
            except jwt.InvalidTokenError:
                # Token inválido
                pass

        return None
