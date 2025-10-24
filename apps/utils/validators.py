"""
SKYNET - Validadores comunes
"""

import re
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model


def validate_guatemala_phone(value):
    """
    Validador para números de teléfono de Guatemala
    Formato: +502 XXXX-XXXX o 502 XXXX-XXXX o XXXX-XXXX
    """
    # Remover espacios y guiones
    clean_value = re.sub(r'[\s\-\+]', '', value)

    # Patrones válidos para Guatemala
    patterns = [
        r'^502\d{8}$',      # 502XXXXXXXX
        r'^\d{8}$',         # XXXXXXXX (número local)
        r'^502\d{4}\d{4}$',  # 502XXXXXXXX
    ]

    if not any(re.match(pattern, clean_value) for pattern in patterns):
        raise ValidationError(
            'Ingrese un número de teléfono válido para Guatemala. '
            'Formatos válidos: +502 XXXX-XXXX, 502 XXXX-XXXX, o XXXX-XXXX'
        )


def validate_guatemala_email(value):
    """
    Validador básico para emails
    """
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, value):
        raise ValidationError('Ingrese un email válido.')


def validate_coordinates(latitude, longitude):
    """
    Validador para coordenadas GPS
    Guatemala está aproximadamente entre:
    Latitud: 13.7° a 17.8° N
    Longitud: 87.4° a 92.3° O
    """
    if latitude is not None:
        if not (13.0 <= latitude <= 18.0):
            raise ValidationError(
                'La latitud debe estar entre 13.0° y 18.0° para Guatemala.')

    if longitude is not None:
        if not (-93.0 <= longitude <= -87.0):
            raise ValidationError(
                'La longitud debe estar entre -93.0° y -87.0° para Guatemala.')


def validate_strong_password(password):
    """
    Validador para contraseñas fuertes
    """
    if len(password) < 8:
        raise ValidationError(
            'La contraseña debe tener al menos 8 caracteres.')

    if not re.search(r'[A-Z]', password):
        raise ValidationError(
            'La contraseña debe contener al menos una letra mayúscula.')

    if not re.search(r'[a-z]', password):
        raise ValidationError(
            'La contraseña debe contener al menos una letra minúscula.')

    if not re.search(r'\d', password):
        raise ValidationError(
            'La contraseña debe contener al menos un número.')

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError(
            'La contraseña debe contener al menos un carácter especial.')


def validate_unique_email(email, user_id=None):
    """
    Validador para email único en el sistema
    """
    User = get_user_model()
    queryset = User.objects.filter(email=email)

    if user_id:
        queryset = queryset.exclude(id=user_id)

    if queryset.exists():
        raise ValidationError('Este email ya está registrado en el sistema.')


def validate_positive_number(value):
    """
    Validador para números positivos
    """
    if value <= 0:
        raise ValidationError('El valor debe ser mayor a cero.')
