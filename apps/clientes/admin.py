"""
SKYNET - Configuración del admin de clientes
"""

from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Cliente
    """
    list_display = [
        'nombre',
        'contacto',
        'email',
        'telefono',
        'tipo_cliente',
        'activo',
        'tiene_coordenadas',
        'fecha_creacion'
    ]

    list_filter = [
        'tipo_cliente',
        'activo',
        'fecha_creacion'
    ]

    search_fields = [
        'nombre',
        'contacto',
        'email',
        'telefono'
    ]

    readonly_fields = [
        'fecha_creacion',
        'fecha_actualizacion'
    ]

    fieldsets = (
        ('Información Básica', {
            'fields': (
                'nombre',
                'contacto',
                'email',
                'telefono'
            )
        }),
        ('Ubicación', {
            'fields': (
                'direccion',
                'latitud',
                'longitud'
            )
        }),
        ('Configuración', {
            'fields': (
                'tipo_cliente',
                'activo'
            )
        }),
        ('Metadatos', {
            'fields': (
                'fecha_creacion',
                'fecha_actualizacion'
            ),
            'classes': ('collapse',)
        })
    )

    ordering = ['nombre']
