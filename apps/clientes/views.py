"""
SKYNET - Vistas del módulo de clientes
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Cliente
from .serializers import (
    ClienteSerializer,
    ClienteCreateSerializer,
    ClienteUpdateSerializer
)


# ==============================================================================
# CRUD DE CLIENTES
# ==============================================================================

@swagger_auto_schema(
    method='get',
    operation_description="Listar todos los clientes con filtros opcionales",
    operation_summary="Listar Clientes",
    manual_parameters=[
        openapi.Parameter(
            'tipo_cliente',
            openapi.IN_QUERY,
            description="Filtrar por tipo de cliente",
            type=openapi.TYPE_STRING,
            enum=['CORPORATIVO', 'INDIVIDUAL', 'GOBIERNO']
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
            description="Buscar por nombre, contacto o email",
            type=openapi.TYPE_STRING
        ),
    ],
    responses={
        200: openapi.Response(
            description="Lista de clientes",
            examples={
                "application/json": {
                    "success": True,
                    "data": [
                        {
                            "idCliente": 1,
                            "nombre": "Empresa XYZ",
                            "contacto": "Juan Pérez",
                            "telefono": "12345678",
                            "email": "contacto@empresa.com",
                            "direccion": "Zona 1, Guatemala",
                            "latitud": 14.6349,
                            "longitud": -90.5069,
                            "tipoCliente": "CORPORATIVO",
                            "activo": True,
                            "fechaCreacion": "2025-10-24T10:00:00Z",
                            "fechaActualizacion": "2025-10-24T10:00:00Z"
                        }
                    ],
                    "message": "Clientes obtenidos exitosamente",
                    "errors": []
                }
            }
        )
    },
    tags=['Clientes']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def clientes_list_view(request):
    """
    Vista para listar clientes con filtros
    """
    # Todos los usuarios autenticados pueden ver clientes
    queryset = Cliente.objects.all()

    # Aplicar filtros
    tipo_cliente = request.GET.get('tipo_cliente')
    if tipo_cliente:
        queryset = queryset.filter(tipo_cliente=tipo_cliente)

    activo = request.GET.get('activo')
    if activo is not None:
        is_active = activo.lower() == 'true'
        queryset = queryset.filter(activo=is_active)

    search = request.GET.get('search')
    if search:
        queryset = queryset.filter(
            nombre__icontains=search
        ) | queryset.filter(
            contacto__icontains=search
        ) | queryset.filter(
            email__icontains=search
        )

    # Ordenar por nombre
    queryset = queryset.order_by('nombre')

    # Serializar datos
    serializer = ClienteSerializer(queryset, many=True)

    return Response({
        'success': True,
        'data': serializer.data,
        'message': 'Clientes obtenidos exitosamente',
        'errors': []
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Crear un nuevo cliente en el sistema",
    operation_summary="Crear Cliente",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['nombre', 'contacto', 'telefono', 'email', 'direccion'],
        properties={
            'nombre': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Nombre de la empresa o cliente'
            ),
            'contacto': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Persona de contacto'
            ),
            'telefono': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Teléfono (formato guatemalteco)'
            ),
            'email': openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_EMAIL,
                description='Email único del cliente'
            ),
            'direccion': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Dirección completa'
            ),
            'latitud': openapi.Schema(
                type=openapi.TYPE_NUMBER,
                description='Latitud GPS (opcional)'
            ),
            'longitud': openapi.Schema(
                type=openapi.TYPE_NUMBER,
                description='Longitud GPS (opcional)'
            ),
            'tipo_cliente': openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=['CORPORATIVO', 'INDIVIDUAL', 'GOBIERNO'],
                description='Tipo de cliente'
            ),
        },
        example={
            'nombre': 'Empresa ABC',
            'contacto': 'María García',
            'telefono': '12345678',
            'email': 'contacto@empresa.com',
            'direccion': 'Zona 10, Guatemala City',
            'latitud': 14.6349,
            'longitud': -90.5069,
            'tipo_cliente': 'CORPORATIVO'
        }
    ),
    responses={
        201: openapi.Response(
            description="Cliente creado exitosamente",
            examples={
                "application/json": {
                    "success": True,
                    "data": {
                        "idCliente": 1,
                        "nombre": "Empresa ABC",
                        "contacto": "María García",
                        "telefono": "12345678",
                        "email": "contacto@empresa.com",
                        "direccion": "Zona 10, Guatemala City",
                        "latitud": 14.6349,
                        "longitud": -90.5069,
                        "tipoCliente": "CORPORATIVO",
                        "activo": True,
                        "fechaCreacion": "2025-10-24T10:00:00Z",
                        "fechaActualizacion": "2025-10-24T10:00:00Z"
                    },
                    "message": "Cliente creado exitosamente",
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
                    "errors": {"email": ["Ya existe un cliente con este email."]}
                }
            }
        )
    },
    tags=['Clientes']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clientes_create_view(request):
    """
    Vista para crear un nuevo cliente
    """
    # Verificar permisos (administradores y supervisores pueden crear clientes)
    if not (request.user.es_administrador or request.user.es_supervisor):
        return Response({
            'success': False,
            'data': None,
            'message': 'No tienes permisos para crear clientes',
            'errors': ['Solo administradores y supervisores pueden crear clientes']
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = ClienteCreateSerializer(data=request.data)

    if serializer.is_valid():
        cliente = serializer.save()
        response_serializer = ClienteSerializer(cliente)

        return Response({
            'success': True,
            'data': response_serializer.data,
            'message': 'Cliente creado exitosamente',
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
    operation_description="Obtener detalles de un cliente específico",
    operation_summary="Detalle de Cliente",
    responses={
        200: openapi.Response(
            description="Detalles del cliente",
            examples={
                "application/json": {
                    "success": True,
                    "data": {
                        "idCliente": 1,
                        "nombre": "Empresa ABC",
                        "contacto": "María García",
                        "telefono": "12345678",
                        "email": "contacto@empresa.com",
                        "direccion": "Zona 10, Guatemala City",
                        "latitud": 14.6349,
                        "longitud": -90.5069,
                        "tipoCliente": "CORPORATIVO",
                        "activo": True,
                        "fechaCreacion": "2025-10-24T10:00:00Z",
                        "fechaActualizacion": "2025-10-24T10:00:00Z"
                    },
                    "message": "Cliente obtenido exitosamente",
                    "errors": []
                }
            }
        ),
        404: openapi.Response(
            description="Cliente no encontrado"
        )
    },
    tags=['Clientes']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def clientes_detail_view(request, pk):
    """
    Vista para obtener detalles de un cliente
    """
    try:
        cliente = Cliente.objects.get(pk=pk)
    except Cliente.DoesNotExist:
        return Response({
            'success': False,
            'data': None,
            'message': 'Cliente no encontrado',
            'errors': ['El cliente no existe']
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = ClienteSerializer(cliente)

    return Response({
        'success': True,
        'data': serializer.data,
        'message': 'Cliente obtenido exitosamente',
        'errors': []
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='put',
    operation_description="Actualizar un cliente existente",
    operation_summary="Actualizar Cliente",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'nombre': openapi.Schema(type=openapi.TYPE_STRING),
            'contacto': openapi.Schema(type=openapi.TYPE_STRING),
            'telefono': openapi.Schema(type=openapi.TYPE_STRING),
            'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
            'direccion': openapi.Schema(type=openapi.TYPE_STRING),
            'latitud': openapi.Schema(type=openapi.TYPE_NUMBER),
            'longitud': openapi.Schema(type=openapi.TYPE_NUMBER),
            'tipo_cliente': openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=['CORPORATIVO', 'INDIVIDUAL', 'GOBIERNO']
            ),
            'activo': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        }
    ),
    responses={
        200: openapi.Response(description="Cliente actualizado exitosamente"),
        400: openapi.Response(description="Error de validación"),
        404: openapi.Response(description="Cliente no encontrado")
    },
    tags=['Clientes']
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def clientes_update_view(request, pk):
    """
    Vista para actualizar un cliente
    """
    try:
        cliente = Cliente.objects.get(pk=pk)
    except Cliente.DoesNotExist:
        return Response({
            'success': False,
            'data': None,
            'message': 'Cliente no encontrado',
            'errors': ['El cliente no existe']
        }, status=status.HTTP_404_NOT_FOUND)

    # Verificar permisos (administradores y supervisores pueden actualizar)
    if not (request.user.es_administrador or request.user.es_supervisor):
        return Response({
            'success': False,
            'data': None,
            'message': 'No tienes permisos para actualizar clientes',
            'errors': ['Solo administradores y supervisores pueden actualizar clientes']
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = ClienteUpdateSerializer(
        cliente, data=request.data, partial=True)

    if serializer.is_valid():
        updated_cliente = serializer.save()
        response_serializer = ClienteSerializer(updated_cliente)

        return Response({
            'success': True,
            'data': response_serializer.data,
            'message': 'Cliente actualizado exitosamente',
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
    operation_description="Eliminar (desactivar) un cliente",
    operation_summary="Eliminar Cliente",
    responses={
        200: openapi.Response(description="Cliente eliminado exitosamente"),
        404: openapi.Response(description="Cliente no encontrado")
    },
    tags=['Clientes']
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clientes_delete_view(request, pk):
    """
    Vista para eliminar (desactivar) un cliente
    """
    try:
        cliente = Cliente.objects.get(pk=pk)
    except Cliente.DoesNotExist:
        return Response({
            'success': False,
            'data': None,
            'message': 'Cliente no encontrado',
            'errors': ['El cliente no existe']
        }, status=status.HTTP_404_NOT_FOUND)

    # Verificar permisos (solo administradores pueden eliminar)
    if not request.user.es_administrador:
        return Response({
            'success': False,
            'data': None,
            'message': 'No tienes permisos para eliminar clientes',
            'errors': ['Solo los administradores pueden eliminar clientes']
        }, status=status.HTTP_403_FORBIDDEN)

    # Soft delete - desactivar cliente
    cliente.activo = False
    cliente.save()

    return Response({
        'success': True,
        'data': None,
        'message': 'Cliente eliminado exitosamente',
        'errors': []
    }, status=status.HTTP_200_OK)
