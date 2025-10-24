"""
SKYNET - Modelos base y mixins comunes
"""

from django.db import models
from django.contrib.auth import get_user_model


class TimestampedModel(models.Model):
    """
    Modelo abstracto que agrega campos de timestamp
    """
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Actualización")

    class Meta:
        abstract = True


class AuditModel(TimestampedModel):
    """
    Modelo abstracto que agrega campos de auditoría
    """
    creado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_creados',
        verbose_name="Creado Por"
    )
    modificado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_modificados',
        verbose_name="Modificado Por"
    )

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    """
    Manager para manejar soft delete
    """

    def get_queryset(self):
        return super().get_queryset().filter(eliminado=False)

    def get_all(self):
        return super().get_queryset()

    def get_deleted(self):
        return super().get_queryset().filter(eliminado=True)


class SoftDeleteModel(models.Model):
    """
    Modelo abstracto que implementa soft delete
    """
    eliminado = models.BooleanField(default=False, verbose_name="Eliminado")
    fecha_eliminacion = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha de Eliminación")

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Override del método delete para implementar soft delete"""
        from django.utils import timezone
        self.eliminado = True
        self.fecha_eliminacion = timezone.now()
        self.save()

    def hard_delete(self):
        """Método para eliminación física"""
        super().delete()

    def restore(self):
        """Método para restaurar un registro eliminado"""
        self.eliminado = False
        self.fecha_eliminacion = None
        self.save()


class BaseModel(AuditModel, SoftDeleteModel):
    """
    Modelo base que combina auditoría y soft delete
    """
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        abstract = True
