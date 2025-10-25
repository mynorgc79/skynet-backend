"""
SKYNET - Serializers del módulo de clientes
"""

from rest_framework import serializers
from .models import Cliente


class ClienteSerializer(serializers.ModelSerializer):
    """
    Serializer para lectura de datos de Cliente
    Estructura compatible con el frontend Angular
    """

    # Campos adicionales para compatibilidad frontend
    idCliente = serializers.IntegerField(source='id', read_only=True)
    tipoCliente = serializers.CharField(source='tipo_cliente', read_only=True)
    fechaCreacion = serializers.DateTimeField(
        source='fecha_creacion', read_only=True)
    fechaActualizacion = serializers.DateTimeField(
        source='fecha_actualizacion', read_only=True)

    class Meta:
        model = Cliente
        fields = [
            'idCliente',
            'nombre',
            'contacto',
            'telefono',
            'email',
            'direccion',
            'latitud',
            'longitud',
            'tipoCliente',
            'activo',
            'fechaCreacion',
            'fechaActualizacion'
        ]


class ClienteCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para creación de Cliente con validaciones
    """

    class Meta:
        model = Cliente
        fields = [
            'nombre',
            'contacto',
            'telefono',
            'email',
            'direccion',
            'latitud',
            'longitud',
            'tipo_cliente'
        ]

    def validate_email(self, value):
        """Validar que el email sea único"""
        if Cliente.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Ya existe un cliente con este email.")
        return value

    def validate_nombre(self, value):
        """Validar nombre del cliente"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "El nombre debe tener al menos 2 caracteres.")
        return value.strip().title()

    def validate_contacto(self, value):
        """Validar nombre del contacto"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "El contacto debe tener al menos 2 caracteres.")
        return value.strip().title()

    def validate_direccion(self, value):
        """Validar dirección"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "La dirección debe ser más específica (mínimo 10 caracteres).")
        return value.strip()

    def validate(self, attrs):
        """Validaciones cruzadas"""
        latitud = attrs.get('latitud')
        longitud = attrs.get('longitud')

        # Si se proporciona una coordenada, ambas deben estar presentes
        if (latitud is not None and longitud is None) or (latitud is None and longitud is not None):
            raise serializers.ValidationError({
                'coordenadas': 'Debe proporcionar tanto latitud como longitud, o ninguna.'
            })

        # Validar rangos de coordenadas para Guatemala
        if latitud is not None:
            if not (13.0 <= float(latitud) <= 18.0):
                raise serializers.ValidationError({
                    'latitud': 'La latitud debe estar en el rango de Guatemala (13.0 - 18.0).'
                })

        if longitud is not None:
            if not (-93.0 <= float(longitud) <= -88.0):
                raise serializers.ValidationError({
                    'longitud': 'La longitud debe estar en el rango de Guatemala (-93.0 - -88.0).'
                })

        return attrs


class ClienteUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualización de Cliente
    """

    class Meta:
        model = Cliente
        fields = [
            'nombre',
            'contacto',
            'telefono',
            'email',
            'direccion',
            'latitud',
            'longitud',
            'tipo_cliente',
            'activo'
        ]

    def validate_email(self, value):
        """Validar que el email sea único (excepto el actual)"""
        cliente_id = self.instance.id if self.instance else None
        if Cliente.objects.filter(email=value).exclude(id=cliente_id).exists():
            raise serializers.ValidationError(
                "Ya existe un cliente con este email.")
        return value

    def validate_nombre(self, value):
        """Validar nombre del cliente"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "El nombre debe tener al menos 2 caracteres.")
        return value.strip().title()

    def validate_contacto(self, value):
        """Validar nombre del contacto"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "El contacto debe tener al menos 2 caracteres.")
        return value.strip().title()

    def validate(self, attrs):
        """Validaciones cruzadas para update"""
        latitud = attrs.get('latitud')
        longitud = attrs.get('longitud')

        # Si se está actualizando coordenadas
        if 'latitud' in attrs or 'longitud' in attrs:
            # Obtener valores actuales si no se proporcionan nuevos
            if latitud is None and self.instance:
                latitud = self.instance.latitud
            if longitud is None and self.instance:
                longitud = self.instance.longitud

            # Validar que ambas coordenadas estén presentes o ambas ausentes
            if (latitud is not None and longitud is None) or (latitud is None and longitud is not None):
                raise serializers.ValidationError({
                    'coordenadas': 'Debe proporcionar tanto latitud como longitud, o ninguna.'
                })

        return attrs
