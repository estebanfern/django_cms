from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.backends.base.schema import logger
from cms.settings import DEFAULT_PROFILE_PHOTO
from django.utils import timezone
from django.contrib.auth.models import Group
from cms.store_backends import PublicMediaStorage

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener un email.')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.photo = DEFAULT_PROFILE_PHOTO
        user.save(using=self._db)

        try:
            default_group = Group.objects.get(name='Suscriptor')
            user.groups.add(default_group)
        except Group.DoesNotExist:
            Group.objects.create(name='Suscriptor')
            default_group = Group.objects.get(name='Suscriptor')
            user.groups.add(default_group)
            logger.warn(f'Group Suscriptor not exists, creating...')

        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='profile_pics/', storage=PublicMediaStorage, null=True, blank=True)
    about = models.CharField(max_length=255, null=True, blank=True, default='')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    # is_staff = models.BooleanField(default=False)
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

    @property
    def is_staff(self):
        return self.is_admin()

    def __str__(self):
        return self.email

    # Agreguen los permisos que habilitan ver el sidebar
    __creator_perms = {
        "app.create_content",
        "app.edit_content",
        "app.publish_content",
        "app.create_roles",
        "app.edit_roles",
        "app.delete_roles",
        "app.assign_roles",
        "app.remove_roles",
        "app.view_roles",
        "app.edit_users",
        "app.delete_users",
        "app.block_users",
        "app.unblock_users",
        "app.view_users",
    }
    def is_creator(self):
        for auth in self.__creator_perms:
            if self.has_perm(auth):
                return True
        return False

    # Agreguen los permisos que habilitan ver el panel de administración
    __admin_perms = {
        "app.create_roles",
        "app.edit_roles",
        "app.delete_roles",
        "app.assign_roles",
        "app.remove_roles",
        "app.view_roles",
        "app.edit_users",
        "app.delete_users",
        "app.block_users",
        "app.unblock_users",
        "app.view_users",
    }
    def is_admin(self):
        for auth in self.__admin_perms:
            if self.has_perm(auth):
                return True
        return False

    def get_groups_string(self):
        return ' - '.join(self.groups.values_list('name', flat=True))
