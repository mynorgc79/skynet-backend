"""
SKYNET - Configuración del admin para usuarios
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Configuración del admin para el modelo Usuario
    """
    list_display = [
        'email',
        'nombre',
        'apellido',
        'rol',
        'activo',
        'is_staff',
        'fecha_creacion'
    ]
    list_filter = [
        'rol',
        'activo',
        'is_staff',
        'is_superuser',
        'fecha_creacion'
    ]
    search_fields = [
        'email',
        'nombre',
        'apellido',
        'telefono'
    ]
    ordering = ['email']

    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'telefono')
        }),
        ('Permisos', {
            'fields': ('rol', 'activo', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas importantes', {
            'fields': ('last_login', 'fecha_creacion', 'fecha_actualizacion')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'apellido', 'telefono', 'rol', 'password1', 'password2'),
        }),
    )

    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ['email']
        return self.readonly_fields
