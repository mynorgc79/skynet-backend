"""
SKYNET - Utilidades comunes del sistema
Exceptions handlers, mixins, validators, etc.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger('apps')


def custom_exception_handler(exc, context):
    """
    Custom exception handler para mantener consistencia en las respuestas de la API
    """
    # Obtener la respuesta base de DRF
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            'success': False,
            'data': None,
            'message': 'Error en la solicitud',
            'errors': []
        }

        # Manejar diferentes tipos de errores
        if hasattr(response.data, 'get'):
            if 'detail' in response.data:
                custom_response_data['message'] = str(response.data['detail'])
            elif 'non_field_errors' in response.data:
                custom_response_data['errors'] = response.data['non_field_errors']
            else:
                # Errores de validación de campos
                errors = []
                for field, field_errors in response.data.items():
                    if isinstance(field_errors, list):
                        for error in field_errors:
                            errors.append(f"{field}: {error}")
                    else:
                        errors.append(f"{field}: {field_errors}")
                custom_response_data['errors'] = errors
        else:
            custom_response_data['message'] = str(response.data)

        # Log del error
        logger.error(f"API Error: {exc} - Context: {context}")

        response.data = custom_response_data

    return response


class StandardResponseMixin:
    """
    Mixin para estandarizar las respuestas de la API
    """

    def success_response(self, data=None, message="Operación exitosa", status_code=status.HTTP_200_OK):
        """Respuesta estándar para operaciones exitosas"""
        return Response({
            'success': True,
            'data': data,
            'message': message,
            'errors': []
        }, status=status_code)

    def error_response(self, message="Error en la operación", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        """Respuesta estándar para errores"""
        return Response({
            'success': False,
            'data': None,
            'message': message,
            'errors': errors or []
        }, status=status_code)


class AuditMixin:
    """
    Mixin para agregar campos de auditoría automáticamente
    """

    def perform_create(self, serializer):
        """Agregar usuario creador"""
        serializer.save(creado_por=self.request.user)

    def perform_update(self, serializer):
        """Agregar usuario modificador"""
        serializer.save(modificado_por=self.request.user)
