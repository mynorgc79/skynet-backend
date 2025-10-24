"""
SKYNET - Modelos del módulo de usuarios
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from apps.utils.models import TimestampedModel
from apps.utils.validators import validate_guatemala_phone, validate_guatemala_email
from .managers import UsuarioManager


class Usuario(AbstractBaseUser, PermissionsMixin, TimestampedModel):
    """
    Modelo de Usuario personalizado basado en el diagrama ER
    """

    class RolChoices(models.TextChoices):
        ADMINISTRADOR = 'ADMINISTRADOR', 'Administrador'
        SUPERVISOR = 'SUPERVISOR', 'Supervisor'
        TECNICO = 'TECNICO', 'Técnico'

    # Campos básicos
    email = models.EmailField(
        unique=True,
        validators=[validate_guatemala_email],
        verbose_name="Email"
    )
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre"
    )
    apellido = models.CharField(
        max_length=100,
        verbose_name="Apellido"
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        validators=[validate_guatemala_phone],
        verbose_name="Teléfono"
    )

    # Rol y estado
    rol = models.CharField(
        max_length=20,
        choices=RolChoices.choices,
        default=RolChoices.TECNICO,
        verbose_name="Rol"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )

    # Campos para Django Auth
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Manager personalizado
    objects = UsuarioManager()

    # Configuración de autenticación
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        db_table = "usuarios"
        ordering = ['nombre', 'apellido']

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.email})"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def es_administrador(self):
        return self.rol == self.RolChoices.ADMINISTRADOR

    @property
    def es_supervisor(self):
        return self.rol == self.RolChoices.SUPERVISOR

    @property
    def es_tecnico(self):
        return self.rol == self.RolChoices.TECNICO

    @property
    def is_active(self):
        """Propiedad para compatibilidad con Django Auth"""
        return self.activo

    @is_active.setter
    def is_active(self, value):
        """Setter para compatibilidad con Django Auth"""
        self.activo = value
