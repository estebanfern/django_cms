from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.backends.base.schema import logger
from cms.profile.base import DEFAULT_PROFILE_PHOTO
from django.utils import timezone
from django.contrib.auth.models import Group
from cms.store_backends import PublicMediaStorage


class CustomUserManager(BaseUserManager):
    """
    Gestor personalizado para el modelo de usuario, que define métodos para la creación de usuarios y su manejo.

    Métodos:
        create_user: Crea y guarda un usuario con el correo electrónico, nombre y contraseña proporcionados.
    """

    def create_user(self, email, name, password=None, **extra_fields):
        """
        Crea y guarda un usuario con el correo electrónico, nombre y contraseña proporcionados.

        Parámetros:
            email (str): Correo electrónico del usuario.
            name (str): Nombre del usuario.
            password (str, opcional): Contraseña del usuario.
            \*\*extra_fields: Campos adicionales para el modelo de usuario.

        Acciones:
            - Normaliza el correo electrónico.
            - Establece la contraseña y la foto de perfil predeterminada.
            - Intenta agregar el usuario al grupo 'Suscriptor', creándolo si no existe.
            - Muestra una advertencia en el registro si el grupo 'Suscriptor' no existe y se crea.

        Retorna:
            CustomUser: El usuario creado.
        """

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
    """
    Modelo de usuario personalizado que extiende AbstractBaseUser y PermissionsMixin.

    Atributos:
        email (EmailField): Campo de correo electrónico único para el usuario.
        name (CharField): Campo de texto para el nombre del usuario.
        photo (ImageField): Campo de imagen para la foto de perfil del usuario.
        about (CharField): Campo de texto para la descripción del usuario.
        is_active (BooleanField): Indica si el usuario está activo.
        date_joined (DateTimeField): Fecha de registro del usuario.

    Configuración:
        USERNAME_FIELD: Campo que se utiliza como identificador único (correo electrónico).
        REQUIRED_FIELDS: Campos obligatorios adicionales para el registro (nombre).

    Meta:
        verbose_name: Nombre legible para el modelo en singular.
        verbose_name_plural: Nombre legible para el modelo en plural.
        permissions: Lista de permisos personalizados asociados al modelo de usuario.
    """

    email = models.EmailField(unique=True, verbose_name=('Correo Electrónico'))
    name = models.CharField(max_length=255, verbose_name=('Nombre'))
    photo = models.ImageField(upload_to='profile_pics/', storage=PublicMediaStorage, null=True, blank=True,verbose_name=('Foto de perfil'))
    about = models.CharField(max_length=255, null=True, blank=True, default='', verbose_name=('Acerca de'))
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    date_joined = models.DateTimeField(default=timezone.now, verbose_name=('Fecha de registro'))

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
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

            # Permisos para categorías
            ("create_category", "Crear categorías"),
            ("view_category", "Ver categorías"),
            ("edit_category", "Editar categorías"),
            ("delete_category", "Eliminar categorías"),
            ("activate_category", "Activar categorías"),
            ("deactivate_category", "Desactivar categorías"),

        ]

    @property
    def is_staff(self):
        """
        Propiedad que indica si el usuario es parte del personal (staff).

        Retorna:
            bool: True si el usuario tiene permisos de administrador, de lo contrario False.
        """

        return self.is_admin()

    def __str__(self):
        """
        Devuelve una representación en cadena del usuario.

        Retorna:
            str: El correo electrónico del usuario.
        """

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
        """
        Verifica si el usuario tiene permisos para ver el sidebar (creador).

        Acciones:
            - Itera sobre un conjunto de permisos específicos para los creadores y verifica si el usuario tiene alguno de ellos.

        Retorna:
            bool: True si el usuario tiene alguno de los permisos de creador, de lo contrario False.
        """

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
        """
        Verifica si el usuario tiene permisos para ver el panel de administración.

        Acciones:
            - Itera sobre un conjunto de permisos específicos para los administradores y verifica si el usuario tiene alguno de ellos.

        Retorna:
            bool: True si el usuario tiene alguno de los permisos de administrador, de lo contrario False.
        """

        for auth in self.__admin_perms:
            if self.has_perm(auth):
                return True
        return False

    def get_groups_string(self):
        """
        Obtiene una cadena con los nombres de los grupos a los que pertenece el usuario.

        Retorna:
            str: Una cadena con los nombres de los grupos separados por ' - '.
        """

        return ' - '.join(self.groups.values_list('name', flat=True))
