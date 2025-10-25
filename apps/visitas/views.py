"""
SKYNET - Vistas del módulo de visitas
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Visita, Ejecucion
from .serializers import (
    VisitaSerializer,
    VisitaCreateSerializer,
    VisitaUpdateSerializer,
    VisitaWorkflowSerializer,
    EjecucionSerializer,
    EjecucionCreateSerializer,
    EjecucionUpdateSerializer
)


# ==============================================================================
# CRUD DE VISITAS
# ==============================================================================

@swagger_auto_schema(
    method='get',
    operation_description="Listar todas las visitas con filtros opcionales",
    operation_summary="Listar Visitas",
    manual_parameters=[
        openapi.Parameter(
            'estado',
            openapi.IN_QUERY,
            description="Filtrar por estado",
            type=openapi.TYPE_STRING,
            enum=['PROGRAMADA', 'EN_PROGRESO',
                  'COMPLETADA', 'CANCELADA', 'REPROGRAMADA']
        ),
        openapi.Parameter(
            'tipo_visita',
            openapi.IN_QUERY,
            description="Filtrar por tipo de visita",
            type=openapi.TYPE_STRING,
            enum=['MANTENIMIENTO', 'INSTALACION', 'REPARACION', 'INSPECCION']
        ),
        openapi.Parameter(
            'tecnico_id',
            openapi.IN_QUERY,
            description="Filtrar por técnico asignado",
            type=openapi.TYPE_INTEGER
        ),
        openapi.Parameter(
            'cliente_id',
            openapi.IN_QUERY,
            description="Filtrar por cliente",
            type=openapi.TYPE_INTEGER
        ),
        openapi.Parameter(
            'fecha_desde',
            openapi.IN_QUERY,
            description="Filtrar desde fecha (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE
        ),
        openapi.Parameter(
            'fecha_hasta',
            openapi.IN_QUERY,
            description="Filtrar hasta fecha (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE
        ),
    ],
    responses={
        200: openapi.Response(
            description="Lista de visitas",
            examples={
                "application/json": {
                    "success": True,
                    "data": [
                        {
                            "idVisita": 1,
                            "clienteId": 1,
                            "tecnicoId": 2,
                            "supervisorId": 3,
                            "fechaProgramada": "2025-10-25T10:00:00Z",
                            "fechaInicio": None,
                            "fechaFin": None,
                            "estado": "PROGRAMADA",
                            "tipoVisita": "MANTENIMIENTO",
                            "descripcion": "Mantenimiento preventivo",
                            "observaciones": "",
                            "latitud": None,
                            "longitud": None,
                            "fechaCreacion": "2025-10-24T10:00:00Z",
                            "fechaActualizacion": "2025-10-24T10:00:00Z"
                        }
                    ],
                    "message": "Visitas obtenidas exitosamente",
                    "errors": []
                }
            }
        )
    },
    tags=['Visitas']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def visitas_list_view(request):
    """
    Vista para listar visitas con filtros
    """
    # Obtener queryset base
    queryset = Visita.objects.select_related(
        'cliente', 'tecnico', 'supervisor').all()

    # Filtrar por rol del usuario
    if request.user.es_tecnico:
        # Los técnicos solo ven sus propias visitas
        queryset = queryset.filter(tecnico=request.user)
    elif request.user.es_supervisor:
        # Los supervisores ven visitas que supervisan o técnicos bajo su supervisión
        queryset = queryset.filter(supervisor=request.user)
    # Los administradores ven todas las visitas

    # Aplicar filtros
    estado = request.GET.get('estado')
    if estado:
        queryset = queryset.filter(estado=estado)

    tipo_visita = request.GET.get('tipo_visita')
    if tipo_visita:
        queryset = queryset.filter(tipo_visita=tipo_visita)

    tecnico_id = request.GET.get('tecnico_id')
    if tecnico_id:
        queryset = queryset.filter(tecnico_id=tecnico_id)

    cliente_id = request.GET.get('cliente_id')
    if cliente_id:
        queryset = queryset.filter(cliente_id=cliente_id)

    fecha_desde = request.GET.get('fecha_desde')
    if fecha_desde:
        queryset = queryset.filter(fecha_programada__date__gte=fecha_desde)

    fecha_hasta = request.GET.get('fecha_hasta')
    if fecha_hasta:
        queryset = queryset.filter(fecha_programada__date__lte=fecha_hasta)

    # Ordenar por fecha programada
    queryset = queryset.order_by('-fecha_programada')

    # Serializar datos
    serializer = VisitaSerializer(queryset, many=True)

    return Response({
        'success': True,
        'data': serializer.data,
        'message': 'Visitas obtenidas exitosamente',
        'errors': []
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Crear una nueva visita en el sistema",
    operation_summary="Crear Visita",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['cliente', 'tecnico', 'fecha_programada',
                  'tipo_visita', 'descripcion'],
        properties={
            'cliente': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='ID del cliente'
            ),
            'tecnico': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='ID del técnico asignado'
            ),
            'supervisor': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='ID del supervisor (opcional)'
            ),
            'fecha_programada': openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME,
                description='Fecha y hora programada'
            ),
            'tipo_visita': openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=['MANTENIMIENTO', 'INSTALACION',
                      'REPARACION', 'INSPECCION'],
                description='Tipo de visita'
            ),
            'descripcion': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Descripción de la visita'
            ),
            'observaciones': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Observaciones adicionales'
            ),
            'latitud': openapi.Schema(
                type=openapi.TYPE_NUMBER,
                description='Latitud GPS (opcional)'
            ),
            'longitud': openapi.Schema(
                type=openapi.TYPE_NUMBER,
                description='Longitud GPS (opcional)'
            ),
        },
        example={
            'cliente': 1,
            'tecnico': 2,
            'supervisor': 3,
            'fecha_programada': '2025-10-25T10:00:00Z',
            'tipo_visita': 'MANTENIMIENTO',
            'descripcion': 'Mantenimiento preventivo del sistema',
            'observaciones': 'Revisar componentes principales',
            'latitud': 14.6349,
            'longitud': -90.5069
        }
    ),
    responses={
        201: openapi.Response(description="Visita creada exitosamente"),
        400: openapi.Response(description="Error de validación"),
        403: openapi.Response(description="Sin permisos")
    },
    tags=['Visitas']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def visitas_create_view(request):
    """
    Vista para crear una nueva visita
    """
    # Verificar permisos (administradores y supervisores pueden crear visitas)
    if not (request.user.es_administrador or request.user.es_supervisor):
        return Response({
            'success': False,
            'data': None,
            'message': 'No tienes permisos para crear visitas',
            'errors': ['Solo administradores y supervisores pueden crear visitas']
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = VisitaCreateSerializer(data=request.data)

    if serializer.is_valid():
        visita = serializer.save()
        response_serializer = VisitaSerializer(visita)

        return Response({
            'success': True,
            'data': response_serializer.data,
            'message': 'Visita creada exitosamente',
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
    operation_description="Obtener detalles de una visita específica",
    operation_summary="Detalle de Visita",
    responses={
        200: openapi.Response(description="Detalles de la visita"),
        404: openapi.Response(description="Visita no encontrada")
    },
    tags=['Visitas']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def visitas_detail_view(request, pk):
    """
    Vista para obtener detalles de una visita
    """
    try:
        visita = Visita.objects.select_related(
            'cliente', 'tecnico', 'supervisor').prefetch_related('ejecuciones').get(pk=pk)
    except Visita.DoesNotExist:
        return Response({
            'success': False,
            'data': None,
            'message': 'Visita no encontrada',
            'errors': ['La visita no existe']
        }, status=status.HTTP_404_NOT_FOUND)

    # Verificar permisos
    if request.user.es_tecnico and visita.tecnico != request.user:
        return Response({
            'success': False,
            'data': None,
            'message': 'No tienes permisos para ver esta visita',
            'errors': ['Solo puedes ver tus propias visitas']
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = VisitaSerializer(visita)

    return Response({
        'success': True,
        'data': serializer.data,
        'message': 'Visita obtenida exitosamente',
        'errors': []
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='put',
    operation_description="Actualizar una visita existente",
    operation_summary="Actualizar Visita",
    request_body=VisitaUpdateSerializer,
    responses={
        200: openapi.Response(description="Visita actualizada exitosamente"),
        400: openapi.Response(description="Error de validación"),
        404: openapi.Response(description="Visita no encontrada")
    },
    tags=['Visitas']
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def visitas_update_view(request, pk):
    """
    Vista para actualizar una visita
    """
    try:
        visita = Visita.objects.get(pk=pk)
    except Visita.DoesNotExist:
        return Response({
            'success': False,
            'data': None,
            'message': 'Visita no encontrada',
            'errors': ['La visita no existe']
        }, status=status.HTTP_404_NOT_FOUND)

    # Verificar permisos
    if not (request.user.es_administrador or request.user.es_supervisor):
        return Response({
            'success': False,
            'data': None,
            'message': 'No tienes permisos para actualizar visitas',
            'errors': ['Solo administradores y supervisores pueden actualizar visitas']
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = VisitaUpdateSerializer(
        visita, data=request.data, partial=True)

    if serializer.is_valid():
        updated_visita = serializer.save()
        response_serializer = VisitaSerializer(updated_visita)

        return Response({
            'success': True,
            'data': response_serializer.data,
            'message': 'Visita actualizada exitosamente',
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
    operation_description="Eliminar una visita",
    operation_summary="Eliminar Visita",
    responses={
        200: openapi.Response(description="Visita eliminada exitosamente"),
        404: openapi.Response(description="Visita no encontrada")
    },
    tags=['Visitas']
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def visitas_delete_view(request, pk):
    """
    Vista para eliminar una visita
    """
    try:
        visita = Visita.objects.get(pk=pk)
    except Visita.DoesNotExist:
        return Response({
            'success': False,
            'data': None,
            'message': 'Visita no encontrada',
            'errors': ['La visita no existe']
        }, status=status.HTTP_404_NOT_FOUND)

    # Verificar permisos (solo administradores pueden eliminar)
    if not request.user.es_administrador:
        return Response({
            'success': False,
            'data': None,
            'message': 'No tienes permisos para eliminar visitas',
            'errors': ['Solo los administradores pueden eliminar visitas']
        }, status=status.HTTP_403_FORBIDDEN)

    # No permitir eliminar visitas en progreso o completadas
    if visita.estado in [Visita.EstadoVisitaChoices.EN_PROGRESO, Visita.EstadoVisitaChoices.COMPLETADA]:
        return Response({
            'success': False,
            'data': None,
            'message': 'No se puede eliminar esta visita',
            'errors': ['No se pueden eliminar visitas en progreso o completadas']
        }, status=status.HTTP_400_BAD_REQUEST)

    visita.delete()

    return Response({
        'success': True,
        'data': None,
        'message': 'Visita eliminada exitosamente',
        'errors': []
    }, status=status.HTTP_200_OK)


# ==============================================================================
# WORKFLOW DE VISITAS
# ==============================================================================

@swagger_auto_schema(
    method='post',
    operation_description="Iniciar una visita programada",
    operation_summary="Iniciar Visita",
    request_body=VisitaWorkflowSerializer,
    responses={
        200: openapi.Response(description="Visita iniciada exitosamente"),
        400: openapi.Response(description="Error en el workflow"),
        404: openapi.Response(description="Visita no encontrada")
    },
    tags=['Workflow Visitas']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def visitas_iniciar_view(request, pk):
    """
    Vista para iniciar una visita programada
    """
    try:
        visita = Visita.objects.get(pk=pk)
    except Visita.DoesNotExist:
        return Response({
            'success': False,
            'data': None,
            'message': 'Visita no encontrada',
            'errors': ['La visita no existe']
        }, status=status.HTTP_404_NOT_FOUND)

    # Verificar que solo el técnico asignado puede iniciar
    if visita.tecnico != request.user:
        return Response({
            'success': False,
            'data': None,
            'message': 'No puedes iniciar esta visita',
            'errors': ['Solo el técnico asignado puede iniciar la visita']
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        # Actualizar coordenadas si se proporcionan
        serializer = VisitaWorkflowSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            if data.get('latitud') and data.get('longitud'):
                visita.latitud = data['latitud']
                visita.longitud = data['longitud']
            if data.get('observaciones'):
                visita.observaciones = data['observaciones']

        visita.iniciar()
        response_serializer = VisitaSerializer(visita)

        return Response({
            'success': True,
            'data': response_serializer.data,
            'message': 'Visita iniciada exitosamente',
            'errors': []
        }, status=status.HTTP_200_OK)

    except ValidationError as e:
        return Response({
            'success': False,
            'data': None,
            'message': 'Error al iniciar la visita',
            'errors': [str(e)]
        }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    operation_description="Completar una visita en progreso",
    operation_summary="Completar Visita",
    request_body=VisitaWorkflowSerializer,
    responses={
        200: openapi.Response(description="Visita completada exitosamente"),
        400: openapi.Response(description="Error en el workflow")
    },
    tags=['Workflow Visitas']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def visitas_completar_view(request, pk):
    """
    Vista para completar una visita en progreso
    """
    try:
        visita = Visita.objects.get(pk=pk)
    except Visita.DoesNotExist:
        return Response({
            'success': False,
            'data': None,
            'message': 'Visita no encontrada',
            'errors': ['La visita no existe']
        }, status=status.HTTP_404_NOT_FOUND)

    # Verificar que solo el técnico asignado puede completar
    if visita.tecnico != request.user:
        return Response({
            'success': False,
            'data': None,
            'message': 'No puedes completar esta visita',
            'errors': ['Solo el técnico asignado puede completar la visita']
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        serializer = VisitaWorkflowSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            observaciones = data.get('observaciones')

            # Actualizar coordenadas finales si se proporcionan
            if data.get('latitud') and data.get('longitud'):
                visita.latitud = data['latitud']
                visita.longitud = data['longitud']
                visita.save()

        visita.completar(observaciones)
        response_serializer = VisitaSerializer(visita)

        return Response({
            'success': True,
            'data': response_serializer.data,
            'message': 'Visita completada exitosamente',
            'errors': []
        }, status=status.HTTP_200_OK)

    except ValidationError as e:
        return Response({
            'success': False,
            'data': None,
            'message': 'Error al completar la visita',
            'errors': [str(e)]
        }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    operation_description="Cancelar una visita",
    operation_summary="Cancelar Visita",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['motivo'],
        properties={
            'motivo': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Motivo de la cancelación'
            ),
        }
    ),
    responses={
        200: openapi.Response(description="Visita cancelada exitosamente"),
        400: openapi.Response(description="Error en el workflow")
    },
    tags=['Workflow Visitas']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def visitas_cancelar_view(request, pk):
    """
    Vista para cancelar una visita
    """
    try:
        visita = Visita.objects.get(pk=pk)
    except Visita.DoesNotExist:
        return Response({
            'success': False,
            'data': None,
            'message': 'Visita no encontrada',
            'errors': ['La visita no existe']
        }, status=status.HTTP_404_NOT_FOUND)

    # Verificar permisos (técnico asignado o supervisor)
    if not (visita.tecnico == request.user or request.user.es_administrador or request.user.es_supervisor):
        return Response({
            'success': False,
            'data': None,
            'message': 'No puedes cancelar esta visita',
            'errors': ['Solo el técnico asignado o supervisores pueden cancelar visitas']
        }, status=status.HTTP_403_FORBIDDEN)

    motivo = request.data.get('motivo')
    if not motivo:
        return Response({
            'success': False,
            'data': None,
            'message': 'Motivo requerido',
            'errors': ['Debe proporcionar un motivo para la cancelación']
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        visita.cancelar(motivo)
        response_serializer = VisitaSerializer(visita)

        return Response({
            'success': True,
            'data': response_serializer.data,
            'message': 'Visita cancelada exitosamente',
            'errors': []
        }, status=status.HTTP_200_OK)

    except ValidationError as e:
        return Response({
            'success': False,
            'data': None,
            'message': 'Error al cancelar la visita',
            'errors': [str(e)]
        }, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# EJECUCIONES DE VISITAS
# ==============================================================================

@swagger_auto_schema(
    method='get',
    operation_description="Obtener ejecuciones de una visita",
    operation_summary="Listar Ejecuciones",
    responses={
        200: openapi.Response(description="Lista de ejecuciones"),
        404: openapi.Response(description="Visita no encontrada")
    },
    tags=['Ejecuciones']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def visitas_ejecuciones_list_view(request, pk):
    """
    Vista para obtener las ejecuciones de una visita
    """
    try:
        visita = Visita.objects.get(pk=pk)
    except Visita.DoesNotExist:
        return Response({
            'success': False,
            'data': None,
            'message': 'Visita no encontrada',
            'errors': ['La visita no existe']
        }, status=status.HTTP_404_NOT_FOUND)

    # Verificar permisos
    if request.user.es_tecnico and visita.tecnico != request.user:
        return Response({
            'success': False,
            'data': None,
            'message': 'No tienes permisos para ver estas ejecuciones',
            'errors': ['Solo puedes ver ejecuciones de tus propias visitas']
        }, status=status.HTTP_403_FORBIDDEN)

    ejecuciones = visita.ejecuciones.all().order_by('tiempo_inicio')
    serializer = EjecucionSerializer(ejecuciones, many=True)

    return Response({
        'success': True,
        'data': serializer.data,
        'message': 'Ejecuciones obtenidas exitosamente',
        'errors': []
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Crear una nueva ejecución en una visita",
    operation_summary="Crear Ejecución",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['descripcion', 'tiempo_inicio'],
        properties={
            'descripcion': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Descripción de la ejecución'
            ),
            'tiempo_inicio': openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME,
                description='Tiempo de inicio'
            ),
            'observaciones': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Observaciones'
            ),
            'evidencia_foto': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='URL de evidencia fotográfica'
            ),
        }
    ),
    responses={
        201: openapi.Response(description="Ejecución creada exitosamente"),
        400: openapi.Response(description="Error de validación")
    },
    tags=['Ejecuciones']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def visitas_ejecuciones_create_view(request, pk):
    """
    Vista para crear una ejecución en una visita
    """
    try:
        visita = Visita.objects.get(pk=pk)
    except Visita.DoesNotExist:
        return Response({
            'success': False,
            'data': None,
            'message': 'Visita no encontrada',
            'errors': ['La visita no existe']
        }, status=status.HTTP_404_NOT_FOUND)

    # Solo el técnico asignado puede crear ejecuciones
    if visita.tecnico != request.user:
        return Response({
            'success': False,
            'data': None,
            'message': 'No puedes crear ejecuciones en esta visita',
            'errors': ['Solo el técnico asignado puede crear ejecuciones']
        }, status=status.HTTP_403_FORBIDDEN)

    # Agregar la visita a los datos
    data = request.data.copy()
    data['visita'] = visita.id

    serializer = EjecucionCreateSerializer(data=data)

    if serializer.is_valid():
        ejecucion = serializer.save()
        response_serializer = EjecucionSerializer(ejecucion)

        return Response({
            'success': True,
            'data': response_serializer.data,
            'message': 'Ejecución creada exitosamente',
            'errors': []
        }, status=status.HTTP_201_CREATED)

    return Response({
        'success': False,
        'data': None,
        'message': 'Error en la validación',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='put',
    operation_description="Actualizar una ejecución",
    operation_summary="Actualizar Ejecución",
    request_body=EjecucionUpdateSerializer,
    responses={
        200: openapi.Response(description="Ejecución actualizada exitosamente"),
        400: openapi.Response(description="Error de validación"),
        404: openapi.Response(description="Ejecución no encontrada")
    },
    tags=['Ejecuciones']
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def ejecuciones_update_view(request, pk):
    """
    Vista para actualizar una ejecución
    """
    try:
        ejecucion = Ejecucion.objects.select_related('visita').get(pk=pk)
    except Ejecucion.DoesNotExist:
        return Response({
            'success': False,
            'data': None,
            'message': 'Ejecución no encontrada',
            'errors': ['La ejecución no existe']
        }, status=status.HTTP_404_NOT_FOUND)

    # Solo el técnico asignado puede actualizar ejecuciones
    if ejecucion.visita.tecnico != request.user:
        return Response({
            'success': False,
            'data': None,
            'message': 'No puedes actualizar esta ejecución',
            'errors': ['Solo el técnico asignado puede actualizar ejecuciones']
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = EjecucionUpdateSerializer(
        ejecucion, data=request.data, partial=True)

    if serializer.is_valid():
        updated_ejecucion = serializer.save()
        response_serializer = EjecucionSerializer(updated_ejecucion)

        return Response({
            'success': True,
            'data': response_serializer.data,
            'message': 'Ejecución actualizada exitosamente',
            'errors': []
        }, status=status.HTTP_200_OK)

    return Response({
        'success': False,
        'data': None,
        'message': 'Error en la validación',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)
