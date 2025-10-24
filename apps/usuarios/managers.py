from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UsuarioManager(BaseUserManager):
    """Manager personalizado para el modelo Usuario."""

    def create_user(self, email, nombre, apellido, password=None, **extra_fields):
        """Crea y retorna un usuario regular."""
        if not email:
            raise ValueError(_('El usuario debe tener un email'))
        if not nombre:
            raise ValueError(_('El usuario debe tener un nombre'))
        if not apellido:
            raise ValueError(_('El usuario debe tener un apellido'))

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            nombre=nombre,
            apellido=apellido,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nombre, apellido, password=None, **extra_fields):
        """Crea y retorna un superusuario (administrador)."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('activo', True)
        extra_fields.setdefault('rol', 'ADMINISTRADOR')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('El superusuario debe tener is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(
                _('El superusuario debe tener is_superuser=True.'))

        return self.create_user(email, nombre, apellido, password, **extra_fields)

    def get_by_email(self, email):
        """Obtener usuario por email."""
        try:
            return self.get(email=email)
        except self.model.DoesNotExist:
            return None

    def administradores(self):
        """Retorna solo los administradores."""
        return self.filter(rol='ADMINISTRADOR', activo=True)

    def supervisores(self):
        """Retorna solo los supervisores."""
        return self.filter(rol='SUPERVISOR', activo=True)

    def tecnicos(self):
        """Retorna solo los técnicos."""
        return self.filter(rol='TECNICO', activo=True)

    def activos(self):
        """Retorna solo los usuarios activos."""
        return self.filter(activo=True)

    def por_rol(self, rol):
        """Obtener usuarios por rol."""
        return self.filter(rol=rol, activo=True)
