from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin, UserAdmin
from django.contrib.auth.models import Group
from django.contrib import admin, messages
from app.models import CustomUser
from django.utils.translation import gettext_lazy as _
from django.forms.models import fields_for_model
from app.forms import CustomUserFormAdmin

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


class CustomUserAdmin(UserAdmin):

    form = CustomUserFormAdmin

    list_display = ('email', 'name', 'is_active')
    list_filter = ('is_active', 'groups')

    fieldsets = (
        (None, {'fields': ()}),
        (_('Informacion personal'), {'fields': ('name', 'email' ,'photo', 'about')}),
        (_('Grupos y estado'), {'fields': ('is_active', 'groups')}),
        (_('Fechas relevantes'), {'fields': ('last_login', 'date_joined')}),
    )
    search_fields = ('email', 'name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

    readonly_fields = ('name', 'email', 'photo', 'about', 'last_login', 'date_joined')

    def has_module_permission(self, request):
        return request.user.is_staff and request.user.has_perm('app.view_users')

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff and request.user.has_perm('app.view_users')

    def has_add_permission(self, request):
        return request.user.is_staff and request.user.has_perm('app.create_users')

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff and request.user.has_perm('app.edit_roles')

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff and request.user.has_perm('app.delete_users')

 # Restringir la edición solo a 'groups' e 'is_active'
    def get_readonly_fields(self, request, obj=None):
        if obj:
            # Obtener todos los campos del modelo
            all_fields = list(fields_for_model(self.model).keys())
            editable_fields = {'groups', 'is_active'}
            return [field for field in all_fields if field not in editable_fields]
        return super().get_readonly_fields(request, obj)


admin.site.register(CustomUser, CustomUserAdmin)

class CustomGroupAdmin(BaseGroupAdmin):
    def has_module_permission(self, request):
        return request.user.is_staff and request.user.has_perm('app.view_roles')

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff and request.user.has_perm('app.view_roles')

    def has_add_permission(self, request):
        return request.user.is_staff and request.user.has_perm('app.create_roles')

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff and request.user.has_perm('app.edit_roles')

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff and request.user.has_perm('app.delete_roles')

# Desregistrar el modelo Group
admin.site.unregister(Group)

# Registrar el modelo Group con la clase CustomGroupAdmin
admin.site.register(Group, CustomGroupAdmin)

admin.site.site_header = "Administración del Sistema"