"""
SKYNET - Modelos del módulo de visitas
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.utils.models import TimestampedModel
from apps.clientes.models import Cliente
from apps.usuarios.models import Usuario


class Visita(TimestampedModel):
    """
    Modelo de Visita según la especificación del frontend
    """

    class EstadoVisitaChoices(models.TextChoices):
        PROGRAMADA = 'PROGRAMADA', 'Programada'
        EN_PROGRESO = 'EN_PROGRESO', 'En Progreso'
        COMPLETADA = 'COMPLETADA', 'Completada'
        CANCELADA = 'CANCELADA', 'Cancelada'
        REPROGRAMADA = 'REPROGRAMADA', 'Reprogramada'

    class TipoVisitaChoices(models.TextChoices):
        MANTENIMIENTO = 'MANTENIMIENTO', 'Mantenimiento'
        INSTALACION = 'INSTALACION', 'Instalación'
        REPARACION = 'REPARACION', 'Reparación'
        INSPECCION = 'INSPECCION', 'Inspección'

    # Relaciones requeridas por el frontend
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='visitas',
        verbose_name="Cliente"
    )
    tecnico = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='visitas_asignadas',
        limit_choices_to={'rol': Usuario.RolChoices.TECNICO},
        verbose_name="Técnico Asignado"
    )
    supervisor = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visitas_supervisadas',
        limit_choices_to={'rol': Usuario.RolChoices.SUPERVISOR},
        verbose_name="Supervisor"
    )

    # Fechas y horarios
    fecha_programada = models.DateTimeField(
        verbose_name="Fecha Programada"
    )
    fecha_inicio = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Inicio"
    )
    fecha_fin = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Finalización"
    )

    # Estados y tipos
    estado = models.CharField(
        max_length=20,
        choices=EstadoVisitaChoices.choices,
        default=EstadoVisitaChoices.PROGRAMADA,
        verbose_name="Estado"
    )
    tipo_visita = models.CharField(
        max_length=20,
        choices=TipoVisitaChoices.choices,
        verbose_name="Tipo de Visita"
    )

    # Descripciones
    descripcion = models.TextField(
        verbose_name="Descripción"
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )

    # Coordenadas GPS para tracking
    latitud = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name="Latitud"
    )
    longitud = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name="Longitud"
    )

    class Meta:
        verbose_name = "Visita"
        verbose_name_plural = "Visitas"
        db_table = "visitas"
        ordering = ['-fecha_programada']

    def __str__(self):
        return f"Visita {self.id} - {self.cliente.nombre} ({self.estado})"

    def clean(self):
        """Validaciones del modelo"""
        super().clean()

        # No permitir programar visitas en el pasado
        if self.fecha_programada and self.fecha_programada < timezone.now():
            raise ValidationError({
                'fecha_programada': 'No se pueden programar visitas en fechas pasadas.'
            })

        # Validar fechas de inicio y fin
        if self.fecha_inicio and self.fecha_fin:
            if self.fecha_inicio > self.fecha_fin:
                raise ValidationError({
                    'fecha_fin': 'La fecha de fin no puede ser anterior a la fecha de inicio.'
                })

        # Validar estado vs fechas
        if self.estado == self.EstadoVisitaChoices.EN_PROGRESO and not self.fecha_inicio:
            raise ValidationError({
                'fecha_inicio': 'Una visita en progreso debe tener fecha de inicio.'
            })

        if self.estado == self.EstadoVisitaChoices.COMPLETADA and not self.fecha_fin:
            raise ValidationError({
                'fecha_fin': 'Una visita completada debe tener fecha de finalización.'
            })

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    # Propiedades de estado
    @property
    def esta_programada(self):
        return self.estado == self.EstadoVisitaChoices.PROGRAMADA

    @property
    def esta_en_progreso(self):
        return self.estado == self.EstadoVisitaChoices.EN_PROGRESO

    @property
    def esta_completada(self):
        return self.estado == self.EstadoVisitaChoices.COMPLETADA

    @property
    def esta_cancelada(self):
        return self.estado == self.EstadoVisitaChoices.CANCELADA

    @property
    def duracion_minutos(self):
        """Duración de la visita en minutos"""
        if self.fecha_inicio and self.fecha_fin:
            delta = self.fecha_fin - self.fecha_inicio
            return delta.total_seconds() / 60
        return None

    @property
    def tiene_coordenadas(self):
        """Verifica si la visita tiene coordenadas GPS"""
        return self.latitud is not None and self.longitud is not None

    # Métodos de workflow
    def iniciar(self, usuario=None):
        """Iniciar una visita programada"""
        if self.estado != self.EstadoVisitaChoices.PROGRAMADA:
            raise ValidationError(
                "Solo se pueden iniciar visitas programadas.")

        self.estado = self.EstadoVisitaChoices.EN_PROGRESO
        self.fecha_inicio = timezone.now()
        self.save()

    def completar(self, observaciones=None):
        """Completar una visita en progreso"""
        if self.estado != self.EstadoVisitaChoices.EN_PROGRESO:
            raise ValidationError(
                "Solo se pueden completar visitas en progreso.")

        self.estado = self.EstadoVisitaChoices.COMPLETADA
        self.fecha_fin = timezone.now()
        if observaciones:
            self.observaciones = observaciones
        self.save()

    def cancelar(self, motivo=None):
        """Cancelar una visita"""
        if self.estado in [self.EstadoVisitaChoices.COMPLETADA]:
            raise ValidationError("No se pueden cancelar visitas completadas.")

        self.estado = self.EstadoVisitaChoices.CANCELADA
        if motivo:
            self.observaciones = f"CANCELADA: {motivo}"
        self.save()


class Ejecucion(TimestampedModel):
    """
    Modelo de Ejecución - subtareas dentro de una visita
    """

    visita = models.ForeignKey(
        Visita,
        on_delete=models.CASCADE,
        related_name='ejecuciones',
        verbose_name="Visita"
    )
    descripcion = models.TextField(
        verbose_name="Descripción de la Ejecución"
    )
    tiempo_inicio = models.DateTimeField(
        verbose_name="Tiempo de Inicio"
    )
    tiempo_fin = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Tiempo de Finalización"
    )
    completada = models.BooleanField(
        default=False,
        verbose_name="Completada"
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )
    evidencia_foto = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="URL de Evidencia Fotográfica"
    )

    class Meta:
        verbose_name = "Ejecución"
        verbose_name_plural = "Ejecuciones"
        db_table = "ejecuciones"
        ordering = ['tiempo_inicio']

    def __str__(self):
        return f"Ejecución {self.id} - Visita {self.visita.id}"

    def clean(self):
        """Validaciones del modelo"""
        super().clean()

        # Validar tiempos
        if self.tiempo_inicio and self.tiempo_fin:
            if self.tiempo_inicio > self.tiempo_fin:
                raise ValidationError({
                    'tiempo_fin': 'El tiempo de fin no puede ser anterior al tiempo de inicio.'
                })

        # Si está completada, debe tener tiempo de fin
        if self.completada and not self.tiempo_fin:
            raise ValidationError({
                'tiempo_fin': 'Una ejecución completada debe tener tiempo de finalización.'
            })

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def duracion_minutos(self):
        """Duración de la ejecución en minutos"""
        if self.tiempo_inicio and self.tiempo_fin:
            delta = self.tiempo_fin - self.tiempo_inicio
            return delta.total_seconds() / 60
        return None

    def completar(self, observaciones=None):
        """Completar una ejecución"""
        self.completada = True
        self.tiempo_fin = timezone.now()
        if observaciones:
            self.observaciones = observaciones
        self.save()
