"""
SKYNET - Serializers para el módulo de usuarios
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from apps.utils.validators import validate_guatemala_phone, validate_guatemala_email
from .models import Usuario


class LoginSerializer(serializers.Serializer):
    """
    Serializer para login de usuarios
    """
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # Buscar usuario por email
            try:
                user = Usuario.objects.get(email=email)
            except Usuario.DoesNotExist:
                raise serializers.ValidationError(
                    'Email o contraseña incorrectos.'
                )

            # Verificar contraseña
            if not user.check_password(password):
                raise serializers.ValidationError(
                    'Email o contraseña incorrectos.'
                )

            if not user.activo:
                raise serializers.ValidationError(
                    'Esta cuenta está inactiva.'
                )

            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Debe incluir email y contraseña.'
            )


class CustomTokenObtainPairSerializer(serializers.Serializer):
    """
    Serializer personalizado para JWT tokens - Implementación manual
    """
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        # Obtener credenciales
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError(
                'Email y contraseña son requeridos.')

        # Buscar usuario por email
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError('Credenciales inválidas.')

        # Verificar contraseña
        if not user.check_password(password):
            raise serializers.ValidationError('Credenciales inválidas.')

        if not user.activo:
            raise serializers.ValidationError('Esta cuenta está inactiva.')

        # Actualizar último login
        from django.utils import timezone
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        # Generar tokens JWT manualmente usando PyJWT
        import jwt
        from django.conf import settings
        from datetime import datetime, timedelta

        # Payload del access token
        access_payload = {
            'user_id': user.id,
            'email': user.email,
            'nombre': user.nombre,
            'apellido': user.apellido,
            'rol': user.rol,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow(),
            'token_type': 'access'
        }

        # Payload del refresh token
        refresh_payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=7),
            'iat': datetime.utcnow(),
            'token_type': 'refresh'
        }

        # Generar tokens
        access_token = jwt.encode(
            access_payload, settings.SECRET_KEY, algorithm='HS256')
        refresh_token = jwt.encode(
            refresh_payload, settings.SECRET_KEY, algorithm='HS256')

        return {
            'access': access_token,
            'refresh': refresh_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'nombre': user.nombre,
                'apellido': user.apellido,
                'nombre_completo': user.nombre_completo,
                'rol': user.rol,
                'activo': user.activo,
            }
        }


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer básico para mostrar información del usuario
    """
    nombre_completo = serializers.ReadOnlyField()

    class Meta:
        model = Usuario
        fields = [
            'id',
            'email',
            'nombre',
            'apellido',
            'nombre_completo',
            'telefono',
            'rol',
            'activo',
            'fecha_creacion',
            'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']


class UsuarioCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear usuarios con validaciones completas
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text="Mínimo 8 caracteres"
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Debe coincidir con la contraseña"
    )

    class Meta:
        model = Usuario
        fields = [
            'email',
            'nombre',
            'apellido',
            'telefono',
            'rol',
            'password',
            'confirm_password'
        ]

    def validate_email(self, value):
        """Validar email único"""
        validate_guatemala_email(value)

        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value

    def validate_telefono(self, value):
        """Validar teléfono guatemalteco"""
        if value:
            validate_guatemala_phone(value)
        return value

    def validate_nombre(self, value):
        """Validar nombre"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError(
                "El nombre debe tener al menos 2 caracteres.")
        return value.strip().title()

    def validate_apellido(self, value):
        """Validar apellido"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError(
                "El apellido debe tener al menos 2 caracteres.")
        return value.strip().title()

    def validate_rol(self, value):
        """Validar rol"""
        roles_validos = [choice[0] for choice in Usuario.RolChoices.choices]
        if value not in roles_validos:
            raise serializers.ValidationError(
                f"Rol inválido. Opciones: {', '.join(roles_validos)}")
        return value

    def validate_password(self, value):
        """Validar fortaleza de contraseña"""
        if len(value) < 8:
            raise serializers.ValidationError(
                "La contraseña debe tener al menos 8 caracteres.")

        # Verificar que tenga al menos una letra
        if not any(c.isalpha() for c in value):
            raise serializers.ValidationError(
                "La contraseña debe contener al menos una letra.")

        # Verificar que tenga al menos un número
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError(
                "La contraseña debe contener al menos un número.")

        return value

    def validate(self, attrs):
        """Validaciones generales"""
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        # Verificar que las contraseñas coincidan
        if password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Las contraseñas no coinciden."}
            )

        # Remover confirm_password antes de crear el usuario
        attrs.pop('confirm_password', None)
        return attrs

    def create(self, validated_data):
        """Crear usuario con contraseña encriptada"""
        password = validated_data.pop('password')

        usuario = Usuario.objects.create_user(
            password=password,
            **validated_data
        )

        return usuario


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar usuarios (sin contraseña)
    """

    class Meta:
        model = Usuario
        fields = [
            'nombre',
            'apellido',
            'telefono',
            'rol',
            'activo'
        ]

    def validate_nombre(self, value):
        """Validar nombre"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError(
                "El nombre debe tener al menos 2 caracteres.")
        return value.strip().title()

    def validate_apellido(self, value):
        """Validar apellido"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError(
                "El apellido debe tener al menos 2 caracteres.")
        return value.strip().title()

    def validate_telefono(self, value):
        """Validar teléfono guatemalteco"""
        if value:
            validate_guatemala_phone(value)
        return value

    def validate_rol(self, value):
        """Validar rol"""
        roles_validos = [choice[0] for choice in Usuario.RolChoices.choices]
        if value not in roles_validos:
            raise serializers.ValidationError(
                f"Rol inválido. Opciones: {', '.join(roles_validos)}")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para cambio de contraseña
    """
    old_password = serializers.CharField(
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        min_length=8,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        style={'input_type': 'password'}
    )

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                'La contraseña actual es incorrecta.'
            )
        return value

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError(
                'Las contraseñas nuevas no coinciden.'
            )

        return attrs
