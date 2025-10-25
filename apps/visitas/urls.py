"""
SKYNET - URLs del módulo de visitas
"""

from django.urls import path
from .views import (
    # CRUD de visitas
    visitas_list_view,
    visitas_create_view,
    visitas_detail_view,
    visitas_update_view,
    visitas_delete_view,
    # Workflow de visitas
    visitas_iniciar_view,
    visitas_completar_view,
    visitas_cancelar_view,
    # Ejecuciones
    visitas_ejecuciones_list_view,
    visitas_ejecuciones_create_view,
    ejecuciones_update_view
)

app_name = 'visitas'

urlpatterns = [
    # CRUD de visitas - siguiendo la especificación del frontend
    path('', visitas_list_view, name='visitas_list'),
    path('create/', visitas_create_view, name='visitas_create'),
    path('<int:pk>/', visitas_detail_view, name='visitas_detail'),
    path('<int:pk>/update/', visitas_update_view, name='visitas_update'),
    path('<int:pk>/delete/', visitas_delete_view, name='visitas_delete'),
    
    # Workflow de visitas
    path('<int:pk>/iniciar/', visitas_iniciar_view, name='visitas_iniciar'),
    path('<int:pk>/completar/', visitas_completar_view, name='visitas_completar'),
    path('<int:pk>/cancelar/', visitas_cancelar_view, name='visitas_cancelar'),
    
    # Ejecuciones de visitas
    path('<int:pk>/ejecuciones/', visitas_ejecuciones_list_view, name='visitas_ejecuciones_list'),
    path('<int:pk>/ejecuciones/create/', visitas_ejecuciones_create_view, name='visitas_ejecuciones_create'),
    
    # Actualizar ejecuciones específicas
    path('ejecuciones/<int:pk>/update/', ejecuciones_update_view, name='ejecuciones_update'),
]