from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin, UserAdmin
from django.contrib.auth.models import Group
from django.contrib import admin, messages
from django.http import HttpResponseRedirect

import notification.service
from app.models import CustomUser
from django.utils.translation import gettext_lazy as _
from app.forms import CustomUserFormAdmin
from django.urls import reverse

@admin.action(description="Bloquear usuario/s")
def bloquear_usuarios(self, request, queryset):
    """
    Bloquea los usuarios seleccionados en el panel de administración.

    :param self: Referencia al objeto actual.
    :param request: Objeto de solicitud HTTP que contiene metadatos sobre la solicitud.
    :param queryset: QuerySet que contiene los usuarios seleccionados para la acción.

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

    :param self: Referencia al objeto actual.
    :param request: Objeto de solicitud HTTP que contiene metadatos sobre la solicitud.
    :param queryset: QuerySet que contiene los usuarios seleccionados para la acción.

    Acciones:
        - Itera sobre los usuarios seleccionados y activa su cuenta.
        - Muestra un mensaje de éxito por cada usuario desbloqueado.
    """
    for usuario in queryset:
        if not usuario.is_active:
            usuario.is_active = True
            usuario.save()
            self.message_user(request, f'El usuario {usuario.name} ha sido desbloqueado.', messages.SUCCESS)


