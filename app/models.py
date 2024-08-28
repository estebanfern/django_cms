from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener un email.')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    # def create_superuser(self, email, name, password=None, **extra_fields):
    #     extra_fields.setdefault('is_staff', True)
    #     extra_fields.setdefault('is_superuser', True)
    #     return self.create_user(email, name, password, **extra_fields)

class Role(models.Model):
    name = models.CharField(max_length=255)
    permissions = models.ManyToManyField('auth.Permission')

    def __str__(self):
        return self.name

    class Meta:
        permissions = [
            ("create_content", "Crear contenidos"),
            ("edit_content", "Editar contenidos"),
            ("publish_content", "Publicar contenidos"),
            ("manage_roles", "Gestionar roles"),
        ]

# def get_default_role():
#     return Role.objects.get_or_create(name='SUSCRIPTOR')[0]

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

