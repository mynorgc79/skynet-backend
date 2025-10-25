"""
SKYNET - Serializers del módulo de visitas
"""

from rest_framework import serializers
from django.utils import timezone
from .models import Visita, Ejecucion
from apps.clientes.serializers import ClienteSerializer
from apps.usuarios.serializers import UsuarioSerializer


class EjecucionSerializer(serializers.ModelSerializer):
    """
    Serializer para lectura de datos de Ejecución
    """

    # Campos adicionales para compatibilidad frontend
    idEjecucion = serializers.IntegerField(source='id', read_only=True)
    visitaId = serializers.IntegerField(source='visita_id', read_only=True)
    tiempoInicio = serializers.DateTimeField(
        source='tiempo_inicio', read_only=True)
    tiempoFin = serializers.DateTimeField(source='tiempo_fin', read_only=True)
    evidenciaFoto = serializers.CharField(
        source='evidencia_foto', read_only=True)
    fechaCreacion = serializers.DateTimeField(
        source='fecha_creacion', read_only=True)

    class Meta:
        model = Ejecucion
        fields = [
            'idEjecucion',
            'visitaId',
            'descripcion',
            'tiempoInicio',
            'tiempoFin',
            'completada',
            'observaciones',
            'evidenciaFoto',
            'fechaCreacion'
        ]


class VisitaSerializer(serializers.ModelSerializer):
    """
    Serializer para lectura de datos de Visita
    Estructura compatible con el frontend Angular
    """

    # Campos adicionales para compatibilidad frontend
    idVisita = serializers.IntegerField(source='id', read_only=True)
    clienteId = serializers.IntegerField(source='cliente_id', read_only=True)
    tecnicoId = serializers.IntegerField(source='tecnico_id', read_only=True)
    supervisorId = serializers.IntegerField(
        source='supervisor_id', read_only=True)
    fechaProgramada = serializers.DateTimeField(
        source='fecha_programada', read_only=True)
    fechaInicio = serializers.DateTimeField(
        source='fecha_inicio', read_only=True)
    fechaFin = serializers.DateTimeField(source='fecha_fin', read_only=True)
    tipoVisita = serializers.CharField(source='tipo_visita', read_only=True)
    fechaCreacion = serializers.DateTimeField(
        source='fecha_creacion', read_only=True)
    fechaActualizacion = serializers.DateTimeField(
        source='fecha_actualizacion', read_only=True)

    # Relaciones anidadas (opcional)
    cliente = ClienteSerializer(read_only=True)
    tecnico = UsuarioSerializer(read_only=True)
    supervisor = UsuarioSerializer(read_only=True)
    ejecuciones = EjecucionSerializer(many=True, read_only=True)

    class Meta:
        model = Visita
        fields = [
            'idVisita',
            'clienteId',
            'tecnicoId',
            'supervisorId',
            'fechaProgramada',
            'fechaInicio',
            'fechaFin',
            'estado',
            'tipoVisita',
            'descripcion',
            'observaciones',
            'latitud',
            'longitud',
            'fechaCreacion',
            'fechaActualizacion',
            # Relaciones
            'cliente',
            'tecnico',
            'supervisor',
            'ejecuciones'
        ]


class VisitaCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para creación de Visita con validaciones
    """

    class Meta:
        model = Visita
        fields = [
            'cliente',
            'tecnico',
            'supervisor',
            'fecha_programada',
            'tipo_visita',
            'descripcion',
            'observaciones',
            'latitud',
            'longitud'
        ]

    def validate_fecha_programada(self, value):
        """Validar que la fecha programada sea futura"""
        if value < timezone.now():
            raise serializers.ValidationError(
                "No se pueden programar visitas en fechas pasadas.")
        return value

    def validate_tecnico(self, value):
        """Validar que el usuario asignado sea técnico"""
        if not value.es_tecnico:
            raise serializers.ValidationError(
                "Solo se pueden asignar usuarios con rol TECNICO.")
        if not value.activo:
            raise serializers.ValidationError(
                "No se puede asignar un técnico inactivo.")
        return value

    def validate_supervisor(self, value):
        """Validar supervisor si se proporciona"""
        if value and not value.es_supervisor:
            raise serializers.ValidationError(
                "Solo se pueden asignar usuarios con rol SUPERVISOR.")
        if value and not value.activo:
            raise serializers.ValidationError(
                "No se puede asignar un supervisor inactivo.")
        return value

    def validate_cliente(self, value):
        """Validar que el cliente esté activo"""
        if not value.activo:
            raise serializers.ValidationError(
                "No se pueden crear visitas para clientes inactivos.")
        return value

    def validate(self, attrs):
        """Validaciones cruzadas"""
        tecnico = attrs.get('tecnico')
        fecha_programada = attrs.get('fecha_programada')

        # Validar que el técnico no tenga visitas simultáneas
        if tecnico and fecha_programada:
            # Buscar visitas del técnico en la misma fecha/hora
            conflictos = Visita.objects.filter(
                tecnico=tecnico,
                fecha_programada__date=fecha_programada.date(),
                estado__in=[Visita.EstadoVisitaChoices.PROGRAMADA,
                            Visita.EstadoVisitaChoices.EN_PROGRESO]
            ).exclude(id=self.instance.id if self.instance else None)

            if conflictos.exists():
                raise serializers.ValidationError({
                    'tecnico': f'El técnico ya tiene visitas programadas para {fecha_programada.date()}.'
                })

        # Validar coordenadas si se proporcionan
        latitud = attrs.get('latitud')
        longitud = attrs.get('longitud')

        if (latitud is not None and longitud is None) or (latitud is None and longitud is not None):
            raise serializers.ValidationError({
                'coordenadas': 'Debe proporcionar tanto latitud como longitud, o ninguna.'
            })

        return attrs


class VisitaUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualización de Visita
    """

    class Meta:
        model = Visita
        fields = [
            'tecnico',
            'supervisor',
            'fecha_programada',
            'tipo_visita',
            'descripcion',
            'observaciones',
            'latitud',
            'longitud'
        ]

    def validate_fecha_programada(self, value):
        """Validar fecha programada en actualizaciones"""
        # Solo permitir cambiar fecha si la visita está programada
        if self.instance and self.instance.estado != Visita.EstadoVisitaChoices.PROGRAMADA:
            raise serializers.ValidationError(
                "Solo se puede cambiar la fecha de visitas programadas.")

        if value < timezone.now():
            raise serializers.ValidationError(
                "No se pueden programar visitas en fechas pasadas.")
        return value

    def validate_tecnico(self, value):
        """Validar cambio de técnico"""
        if not value.es_tecnico:
            raise serializers.ValidationError(
                "Solo se pueden asignar usuarios con rol TECNICO.")
        if not value.activo:
            raise serializers.ValidationError(
                "No se puede asignar un técnico inactivo.")

        # No permitir cambiar técnico si la visita está en progreso o completada
        if self.instance and self.instance.estado in [
            Visita.EstadoVisitaChoices.EN_PROGRESO,
            Visita.EstadoVisitaChoices.COMPLETADA
        ]:
            raise serializers.ValidationError(
                "No se puede cambiar el técnico de una visita en progreso o completada.")

        return value


class EjecucionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear ejecución
    """

    class Meta:
        model = Ejecucion
        fields = [
            'visita',
            'descripcion',
            'tiempo_inicio',
            'observaciones',
            'evidencia_foto'
        ]

    def validate_visita(self, value):
        """Validar que la visita esté en progreso"""
        if value.estado != Visita.EstadoVisitaChoices.EN_PROGRESO:
            raise serializers.ValidationError(
                "Solo se pueden crear ejecuciones en visitas en progreso.")
        return value

    def validate_tiempo_inicio(self, value):
        """Validar tiempo de inicio"""
        if value > timezone.now():
            raise serializers.ValidationError(
                "El tiempo de inicio no puede ser futuro.")
        return value


class EjecucionUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar ejecución
    """

    class Meta:
        model = Ejecucion
        fields = [
            'descripcion',
            'tiempo_fin',
            'completada',
            'observaciones',
            'evidencia_foto'
        ]

    def validate_tiempo_fin(self, value):
        """Validar tiempo de finalización"""
        if value and self.instance and value < self.instance.tiempo_inicio:
            raise serializers.ValidationError(
                "El tiempo de fin no puede ser anterior al tiempo de inicio.")
        return value

    def validate(self, attrs):
        """Validaciones cruzadas"""
        completada = attrs.get('completada')
        tiempo_fin = attrs.get('tiempo_fin')

        # Si se marca como completada, debe tener tiempo de fin
        if completada and not tiempo_fin and not self.instance.tiempo_fin:
            raise serializers.ValidationError({
                'tiempo_fin': 'Una ejecución completada debe tener tiempo de finalización.'
            })

        return attrs


class VisitaWorkflowSerializer(serializers.Serializer):
    """
    Serializer para operaciones de workflow (iniciar, completar, cancelar)
    """
    observaciones = serializers.CharField(required=False, allow_blank=True)
    latitud = serializers.DecimalField(
        max_digits=10, decimal_places=8, required=False)
    longitud = serializers.DecimalField(
        max_digits=11, decimal_places=8, required=False)

    def validate(self, attrs):
        """Validaciones para coordenadas"""
        latitud = attrs.get('latitud')
        longitud = attrs.get('longitud')

        if (latitud is not None and longitud is None) or (latitud is None and longitud is not None):
            raise serializers.ValidationError({
                'coordenadas': 'Debe proporcionar tanto latitud como longitud, o ninguna.'
            })

        return attrs
