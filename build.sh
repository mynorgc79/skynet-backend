#!/usr/bin/env bash
# ============================================================================
# SKYNET - BUILD SCRIPT PARA RENDER.COM
# ============================================================================
# Este script se ejecuta automáticamente durante el deployment en Render
# ============================================================================

set -o errexit  # exit on error


# Instalar dependencias de Python
pip install -r requirements/requirements.txt

# Crear directorio de logs si no existe
mkdir -p logs
mkdir -p staticfiles
mkdir -p media

# Ejecutar migraciones de Django
python manage.py migrate --noinput

# Recopilar archivos estáticos
python manage.py collectstatic --noinput --clear

# Crear superusuario si no existe (solo en primera ejecución)
python manage.py shell << EOF
from apps.usuarios.models import Usuario
import os

# Solo crear si no existe ningún administrador
if not Usuario.objects.filter(rol='ADMINISTRADOR').exists():
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@skynet.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    admin = Usuario.objects.create_user(
        email=admin_email,
        password=admin_password,
        nombre='Administrador',
        apellido='Sistema',
        rol='ADMINISTRADOR'
    )
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    print(f"✅ Administrador creado: {admin_email}")
else:
    print("✅ Administrador ya existe")
EOF

echo "✅ Build completado exitosamente!"