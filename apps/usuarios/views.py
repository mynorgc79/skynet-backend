"""
SKYNET - Vistas para el módulo de usuarios
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import logout
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Usuario
from .serializers import (
    LoginSerializer,
    UsuarioSerializer,
    ChangePasswordSerializer
)


# class CustomTokenObtainPairView(TokenObtainPairView):
#     """
#     Vista personalizada para obtener JWT tokens
#     """
#     serializer_class = CustomTokenObtainPairSerializer

#     def post(self, request, *args, **kwargs):
#         response = super().post(request, *args, **kwargs)

#         if response.status_code == 200:
#             # Formato de respuesta estándar
#             return Response({
#                 'success': True,
#                 'data': response.data,
#                 'message': 'Inicio de sesión exitoso',
#                 'errors': []
#             }, status=status.HTTP_200_OK)
#         else:
#             return Response({
#                 'success': False,
#                 'data': None,
#                 'message': 'Error en el inicio de sesión',
#                 'errors': ['Email o contraseña incorrectos']
#             }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    operation_description="Iniciar sesión con email y contraseña",
    operation_summary="Login de Usuario",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email', 'password'],
        properties={
            'email': openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                description='Email del usuario'
            ),
            'password': openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_PASSWORD,
                description='Contraseña del usuario'
            ),
        },
        example={
            'email': 'usuario@example.com',
            'password': 'mi_password123'
        }
    ),
    responses={
        200: openapi.Response(
            description="Login exitoso",
            examples={
                "application/json": {
                    "success": True,
                    "data": {
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "user": {
                            "id": 1,
                            "email": "usuario@example.com",
                            "nombre": "Juan",
                            "apellido": "Pérez",
                            "nombre_completo": "Juan Pérez",
                            "rol": "ADMINISTRADOR",
                            "activo": True
                        }
                    },
                    "message": "Inicio de sesión exitoso",
                    "errors": []
                }
            }
        ),
        400: openapi.Response(
            description="Error en el login",
            examples={
                "application/json": {
                    "success": False,
                    "data": None,
                    "message": "Error en el inicio de sesión",
                    "errors": ["Email o contraseña incorrectos"]
                }
            }
        )
    },
    tags=['Autenticación']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Vista alternativa para login usando serializer personalizado
    """
    serializer = LoginSerializer(
        data=request.data, context={'request': request})

    if serializer.is_valid():
        user = serializer.validated_data['user']

        # Generar tokens JWT manualmente
        import jwt
        from django.conf import settings
        from datetime import datetime, timedelta

        # Payload del access token
        access_payload = {
            'user_id': user.id,
            'email': user.email,
            'nombre': user.nombre,
            'apellido': user.apellido,
            'rol': user.rol,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow(),
            'token_type': 'access'
        }

        # Payload del refresh token
        refresh_payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=7),
            'iat': datetime.utcnow(),
            'token_type': 'refresh'
        }

        # Generar tokens
        access_token = jwt.encode(
            access_payload, settings.SECRET_KEY, algorithm='HS256')
        refresh_token = jwt.encode(
            refresh_payload, settings.SECRET_KEY, algorithm='HS256')

        return Response({
            'success': True,
            'data': {
                'access': access_token,
                'refresh': refresh_token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'nombre': user.nombre,
                    'apellido': user.apellido,
                    'nombre_completo': user.nombre_completo,
                    'rol': user.rol,
                    'activo': user.activo,
                }
            },
            'message': 'Inicio de sesión exitoso',
            'errors': []
        }, status=status.HTTP_200_OK)

    return Response({
        'success': False,
        'data': None,
        'message': 'Error en el inicio de sesión',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Vista para cerrar sesión (simple)
    """
    try:
        # Por ahora solo confirmamos el logout
        # En el futuro se implementará blacklist de tokens

        return Response({
            'success': True,
            'data': None,
            'message': 'Sesión cerrada exitosamente',
            'errors': []
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'data': None,
            'message': 'Error al cerrar sesión',
            'errors': [str(e)]
        }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    operation_description="Obtener información del usuario autenticado",
    operation_summary="Mi Perfil",
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer token",
            type=openapi.TYPE_STRING,
            required=True,
            default="Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        )
    ],
    responses={
        200: openapi.Response(
            description="Información del usuario",
            examples={
                "application/json": {
                    "success": True,
                    "data": {
                        "id": 1,
                        "email": "usuario@example.com",
                        "nombre": "Juan",
                        "apellido": "Pérez",
                        "nombre_completo": "Juan Pérez",
                        "telefono": "12345678",
                        "rol": "ADMINISTRADOR",
                        "activo": True,
                        "fecha_creacion": "2025-10-23T10:00:00Z",
                        "fecha_actualizacion": "2025-10-23T10:00:00Z"
                    },
                    "message": "Información del usuario obtenida exitosamente",
                    "errors": []
                }
            }
        ),
        401: openapi.Response(
            description="No autorizado",
            examples={
                "application/json": {
                    "detail": "Authentication credentials were not provided."
                }
            }
        )
    },
    tags=['Usuario']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """
    Vista para obtener información del usuario autenticado
    """
    serializer = UsuarioSerializer(request.user)
    return Response({
        'success': True,
        'data': serializer.data,
        'message': 'Información del usuario obtenida exitosamente',
        'errors': []
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='put',
    operation_description="Cambiar contraseña del usuario autenticado",
    operation_summary="Cambiar Contraseña",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['old_password', 'new_password', 'confirm_password'],
        properties={
            'old_password': openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_PASSWORD,
                description='Contraseña actual'
            ),
            'new_password': openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_PASSWORD,
                description='Nueva contraseña'
            ),
            'confirm_password': openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_PASSWORD,
                description='Confirmar nueva contraseña'
            ),
        },
        example={
            'old_password': 'mi_password_actual',
            'new_password': 'mi_nueva_password123',
            'confirm_password': 'mi_nueva_password123'
        }
    ),
    responses={
        200: openapi.Response(
            description="Contraseña cambiada exitosamente",
            examples={
                "application/json": {
                    "success": True,
                    "data": None,
                    "message": "Contraseña cambiada exitosamente",
                    "errors": []
                }
            }
        ),
        400: openapi.Response(
            description="Error en validación",
            examples={
                "application/json": {
                    "success": False,
                    "data": None,
                    "message": "Error al cambiar contraseña",
                    "errors": {"old_password": ["La contraseña actual es incorrecta."]}
                }
            }
        )
    },
    tags=['Usuario']
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    Vista para cambiar contraseña del usuario autenticado
    """
    serializer = ChangePasswordSerializer(
        data=request.data,
        context={'request': request}
    )

    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({
            'success': True,
            'data': None,
            'message': 'Contraseña cambiada exitosamente',
            'errors': []
        }, status=status.HTTP_200_OK)

    return Response({
        'success': False,
        'data': None,
        'message': 'Error al cambiar contraseña',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validate_token_view(request):
    """
    Vista para validar si el token JWT es válido
    """
    return Response({
        'success': True,
        'data': {
            'valid': True,
            'user': {
                'id': request.user.id,
                'email': request.user.email,
                'nombre': request.user.nombre,
                'apellido': request.user.apellido,
                'rol': request.user.rol,
            }
        },
        'message': 'Token válido',
        'errors': []
    }, status=status.HTTP_200_OK)