def custom_title_filter_factory(filter_cls, title):
    class Wrapper(filter_cls):
        def __new__(cls, *args, **kwargs):
            instance = filter_cls(*args, **kwargs)
            instance.title = title
            return instance

    return Wrapper


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
    list_filter = (
        'is_active',
        ('groups', custom_title_filter_factory(admin.RelatedFieldListFilter, 'Roles')),
    )

    fieldsets = (
        (_('Informacion personal'), {'fields': ('name', 'email' ,'photo', 'about')}),
        (_('Roles y estado'), {'fields': ('is_active', 'groups')}),
        (_('Fechas relevantes'), {'fields': ('last_login', 'date_joined')}),
    )
    search_fields = ('email', 'name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

    readonly_fields = ('name', 'email', 'photo', 'about', 'last_login', 'date_joined')

    # Cambiar tanto el label como el help_text de "groups" (ahora "Roles")
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'groups':
            # Cambiar el label a "Roles"
            kwargs['label'] = _('Roles')
            # Cambiar el mensaje de ayuda
            kwargs['help_text'] = _('Los roles a los que pertenece este usuario. '
                                    'Un usuario tendrá todos los permisos asignados a cada uno de sus roles. ')
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):

        """
        Sobrescribe el método save_model para manejar la lógica de guardado del grupo y enviar notificaciones
        cuando se cambian los roles de un usuario.

        :param request: Objeto de solicitud HTTP.
        :param obj: El objeto del usuario que se está guardando.
        :param form: El formulario que contiene los datos del usuario.
        :param change: Booleano que indica si el objeto está siendo cambiado.
        """

        if not 'groups' in form.changed_data:
            super().save_model(request, obj, form, change)
            return


        old_groups = set(obj.groups.all())  # Grupos antes de guardar

        super().save_model(request, obj, form, change)

        new_groups = set(form.cleaned_data['groups'])  # Grupos seleccionados en el formulario

        # Comparar usuarios y enviar notificaciones si se les ha asignado o quitado el grupo
        added_groups = new_groups - old_groups
        removed_groups = old_groups - new_groups

        # Enviar notificación a los usuarios añadidos al grupo
        if added_groups:
            notification.service.changeRole(obj, added_groups, True)
        if removed_groups:
            notification.service.changeRole(obj, removed_groups, False)

    # Boton de Cancelar al modificar
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        Modifica la vista de cambio en el panel de administración para agregar un botón de cancelar.

        En el panel de administración añade un botón de cancelar que redirige a la lista de objetos del mismo tipo.

        :param request: Objeto de solicitud HTTP.
        :param object_id: ID del objeto que se va a modificar.
        :param form_url: URL del formulario, si existe. Por defecto es una cadena vacía.
        :param extra_context: Contexto adicional para la plantilla. Por defecto es None.
        :return: La respuesta HTTP renderizada para la vista de cambio del objeto, incluyendo el contexto adicional con la URL de cancelación.
        :rtype: HttpResponse
        """

        extra_context = extra_context or {}
        cancel_url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        extra_context['cancel_url'] = cancel_url
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def has_module_permission(self, request):
        """
        Verifica si el usuario actual tiene permisos para acceder al módulo de administración de usuarios.

        :param request: Objeto de solicitud HTTP.
        :return: True si el usuario tiene permisos de visualización, de lo contrario False.
        :rtype: bool
        """

        return request.user.has_perm('app.view_users')

    def has_view_permission(self, request, obj=None):
        """
        Verifica si el usuario actual tiene permisos para ver usuarios específicos.

        :param request: Objeto de solicitud HTTP.
        :param obj: Objeto usuario específico (opcional).
        :return: True si el usuario tiene permisos de visualización, de lo contrario False.
        :rtype: bool
        """

        return request.user.has_perm('app.view_users')

    def has_add_permission(self, request):
        """
        Controla el permiso para añadir nuevos usuarios desde el panel de administración.

        Esta función siempre devuelve False, impidiendo que los usuarios puedan agregar
        nuevos usuarios directamente desde el panel de administración.

        :param request: Objeto de solicitud HTTP.
        :type request: HttpRequest

        :return: False, indicando que no se permite la adición de nuevos usuarios.
        :rtype: bool
        """
        return False

    def has_change_permission(self, request, obj=None):
        """
        Verifica si el usuario actual tiene permisos para cambiar usuarios.

        :param request: Objeto de solicitud HTTP.
        :param obj: Objeto usuario específico (opcional).
        :return: True si el usuario tiene permisos para cambiar usuarios, de lo contrario False.
        :rtype: bool
        """

        return request.user.has_perm('app.edit_roles')

    def has_delete_permission(self, request, obj=None):
        """
        Controla el permiso para eliminar usuarios desde el panel de administración.

        Esta función siempre devuelve False, impidiendo que los usuarios puedan eliminar
        usuarios directamente desde el panel de administración.

        :param request: Objeto de solicitud HTTP.
        :type request: HttpRequest
        :param obj: Objeto del modelo específico para verificar permisos (opcional).
        :type obj: Model, opcional

        :return: False, indicando que no se permite la eliminación de usuarios.
        :rtype: bool
        """
        return False


class CustomGroupAdmin(BaseGroupAdmin):
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

    # Sobreescribir la acción de eliminar seleccionados
    actions = ['delete_selected_roles']

    # Boton de Cancelar al modificar
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        Modifica la vista de cambio en el panel de administración para agregar un botón de cancelar.

        :param request: Objeto de solicitud HTTP.
        :param object_id: ID del objeto que se va a modificar.
        :param form_url: URL del formulario, si existe. Por defecto es una cadena vacía.
        :param extra_context: Contexto adicional para la plantilla. Por defecto es None.
        :return: La respuesta HTTP renderizada para la vista de cambio del objeto, incluyendo el contexto adicional con la URL de cancelación.
        :rtype: HttpResponse
        """

        extra_context = extra_context or {}
        cancel_url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        extra_context['cancel_url'] = cancel_url
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    # Restricción para no eliminar grupos con usuarios asociados
    def delete_view(self, request, object_id, extra_context=None):
        """
        Sobrescribe la vista de eliminación para impedir eliminar grupos con usuarios asociados.
        """
        group = self.get_object(request, object_id)

        # Verificar si hay usuarios asociados al grupo
        if group.user_set.exists():
            # Si el grupo tiene usuarios, mostrar un mensaje de error y redirigir al listado de grupos
            messages.error(request, 'No puedes eliminar el rol porque tiene usuarios asociados.')
            return HttpResponseRedirect(reverse('admin:auth_group_changelist'))

        # Si no hay usuarios asociados, permitir la eliminación
        return super().delete_view(request, object_id, extra_context)

    # Mensaje de éxito después de la eliminación
    def response_delete(self, request, obj_display, obj_id):
        """
        Sobrescribe el método response_delete para mostrar el mensaje de éxito
        después de que el grupo haya sido eliminado.
        """
        # Mostrar el mensaje de éxito
        messages.success(request, f'El grupo "{obj_display}" se ha eliminado correctamente.')

        # Redirigir a la lista de grupos después de la eliminación
        return HttpResponseRedirect(reverse('admin:auth_group_changelist'))

    # Acción personalizada para eliminar roles seleccionados
    @admin.action(description='Eliminar roles seleccionados')
    def delete_selected_roles(self, request, queryset):
        """
        Acción para eliminar grupos seleccionados. Si alguno de los grupos tiene usuarios asociados,
        se muestra un mensaje de error y no se elimina ese grupo.
        """
        if not request.user.has_perm('app.delete_roles'):
            self.message_user(request, "No tienes permiso para eliminar roles.", level=messages.ERROR)
            return

        groups_with_users = [group for group in queryset if group.user_set.exists()]

        if groups_with_users:
            # Mostrar un mensaje de error si algunos roles tienen usuarios asociados
            group_names = ', '.join([group.name for group in groups_with_users])
            messages.error(request,
                           f'No puedes eliminar los siguientes grupos porque tienen usuarios asociados: {group_names}')
            # Redirigir de vuelta a la lista de grupos
            return HttpResponseRedirect(reverse('admin:auth_group_changelist'))

        # Si ningún rol tiene usuarios asociados, proceder con la eliminación
        roles = ', '.join([group.name for group in queryset])
        super().delete_queryset(request, queryset)
        self.message_user(request, f"Roles eliminadas con éxito: {roles}.", level=messages.SUCCESS)

    # Desactivar la acción predeterminada de eliminar
    def get_actions(self, request):
        """
        Sobrescribe las acciones disponibles en el panel de administración.

        Elimina la acción predeterminada de eliminar elementos seleccionados para personalizar la eliminación.

        :param request: Objeto de solicitud HTTP.
        :type request: HttpRequest
        :return: Diccionario con las acciones disponibles, excluyendo la acción de eliminación predeterminada.
        :rtype: dict
        """
        actions = super().get_actions(request)
        # Eliminar la acción predeterminada de eliminación
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    # Boton de Cancelar al agregar
    def add_view(self, request, form_url='', extra_context=None):
        """
        Modifica la vista de adición en el panel de administración para agregar un botón de cancelar.

        :param request: Objeto de solicitud HTTP.
        :param form_url: URL del formulario, si existe. Por defecto es una cadena vacía.
        :param extra_context: Contexto adicional para la plantilla. Por defecto es None.
        :return: La respuesta HTTP renderizada para la vista de adición del objeto, incluyendo el contexto adicional con la URL de cancelación.
        :rtype: HttpResponse
        """

        extra_context = extra_context or {}
        cancel_url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        extra_context['cancel_url'] = cancel_url
        return super().add_view(request, form_url, extra_context=extra_context)

    def has_module_permission(self, request):
        """
        Verifica si el usuario actual tiene permisos para acceder al módulo de administración de grupos.

        :param request: Objeto de solicitud HTTP.
        :return: True si el usuario tiene permisos de visualización, de lo contrario False.
        :rtype: bool
        """

        return request.user.is_staff and request.user.has_perm('app.view_roles')

    def has_view_permission(self, request, obj=None):
        """
        Verifica si el usuario actual tiene permisos para ver grupos específicos.

        :param request: Objeto de solicitud HTTP.
        :param obj: Objeto grupo específico (opcional).
        :return: True si el usuario tiene permisos de visualización, de lo contrario False.
        :rtype: bool
        """

        return request.user.is_staff and request.user.has_perm('app.view_roles')

    def has_add_permission(self, request):
        """
        Verifica si el usuario actual tiene permisos para añadir nuevos grupos.

        :param request: Objeto de solicitud HTTP.
        :return: True si el usuario tiene permisos para añadir grupos, de lo contrario False.
        :rtype: bool
        """

        return request.user.is_staff and request.user.has_perm('app.create_roles')

    def has_change_permission(self, request, obj=None):
        """
        Verifica si el usuario actual tiene permisos para cambiar grupos.

        :param request: Objeto de solicitud HTTP.
        :param obj: Objeto grupo específico (opcional).
        :return: True si el usuario tiene permisos para cambiar grupos, de lo contrario False.
        :rtype: bool
        """

        return request.user.is_staff and request.user.has_perm('app.edit_roles')

    def has_delete_permission(self, request, obj=None):
        """
        Verifica si el usuario actual tiene permisos para eliminar grupos.

        Verifica si las roles tienen usuarios asociados antes de permitir la eliminación.

        :param request: Objeto de solicitud HTTP.
        :param obj: Objeto grupo específico (opcional).
        :return: True si el usuario tiene permisos para eliminar roles y no hay usuarios asociados, de lo contrario False.
        :rtype: bool
        """
        if obj:
            if obj.user_set.exists():
                self.message_user(request, ("No se puede eliminar este rol porque tiene usuarios asociados."), level=messages.ERROR)
                return False
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

