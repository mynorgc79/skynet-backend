"""
SKYNET - Configuración del admin de visitas
"""

from django.contrib import admin
from .models import Visita, Ejecucion


class EjecucionInline(admin.TabularInline):
    """
    Inline para mostrar ejecuciones en el admin de Visita
    """
    model = Ejecucion
    extra = 0
    readonly_fields = ['fecha_creacion']
    fields = [
        'descripcion',
        'tiempo_inicio',
        'tiempo_fin',
        'completada',
        'observaciones',
        'evidencia_foto'
    ]


@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Visita
    """
    list_display = [
        'id',
        'cliente',
        'tecnico',
        'supervisor',
        'fecha_programada',
        'estado',
        'tipo_visita',
        'duracion_minutos',
        'tiene_coordenadas'
    ]
    
    list_filter = [
        'estado',
        'tipo_visita',
        'fecha_programada',
        'tecnico__rol',
        'fecha_creacion'
    ]
    
    search_fields = [
        'cliente__nombre',
        'tecnico__nombre',
        'tecnico__apellido',
        'supervisor__nombre',
        'descripcion'
    ]
    
    readonly_fields = [
        'fecha_creacion',
        'fecha_actualizacion',
        'duracion_minutos'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'cliente',
                'tecnico',
                'supervisor',
                'fecha_programada'
            )
        }),
        ('Detalles de la Visita', {
            'fields': (
                'tipo_visita',
                'estado',
                'descripcion',
                'observaciones'
            )
        }),
        ('Seguimiento', {
            'fields': (
                'fecha_inicio',
                'fecha_fin',
                'latitud',
                'longitud'
            )
        }),
        ('Metadatos', {
            'fields': (
                'fecha_creacion',
                'fecha_actualizacion',
                'duracion_minutos'
            ),
            'classes': ('collapse',)
        })
    )
    
    inlines = [EjecucionInline]
    ordering = ['-fecha_programada']
    date_hierarchy = 'fecha_programada'
    
    def get_queryset(self, request):
        """Optimizar queryset con select_related"""
        return super().get_queryset(request).select_related('cliente', 'tecnico', 'supervisor')


@admin.register(Ejecucion)
class EjecucionAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Ejecucion
    """
    list_display = [
        'id',
        'visita',
        'descripcion_corta',
        'tiempo_inicio',
        'tiempo_fin',
        'completada',
        'duracion_minutos'
    ]
    
    list_filter = [
        'completada',
        'tiempo_inicio',
        'visita__estado',
        'visita__tipo_visita'
    ]
    
    search_fields = [
        'descripcion',
        'visita__cliente__nombre',
        'visita__tecnico__nombre',
        'observaciones'
    ]
    
    readonly_fields = [
        'fecha_creacion',
        'fecha_actualizacion',
        'duracion_minutos'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'visita',
                'descripcion'
            )
        }),
        ('Tiempos', {
            'fields': (
                'tiempo_inicio',
                'tiempo_fin',
                'completada'
            )
        }),
        ('Detalles', {
            'fields': (
                'observaciones',
                'evidencia_foto'
            )
        }),
        ('Metadatos', {
            'fields': (
                'fecha_creacion',
                'fecha_actualizacion',
                'duracion_minutos'
            ),
            'classes': ('collapse',)
        })
    )
    
    ordering = ['-tiempo_inicio']
    date_hierarchy = 'tiempo_inicio'
    
    def descripcion_corta(self, obj):
        """Mostrar descripción corta en la lista"""
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = 'Descripción'
    
    def get_queryset(self, request):
        """Optimizar queryset con select_related"""
        return super().get_queryset(request).select_related('visita', 'visita__cliente', 'visita__tecnico')