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
    UsuarioCreateSerializer,
    UsuarioUpdateSerializer,
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


# ==============================================================================
# CRUD DE USUARIOS
# ==============================================================================

@swagger_auto_schema(
    method='get',
    operation_description="Listar todos los usuarios con filtros opcionales",
    operation_summary="Listar Usuarios",
    manual_parameters=[
        openapi.Parameter(
            'rol',
            openapi.IN_QUERY,
            description="Filtrar por rol",
            type=openapi.TYPE_STRING,
            enum=['ADMINISTRADOR', 'SUPERVISOR', 'TECNICO']
        ),
        openapi.Parameter(
            'activo',
            openapi.IN_QUERY,
            description="Filtrar por estado activo",
            type=openapi.TYPE_BOOLEAN
        ),
        openapi.Parameter(
            'search',
            openapi.IN_QUERY,
            description="Buscar por nombre, apellido o email",
            type=openapi.TYPE_STRING
        ),
    ],
    responses={
        200: openapi.Response(
            description="Lista de usuarios",
            examples={
                "application/json": {
                    "success": True,
                    "data": [
                        {
                            "id": 1,
                            "email": "admin@example.com",
                            "nombre": "Juan",
                            "apellido": "Pérez",
                            "nombre_completo": "Juan Pérez",
                            "telefono": "12345678",
                            "rol": "ADMINISTRADOR",
                            "activo": True,
                            "fecha_creacion": "2025-10-23T10:00:00Z"
                        }
                    ],
                    "message": "Usuarios obtenidos exitosamente",
                    "errors": []
                }
            }
        )
    },
    tags=['Usuarios']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Temporal para pruebas
def usuarios_list_view(request):
    """
    Vista para listar usuarios con filtros
    """
    # Verificar permisos (solo administradores y supervisores pueden ver la lista)
    # Temporalmente deshabilitado para pruebas
    if request.user.is_authenticated and not (request.user.es_administrador or request.user.es_supervisor):
        return Response({
            'success': False,
            'data': None,
            'message': 'No tienes permisos para ver la lista de usuarios',
            'errors': ['Permisos insuficientes']
        }, status=status.HTTP_403_FORBIDDEN)

    # Obtener queryset base
    queryset = Usuario.objects.all()

    # Aplicar filtros
    rol = request.GET.get('rol')
    if rol:
        queryset = queryset.filter(rol=rol)

    activo = request.GET.get('activo')
    if activo is not None:
        is_active = activo.lower() == 'true'
        queryset = queryset.filter(activo=is_active)

    search = request.GET.get('search')
    if search:
        queryset = queryset.filter(
            nombre__icontains=search
        ) | queryset.filter(
            apellido__icontains=search
        ) | queryset.filter(
            email__icontains=search
        )

    # Si es supervisor, solo ve sus técnicos
    if request.user.es_supervisor:
        # Por ahora mostramos todos, después implementaremos la relación supervisor-técnico
        pass

    # Serializar datos
    serializer = UsuarioSerializer(queryset, many=True)

    return Response({
        'success': True,
        'data': serializer.data,
        'message': 'Usuarios obtenidos exitosamente',
        'errors': []
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Crear un nuevo usuario en el sistema",
    operation_summary="Crear Usuario",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email', 'nombre', 'apellido',
                  'rol', 'password', 'confirm_password'],
        properties={
            'email': openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                description='Email único del usuario'
            ),
            'nombre': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Nombre del usuario'
            ),
            'apellido': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Apellido del usuario'
            ),
            'telefono': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Teléfono (formato guatemalteco)'
            ),
            'rol': openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=['ADMINISTRADOR', 'SUPERVISOR', 'TECNICO'],
                description='Rol del usuario'
            ),
            'password': openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_PASSWORD,
                description='Contraseña (mínimo 8 caracteres)'
            ),
            'confirm_password': openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_PASSWORD,
                description='Confirmar contraseña'
            ),
        },
        example={
            'email': 'nuevo@example.com',
            'nombre': 'Juan',
            'apellido': 'García',
            'telefono': '12345678',
            'rol': 'TECNICO',
            'password': 'password123',
            'confirm_password': 'password123'
        }
    ),
    responses={
        201: openapi.Response(
            description="Usuario creado exitosamente",
            examples={
                "application/json": {
                    "success": True,
                    "data": {
                        "id": 2,
                        "email": "nuevo@example.com",
                        "nombre": "Juan",
                        "apellido": "García",
                        "nombre_completo": "Juan García",
                        "telefono": "12345678",
                        "rol": "TECNICO",
                        "activo": True,
                        "fecha_creacion": "2025-10-23T10:00:00Z"
                    },
                    "message": "Usuario creado exitosamente",
                    "errors": []
                }
            }
        ),
        400: openapi.Response(
            description="Error de validación",
            examples={
                "application/json": {
                    "success": False,
                    "data": None,
                    "message": "Error en la validación",
                    "errors": ["El email ya existe"]
                }
            }
        )
    },
    tags=['Usuarios']
)
@api_view(['POST'])
# Temporalmente permitir sin autenticación para crear el primer admin
@permission_classes([AllowAny])
def usuarios_create_view(request):
    """
    Vista para crear un nuevo usuario
    """
    # Verificar permisos (solo administradores pueden crear usuarios)
    # Temporalmente deshabilitado para permitir crear el primer administrador
    if request.user.is_authenticated and not request.user.es_administrador:
        return Response({
            'success': False,
            'data': None,
            'message': 'No tienes permisos para crear usuarios',
            'errors': ['Solo los administradores pueden crear usuarios']
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = UsuarioCreateSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        response_serializer = UsuarioSerializer(user)

        return Response({
            'success': True,
            'data': response_serializer.data,
            'message': 'Usuario creado exitosamente',
            'errors': []
        }, status=status.HTTP_201_CREATED)

    return Response({
        'success': False,
        'data': None,
        'message': 'Error en la validación',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    operation_description="Obtener detalles de un usuario específico",
    operation_summary="Detalle de Usuario",
    responses={
        200: openapi.Response(
            description="Detalles del usuario",
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
                    "message": "Usuario obtenido exitosamente",
                    "errors": []
                }
            }
        ),
        404: openapi.Response(
            description="Usuario no encontrado"
        )
    },
    tags=['Usuarios']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def usuarios_detail_view(request, pk):
    """
    Vista para obtener detalles de un usuario
    """
    try:
        user = Usuario.objects.get(pk=pk)
    except Usuario.DoesNotExist:
        return Response({
            'success': False,
            'data': None,
            'message': 'Usuario no encontrado',
            'errors': ['El usuario no existe']
        }, status=status.HTTP_404_NOT_FOUND)

    # Verificar permisos
    if not (request.user.es_administrador or request.user.es_supervisor or request.user.id == user.id):
        return Response({
            'success': False,
            'data': None,
            'message': 'No tienes permisos para ver este usuario',
            'errors': ['Permisos insuficientes']
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = UsuarioSerializer(user)

    return Response({
        'success': True,
        'data': serializer.data,
        'message': 'Usuario obtenido exitosamente',
        'errors': []
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='put',
    operation_description="Actualizar un usuario existente",
    operation_summary="Actualizar Usuario",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'nombre': openapi.Schema(type=openapi.TYPE_STRING),
            'apellido': openapi.Schema(type=openapi.TYPE_STRING),
            'telefono': openapi.Schema(type=openapi.TYPE_STRING),
            'rol': openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=['ADMINISTRADOR', 'SUPERVISOR', 'TECNICO']
            ),
            'activo': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        }
    ),
    responses={
        200: openapi.Response(description="Usuario actualizado exitosamente"),
        400: openapi.Response(description="Error de validación"),
        404: openapi.Response(description="Usuario no encontrado")
    },
    tags=['Usuarios']
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def usuarios_update_view(request, pk):
    """
    Vista para actualizar un usuario
    """
    try:
        user = Usuario.objects.get(pk=pk)
    except Usuario.DoesNotExist:
        return Response({
            'success': False,
            'data': None,
            'message': 'Usuario no encontrado',
            'errors': ['El usuario no existe']
        }, status=status.HTTP_404_NOT_FOUND)

    # Verificar permisos (solo administradores pueden actualizar otros usuarios)
    if not request.user.es_administrador and request.user.id != user.id:
        return Response({
            'success': False,
            'data': None,
            'message': 'No tienes permisos para actualizar este usuario',
            'errors': ['Permisos insuficientes']
        }, status=status.HTTP_403_FORBIDDEN)

    # Los usuarios normales no pueden cambiar su rol
    if not request.user.es_administrador and 'rol' in request.data:
        return Response({
            'success': False,
            'data': None,
            'message': 'No puedes cambiar tu propio rol',
            'errors': ['Solo los administradores pueden cambiar roles']
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = UsuarioUpdateSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        updated_user = serializer.save()
        response_serializer = UsuarioSerializer(updated_user)

        return Response({
            'success': True,
            'data': response_serializer.data,
            'message': 'Usuario actualizado exitosamente',
            'errors': []
        }, status=status.HTTP_200_OK)

    return Response({
        'success': False,
        'data': None,
        'message': 'Error en la validación',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='delete',
    operation_description="Eliminar (desactivar) un usuario",
    operation_summary="Eliminar Usuario",
    responses={
        200: openapi.Response(description="Usuario eliminado exitosamente"),
        404: openapi.Response(description="Usuario no encontrado")
    },
    tags=['Usuarios']
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def usuarios_delete_view(request, pk):
    """
    Vista para eliminar (desactivar) un usuario
    """
    try:
        user = Usuario.objects.get(pk=pk)
    except Usuario.DoesNotExist:
        return Response({
            'success': False,
            'data': None,
            'message': 'Usuario no encontrado',
            'errors': ['El usuario no existe']
        }, status=status.HTTP_404_NOT_FOUND)

    # Verificar permisos (solo administradores pueden eliminar usuarios)
    if not request.user.es_administrador:
        return Response({
            'success': False,
            'data': None,
            'message': 'No tienes permisos para eliminar usuarios',
            'errors': ['Solo los administradores pueden eliminar usuarios']
        }, status=status.HTTP_403_FORBIDDEN)

    # No permitir eliminar el propio usuario
    if request.user.id == user.id:
        return Response({
            'success': False,
            'data': None,
            'message': 'No puedes eliminar tu propia cuenta',
            'errors': ['Operación no permitida']
        }, status=status.HTTP_400_BAD_REQUEST)

    # Soft delete - desactivar usuario
    user.activo = False
    user.save()

    return Response({
        'success': True,
        'data': None,
        'message': 'Usuario eliminado exitosamente',
        'errors': []
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Activar o desactivar un usuario",
    operation_summary="Toggle Estado Usuario",
    responses={
        200: openapi.Response(
            description="Estado del usuario cambiado exitosamente",
            examples={
                "application/json": {
                    "success": True,
                    "data": {
                        "id": 1,
                        "activo": False,
                        "mensaje": "Usuario desactivado"
                    },
                    "message": "Estado del usuario cambiado exitosamente",
                    "errors": []
                }
            }
        ),
        404: openapi.Response(description="Usuario no encontrado")
    },
    tags=['Usuarios']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def usuarios_toggle_status_view(request, pk):
    """
    Vista para activar/desactivar un usuario
    """
    try:
        user = Usuario.objects.get(pk=pk)
    except Usuario.DoesNotExist:
        return Response({
            'success': False,
            'data': None,
            'message': 'Usuario no encontrado',
            'errors': ['El usuario no existe']
        }, status=status.HTTP_404_NOT_FOUND)

    # Verificar permisos (solo administradores)
    if not request.user.es_administrador:
        return Response({
            'success': False,
            'data': None,
            'message': 'No tienes permisos para cambiar el estado de usuarios',
            'errors': ['Solo los administradores pueden cambiar estados']
        }, status=status.HTTP_403_FORBIDDEN)

    # No permitir desactivar el propio usuario
    if request.user.id == user.id:
        return Response({
            'success': False,
            'data': None,
            'message': 'No puedes cambiar el estado de tu propia cuenta',
            'errors': ['Operación no permitida']
        }, status=status.HTTP_400_BAD_REQUEST)

    # Cambiar estado
    user.activo = not user.activo
    user.save()

    estado_msg = "activado" if user.activo else "desactivado"

    return Response({
        'success': True,
        'data': {
            'id': user.id,
            'activo': user.activo,
            'mensaje': f'Usuario {estado_msg}'
        },
        'message': 'Estado del usuario cambiado exitosamente',
        'errors': []
    }, status=status.HTTP_200_OK)
