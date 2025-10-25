"""
SKYNET - URLs del módulo de clientes
"""

from django.urls import path
from .views import (
    clientes_list_view,
    clientes_create_view,
    clientes_detail_view,
    clientes_update_view,
    clientes_delete_view
)

app_name = 'clientes'

urlpatterns = [
    # CRUD de clientes - siguiendo la especificación del frontend
    path('', clientes_list_view, name='clientes_list'),
    path('create/', clientes_create_view, name='clientes_create'),
    path('<int:pk>/', clientes_detail_view, name='clientes_detail'),
    path('<int:pk>/update/', clientes_update_view, name='clientes_update'),
    path('<int:pk>/delete/', clientes_delete_view, name='clientes_delete'),
]
