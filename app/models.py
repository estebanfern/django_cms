from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.contrib.auth.models import Group


# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener un email.')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        try:
            default_group = Group.objects.get(name='Suscriptor')
            user.groups.add(default_group)
        except Group.DoesNotExist:
            raise ValueError('El grupo "Suscriptor" no existe.')

        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    about = models.CharField(max_length=255, null=True, blank=True, default='')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        permissions = [
            # Permisos para contenido
            ("create_content", "Crear contenidos"),
            ("edit_content", "Editar contenidos"),
            ("publish_content", "Publicar contenidos"),
            ("comment_post", "Comentar contenidos"),
            ("react_to_post", "Reaccionar a contenidos"),
            ("report_post","Reportar contenidos"),

            # Permisos para roles
            ("create_roles", "Crear roles"),
            ("edit_roles", "Editar roles"),
            ("delete_roles", "Eliminar roles"),
            ("assign_roles", "Asignar roles a usuarios"),
            ("remove_roles", "Quitar roles a usuarios"),
            ("view_roles", "Ver roles"),

            # Permisos para usuarios
            ("create_users", "Crear usuarios"),
            ("edit_users", "Editar usuarios"),
            ("delete_users", "Eliminar usuarios"),
            ("block_users", "Bloquear usuarios"),
            ("unblock_users", "Desbloquear usuarios"),
            ("reset_passwords", "Restablecer contraseñas"),
            ("view_users", "Ver usuarios"),

        ]

    def __str__(self):
        return self.email



