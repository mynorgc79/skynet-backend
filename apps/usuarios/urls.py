"""
SKYNET - URLs del módulo de usuarios
"""

from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Autenticación personalizada
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Usuario autenticado
    path('me/', views.me_view, name='me'),
    path('validate-token/', views.validate_token_view, name='validate_token'),
    path('change-password/', views.change_password_view, name='change_password'),
]
