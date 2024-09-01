from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin, UserAdmin
from django.contrib.auth.models import Group
from django.contrib import admin, messages
from app import models
from app.models import CustomUser
from django.utils.translation import gettext_lazy as _
from django.forms.models import fields_for_model
from app.forms import CustomUserFormAdmin
from django.urls import reverse

@admin.action(description="Bloquear usuario/s")
def bloquear_usuarios(self, request, queryset):
    """
    Bloquea los usuarios seleccionados en el panel de administración.

    Parámetros:
        self: Referencia al objeto actual.
        request: Objeto de solicitud HTTP que contiene metadatos sobre la solicitud.
        queryset: QuerySet que contiene los usuarios seleccionados para la acción.

    Acciones:
        - Itera sobre los usuarios seleccionados y desactiva su cuenta.
        - Muestra un mensaje de éxito por cada usuario bloqueado.
    """

    for usuario in queryset:
        if usuario.is_active:
            usuario.is_active = False
            usuario.save()
            self.message_user(request, f'El usuario {usuario.name} ha sido bloqueado.', messages.SUCCESS)

@admin.action(description="Desbloquear usuario/s")
def desbloquear_usuarios(self, request, queryset):
    """
    Desbloquea los usuarios seleccionados en el panel de administración.

    Parameters:
        self: Referencia al objeto actual.

        request: Objeto de solicitud HTTP que contiene metadatos sobre la solicitud.

        queryset: QuerySet que contiene los usuarios seleccionados para la acción.

    Acciones:
        - Itera sobre los usuarios seleccionados y activa su cuenta.
        - Muestra un mensaje de éxito por cada usuario desbloqueado.
    """
    for usuario in queryset:
        if not usuario.is_active:
            usuario.is_active = True
            usuario.save()
            self.message_user(request, f'El usuario {usuario.name} ha sido desbloqueado.', messages.SUCCESS)


class CustomUserAdmin(UserAdmin):
    """
    Configuración personalizada para la administración de usuarios en el panel de administración de Django.

    Atributos:
        form (ModelForm): Formulario personalizado utilizado para editar usuarios.
        list_display (tuple): Campos que se mostrarán en la lista de usuarios.
        list_filter (tuple): Filtros disponibles en la lista de usuarios.
        fieldsets (tuple): Estructura y agrupación de los campos en el formulario de edición de usuarios.
        search_fields (tuple): Campos por los cuales se puede buscar en la lista de usuarios.
        ordering (tuple): Orden por defecto de la lista de usuarios.
        filter_horizontal (tuple): Campos de selección múltiple que se muestran de manera horizontal.
        readonly_fields (tuple): Campos que son de solo lectura en el formulario de edición.
    """

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

    # Boton de Cancelar al modificar
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        cancel_url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        extra_context['cancel_url'] = cancel_url
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def has_module_permission(self, request):
        """
        Verifica si el usuario actual tiene permisos para acceder al módulo de administración de usuarios.

        Parámetros:
            request: Objeto de solicitud HTTP.

        Retorna:
            bool: True si el usuario tiene permisos de visualización, de lo contrario False.
        """

        return request.user.is_staff and request.user.has_perm('app.view_users')

    def has_view_permission(self, request, obj=None):
        """
        Verifica si el usuario actual tiene permisos para ver usuarios específicos.

        Parámetros:
            request: Objeto de solicitud HTTP.
            obj: Objeto usuario específico (opcional).

        Retorna:
            bool: True si el usuario tiene permisos de visualización, de lo contrario False.
        """

        return request.user.is_staff and request.user.has_perm('app.view_users')

    def has_add_permission(self, request):
        """
        Verifica si el usuario actual tiene permisos para añadir nuevos usuarios.

        Parámetros:
            request: Objeto de solicitud HTTP.

        Retorna:
            bool: True si el usuario tiene permisos para añadir usuarios, de lo contrario False.
        """

        return request.user.is_staff and request.user.has_perm('app.create_users')

    def has_change_permission(self, request, obj=None):
        """
        Verifica si el usuario actual tiene permisos para cambiar usuarios.

        Parámetros:
            request: Objeto de solicitud HTTP.
            obj: Objeto usuario específico (opcional).

        Retorna:
            bool: True si el usuario tiene permisos para cambiar usuarios, de lo contrario False.
        """

        return request.user.is_staff and request.user.has_perm('app.edit_roles')

    def has_delete_permission(self, request, obj=None):
        """
        Verifica si el usuario actual tiene permisos para eliminar usuarios.

        Parámetros:
            request: Objeto de solicitud HTTP.
            obj: Objeto usuario específico (opcional).

        Retorna:
            bool: True si el usuario tiene permisos para eliminar usuarios, de lo contrario False.
        """

        return request.user.is_staff and request.user.has_perm('app.delete_users')

 # Restringir la edición solo a 'groups' e 'is_active'
    def get_readonly_fields(self, request, obj=None):
        """
        Restringe la edición a solo los campos 'groups' e 'is_active', dejando los demás como solo lectura.

        Parámetros:
            request: Objeto de solicitud HTTP.
            obj: Objeto usuario específico (opcional).

        Retorna:
            list: Lista de campos de solo lectura.
        """

        if obj:
            # Obtener todos los campos del modelo
            all_fields = list(fields_for_model(self.model).keys())
            editable_fields = {'groups', 'is_active'}
            return [field for field in all_fields if field not in editable_fields]
        return super().get_readonly_fields(request, obj)


