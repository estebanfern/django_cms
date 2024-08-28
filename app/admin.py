from django.contrib import admin, messages
from app.models import CustomUser

# Register your models here.


@admin.action(description="Bloquear usuario/s")
def bloquear_usuarios(self, request, queryset):
    for usuario in queryset:
        if usuario.is_active:
            usuario.is_active = False
            usuario.save()
            self.message_user(request, f'El usuario {usuario.name} ha sido bloqueado.', messages.SUCCESS)


@admin.action(description="Desbloquear usuario/s")
def desbloquear_usuarios(self, request, queryset):
    for usuario in queryset:
        if not usuario.is_active:
            usuario.is_active = True
            usuario.save()
            self.message_user(request, f'El usuario {usuario.name} ha sido desbloqueado.', messages.SUCCESS)


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'role', 'is_active')
    actions = [bloquear_usuarios, desbloquear_usuarios]


