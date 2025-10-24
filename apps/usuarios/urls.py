"""
SKYNET - URLs del módulo de usuarios
"""

from django.urls import path
from . import views
from .views import (
    login_view, logout_view, me_view, validate_token_view, change_password_view,
    usuarios_list_view, usuarios_create_view, usuarios_detail_view,
    usuarios_update_view, usuarios_delete_view, usuarios_toggle_status_view
)

app_name = 'usuarios'

urlpatterns = [
    # Autenticación personalizada
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Usuario autenticado
    path('me/', me_view, name='me'),
    path('validate-token/', validate_token_view, name='validate_token'),
    path('change-password/', change_password_view, name='change_password'),

    # CRUD de usuarios - reorganizados para evitar conflictos
    path('usuarios/create/', usuarios_create_view, name='usuarios_create'),
    path('usuarios/<int:pk>/update/',
         usuarios_update_view, name='usuarios_update'),
    path('usuarios/<int:pk>/delete/',
         usuarios_delete_view, name='usuarios_delete'),
    path('usuarios/<int:pk>/toggle-status/',
         usuarios_toggle_status_view, name='usuarios_toggle_status'),
    path('usuarios/<int:pk>/', usuarios_detail_view, name='usuarios_detail'),
    path('usuarios/', usuarios_list_view,
         name='usuarios_list'),  # Esta debe ir al final
]