class CustomGroupAdmin(BaseGroupAdmin):
    # Boton de Cancelar al modificar
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        cancel_url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        extra_context['cancel_url'] = cancel_url
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
    
    # Boton de Cancelar al agregar
    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        cancel_url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        extra_context['cancel_url'] = cancel_url
        return super().add_view(request, form_url, extra_context=extra_context)
    """
    Configuración personalizada para la administración de grupos en el panel de administración de Django.

    Hereda de:
        BaseGroupAdmin: La clase base de administración para grupos.

    Métodos:
        has_module_permission: Verifica si el usuario tiene permisos para acceder al módulo de grupos.
        has_view_permission: Verifica si el usuario tiene permisos para ver grupos específicos.
        has_add_permission: Verifica si el usuario tiene permisos para añadir nuevos grupos.
        has_change_permission: Verifica si el usuario tiene permisos para cambiar grupos.
        has_delete_permission: Verifica si el usuario tiene permisos para eliminar grupos.
    """

    def has_module_permission(self, request):
        """
        Verifica si el usuario actual tiene permisos para acceder al módulo de administración de grupos.

        Parámetros:
            request: Objeto de solicitud HTTP.

        Retorna:
            bool: True si el usuario tiene permisos de visualización, de lo contrario False.
        """

        return request.user.is_staff and request.user.has_perm('app.view_roles')

    def has_view_permission(self, request, obj=None):
        """
        Verifica si el usuario actual tiene permisos para ver grupos específicos.

        Parámetros:
            request: Objeto de solicitud HTTP.
            obj: Objeto grupo específico (opcional).

        Retorna:
            bool: True si el usuario tiene permisos de visualización, de lo contrario False.
        """

        return request.user.is_staff and request.user.has_perm('app.view_roles')

    def has_add_permission(self, request):
        """
        Verifica si el usuario actual tiene permisos para añadir nuevos grupos.

        Parámetros:
            request: Objeto de solicitud HTTP.

        Retorna:
            bool: True si el usuario tiene permisos para añadir grupos, de lo contrario False.
        """

        return request.user.is_staff and request.user.has_perm('app.create_roles')

    def has_change_permission(self, request, obj=None):
        """
        Verifica si el usuario actual tiene permisos para cambiar grupos.

        Parámetros:
            request: Objeto de solicitud HTTP.
            obj: Objeto grupo específico (opcional).

        Retorna:
            bool: True si el usuario tiene permisos para cambiar grupos, de lo contrario False.
        """

        return request.user.is_staff and request.user.has_perm('app.edit_roles')

    def has_delete_permission(self, request, obj=None):
        """
        Verifica si el usuario actual tiene permisos para eliminar grupos.

        Parámetros:
            request: Objeto de solicitud HTTP.
            obj: Objeto grupo específico (opcional).

        Retorna:
            bool: True si el usuario tiene permisos para eliminar grupos, de lo contrario False.
        """

        return request.user.is_staff and request.user.has_perm('app.delete_roles')

# Desregistrar el modelo Group
admin.site.unregister(Group)

# Registrar el modelo Group con la clase CustomGroupAdmin
admin.site.register(Group, CustomGroupAdmin)

# Registrar CustomUser con CustomUserAdmin
admin.site.register(CustomUser, CustomUserAdmin)

admin.site.site_header = "Administración del Sistema"

Group._meta.verbose_name = _("Rol")  # Singular: "Rol"
Group._meta.verbose_name_plural = _("Roles")  # Plural: "Roles"

