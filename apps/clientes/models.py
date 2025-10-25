"""
SKYNET - Modelos del módulo de clientes
"""

from django.db import models
from apps.utils.models import TimestampedModel
from apps.utils.validators import validate_guatemala_phone, validate_guatemala_email


class Cliente(TimestampedModel):
    """
    Modelo de Cliente según la especificación del frontend
    """

    class TipoClienteChoices(models.TextChoices):
        CORPORATIVO = 'CORPORATIVO', 'Corporativo'
        INDIVIDUAL = 'INDIVIDUAL', 'Individual'
        GOBIERNO = 'GOBIERNO', 'Gobierno'

    # Campos básicos requeridos por el frontend
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre"
    )
    contacto = models.CharField(
        max_length=100,
        verbose_name="Persona de Contacto"
    )
    telefono = models.CharField(
        max_length=20,
        validators=[validate_guatemala_phone],
        verbose_name="Teléfono"
    )
    email = models.EmailField(
        validators=[validate_guatemala_email],
        verbose_name="Email"
    )
    direccion = models.TextField(
        verbose_name="Dirección"
    )

    # Coordenadas GPS para Google Maps
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

    # Tipo y estado
    tipo_cliente = models.CharField(
        max_length=20,
        choices=TipoClienteChoices.choices,
        default=TipoClienteChoices.INDIVIDUAL,
        verbose_name="Tipo de Cliente"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        db_table = "clientes"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - {self.contacto}"

    @property
    def tiene_coordenadas(self):
        """Verifica si el cliente tiene coordenadas GPS"""
        return self.latitud is not None and self.longitud is not None

    @property
    def es_corporativo(self):
        return self.tipo_cliente == self.TipoClienteChoices.CORPORATIVO

    @property
    def es_individual(self):
        return self.tipo_cliente == self.TipoClienteChoices.INDIVIDUAL

    @property
    def es_gobierno(self):
        return self.tipo_cliente == self.TipoClienteChoices.GOBIERNO
