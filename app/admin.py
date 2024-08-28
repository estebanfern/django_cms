from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from django.contrib import admin, messages
from app.models import CustomUser



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
    list_display = ('name', 'email', 'is_active')
    actions = [bloquear_usuarios, desbloquear_usuarios]
    def has_module_permission(self, request):
        return request.user.is_staff and request.user.has_perm('app.manage_users')

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff and request.user.has_perm('app.manage_users')

    def has_add_permission(self, request):
        return request.user.is_staff and request.user.has_perm('app.manage_users')

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff and request.user.has_perm('app.manage_users')

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff and request.user.has_perm('app.manage_users')


class CustomGroupAdmin(BaseGroupAdmin):
    def has_module_permission(self, request):
        return request.user.is_staff and request.user.has_perm('app.manage_roles')

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff and request.user.has_perm('app.manage_roles')

    def has_add_permission(self, request):
        return request.user.is_staff and request.user.has_perm('app.manage_roles')

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff and request.user.has_perm('app.manage_roles')

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff and request.user.has_perm('app.manage_roles')

# Desregistrar el modelo Group
admin.site.unregister(Group)

# Registrar el modelo Group con la clase CustomGroupAdmin
admin.site.register(Group, CustomGroupAdmin)