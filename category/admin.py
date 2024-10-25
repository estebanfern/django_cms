from django.contrib import admin, messages
from django.http import HttpResponseRedirect

from suscription.models import Suscription
from .models import Category
from .forms import CategoryForm
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

class CategoryAdmin(admin.ModelAdmin):
    """
    Configuración personalizada para la administración del modelo Category en el panel de administración de Django.

    Atributos:
        form (ModelForm): Formulario personalizado utilizado para editar categorías.
        list_display (tuple): Campos que se mostrarán en la lista de categorías.
        list_filter (tuple): Filtros disponibles en la lista de categorías.
        search_fields (tuple): Campos por los cuales se puede buscar en la lista de categorías.
        fields (tuple): Campos a mostrar en el formulario de creación y edición.
        ordering (tuple): Orden por defecto de la lista de categorías.
        actions (list): Lista de acciones personalizadas para el modelo.
    """
    form = CategoryForm

    # Mostrar estos campos en la lista de categorías
    list_display = ('name', 'type', 'is_active','is_moderated' ,'price', 'date_create')

    # Añadir filtros para estos campos
    list_filter = ('type', 'is_active', 'is_moderated')

    # Habilitar búsqueda por estos campos
    search_fields = ('name', 'description')

    # Campos a mostrar en el formulario de creación y edición
    fields = ('name', 'description', 'type', 'is_active', 'is_moderated', 'price')

    # Ordenar los registros por fecha de creación de manera descendente
    ordering = ('-date_create',)

    # Definir acciones personalizadas
    actions = ['activar_categorias', 'desactivar_categorias', 'delete_selected_categories', 'moderar_categorias', 'quitar_moderacion_categorias']

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

    # Boton de Cancelar al modificar
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        Modifica la vista de cambio en el panel de administración para agregar un botón de cancelar.

        Esta función personaliza la vista de modificación de un objeto en el panel de administración,
        añadiendo un botón de cancelar que redirige a la lista de objetos del mismo tipo.

        :param request: Objeto de solicitud HTTP.
        :type request: HttpRequest
        :param object_id: ID del objeto que se va a modificar.
        :type object_id: str
        :param form_url: URL del formulario, si existe. Por defecto es una cadena vacía.
        :type form_url: str, opcional
        :param extra_context: Contexto adicional para la plantilla. Por defecto es None.
        :type extra_context: dict, opcional
        :return: La respuesta HTTP renderizada para la vista de cambio del objeto, incluyendo el contexto adicional con la URL de cancelación.
        :rtype: HttpResponse
        """
        extra_context = extra_context or {}
        cancel_url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        extra_context['cancel_url'] = cancel_url
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
    
    # Boton de Cancelar al agregar
    def add_view(self, request, form_url='', extra_context=None):
        """
        Modifica la vista de adición en el panel de administración para agregar un botón de cancelar.

        Esta función personaliza la vista de adición de un nuevo objeto en el panel de administración,
        añadiendo un botón de cancelar que redirige a la lista de objetos del mismo tipo.

        :param request: Objeto de solicitud HTTP.
        :type request: HttpRequest
        :param form_url: URL del formulario, si existe. Por defecto es una cadena vacía.
        :type form_url: str, opcional
        :param extra_context: Contexto adicional para la plantilla. Por defecto es None.
        :type extra_context: dict, opcional
        :return: La respuesta HTTP renderizada para la vista de adición del objeto, incluyendo el contexto adicional con la URL de cancelación.
        :rtype: HttpResponse
        """

        extra_context = extra_context or {}
        cancel_url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        extra_context['cancel_url'] = cancel_url
        return super().add_view(request, form_url, extra_context=extra_context)

    # Acción para moderar categorías
    @admin.action(description='Moderar categorías seleccionadas')
    def moderar_categorias(self, request, queryset):
        """
        Acción personalizada para moderar categorías seleccionadas en el panel de administración.

        Esta acción establece el estado de moderación de las categorías seleccionadas como moderadas.

        :param request: Objeto de solicitud HTTP.
        :type request: HttpRequest
        :param queryset: QuerySet que contiene las categorías seleccionadas para la acción.
        :type queryset: QuerySet
        """
        if not request.user.has_perm('app.edit_category'):
            self.message_user(request, "No tienes permiso para moderar categorías.", level=messages.ERROR)
            return
        queryset.update(is_moderated=True)
        nombres = ', '.join([category.name for category in queryset])
        self.message_user(request, f"Categorías moderadas: {nombres}.", level=messages.SUCCESS)

    # Acción para quitar la moderación de categorías
    @admin.action(description='Quitar moderación de categorías seleccionadas')
    def quitar_moderacion_categorias(self, request, queryset):
        """
        Acción personalizada para quitar la moderación de las categorías seleccionadas en el panel de administración.

        Esta acción establece el estado de moderación de las categorías seleccionadas como no moderadas.

        :param request: Objeto de solicitud HTTP.
        :type request: HttpRequest
        :param queryset: QuerySet que contiene las categorías seleccionadas para la acción.
        :type queryset: QuerySet
        """
        if not request.user.has_perm('app.edit_category'):
            self.message_user(request, "No tienes permiso para quitar la moderación de categorías.",
                              level=messages.ERROR)
            return
        queryset.update(is_moderated=False)
        nombres = ', '.join([category.name for category in queryset])
        self.message_user(request, f"Moderación quitada de las categorías: {nombres}.", level=messages.SUCCESS)

    # Acción para activar categorías
    @admin.action(description='Activar categorías seleccionadas')
    def activar_categorias(self, request, queryset):
        """
        Acción personalizada para activar categorías seleccionadas en el panel de administración.

        Esta acción establece el estado de activación de las categorías seleccionadas como activas.

        :param request: Objeto de solicitud HTTP.
        :type request: HttpRequest
        :param queryset: QuerySet que contiene las categorías seleccionadas para la acción.
        :type queryset: QuerySet
        """
        if not request.user.has_perm('app.edit_category'):
            self.message_user(request, "No tienes permiso para activar categorías.", level=messages.ERROR)
            return
        queryset.update(is_active=True)
        nombres = ', '.join([category.name for category in queryset])
        self.message_user(request, f"Categorías activadas: {nombres}.", level=messages.SUCCESS)

    # Acción para desactivar categorías
    @admin.action(description='Desactivar categorías seleccionadas')
    def desactivar_categorias(self, request, queryset):
        """
        Acción personalizada para desactivar categorías seleccionadas en el panel de administración.

        Esta acción establece el estado de activación de las categorías seleccionadas como inactivas.

        :param request: Objeto de solicitud HTTP.
        :type request: HttpRequest
        :param queryset: QuerySet que contiene las categorías seleccionadas para la acción.
        :type queryset: QuerySet
        """

        if not request.user.has_perm('app.edit_category'):
            self.message_user(request, "No tienes permiso para desactivar categorías.", level=messages.ERROR)
            return
        queryset.update(is_active=False)
        nombres = ', '.join([category.name for category in queryset])
        self.message_user(request, f"Categorías desactivadas: {nombres}.", level=messages.SUCCESS)

    # Definir una acción personalizada para la eliminación
    @admin.action(description='Eliminar categorías seleccionadas')
    def delete_selected_categories(self, request, queryset):
        """
        Acción personalizada para eliminar categorías seleccionadas en el panel de administración.

        Verifica si las categorías tienen contenidos y/o suscripciones asociados antes de eliminarlas.
        Si hay contenidos y/o suscripciones asociados, muestra un mensaje de error; de lo contrario, elimina las categorías seleccionadas.

        :param request: Objeto de solicitud HTTP.
        :type request: HttpRequest
        :param queryset: QuerySet que contiene las categorías seleccionadas para la acción.
        :type queryset: QuerySet
        """
        if not request.user.has_perm('app.delete_category'):
            self.message_user(request, "No tienes permiso para eliminar categorías.", level=messages.ERROR)
            return

        # Filtrar las categorías con contenidos asociados
        categories_with_content = queryset.filter(content__isnull=False).distinct()
        categories_without_content = queryset.exclude(content__isnull=False).distinct()
        categories_with_subcriptions = queryset.filter(suscription__isnull=False).distinct()
        categories_without_subcriptions = queryset.exclude(suscription__isnull=False).distinct()

        if categories_with_content.exists() and categories_with_subcriptions.exists():
            # Mostrar mensaje de error para categorías con contenidos y suscripciones asociados
            self.message_user(
                request,
                f"No se pueden eliminar las siguientes categorías porque tienen contenidos y suscripciones asociados:\n"
                f"Categorías con contenidos: {', '.join([str(cat) for cat in categories_with_content])}.\n"
                f"Categorías con suscripciones: {', '.join([str(cat) for cat in categories_with_subcriptions])}.",
                level=messages.ERROR
            )
        elif categories_with_content.exists():
            # Mostrar mensaje de error para categorías con contenidos asociados
            self.message_user(
                request,
                f"No se pueden eliminar las siguientes categorías porque tienen contenidos asociados: {', '.join([str(cat) for cat in categories_with_content])}.",
                level=messages.ERROR
            )
        elif categories_with_subcriptions.exists():
            # Mostrar mensaje de error para categorías con suscripciones asociados
            self.message_user(
                request,
                f"No se pueden eliminar las siguientes categorías porque tienen suscripciones asociados: {', '.join([str(cat) for cat in categories_with_subcriptions])}.",
                level=messages.ERROR
            )
        if categories_without_content.exists() and categories_without_subcriptions.exists():
            deleted_categories_name = ', '.join([str(cat) for cat in categories_without_content])
            queryset.filter(id__in=[category.id for category in categories_without_content]).delete()
            self.message_user(request, f"Categorías eliminadas con éxito: {deleted_categories_name}.", level=messages.SUCCESS)

        # Redirigir de vuelta a la lista de categorias
        return HttpResponseRedirect(reverse('admin:category_category_changelist'))

    def delete_view (self, request, object_id, extra_context=None):
        """
        Sobrescribe la vista de eliminación para impedir eliminar categorias con contenidos y suscripciones asociados.
        """
        category = self.get_object(request, object_id)
        subscription = Suscription.objects.filter(category=category).first()

        if category.content_set.exists() and subscription:
            messages.error(request, "No se puede eliminar esta categoría porque tiene contenidos y suscripciones asociados.")
            return HttpResponseRedirect(reverse('admin:category_category_changelist'))
        elif subscription:
            messages.error(request, "No se puede eliminar esta categoría porque tiene suscripciones asociados.")
            return HttpResponseRedirect(reverse('admin:category_category_changelist'))
        elif category.content_set.exists():
            messages.error(request, "No se puede eliminar esta categoría porque tiene contenidos asociados.")
            return HttpResponseRedirect(reverse('admin:category_category_changelist'))

        return super().delete_view(request, object_id, extra_context)

    def response_delete(self, request, obj_display, obj_id):
        """
        Sobrescribe el método response_delete para mostrar el mensaje de éxito
        después de que la categoria haya sido eliminado.
        """
        messages.success(request, f'La categoria "{obj_display}" se ha eliminado correctamente.')

        return HttpResponseRedirect(reverse('admin:category_category_changelist'))

    def response_add(self, request, obj, post_url_continue=None):
        """
        Sobrescribe el método response_add para mostrar un mensaje de éxito personalizado
        después de crear un grupo.
        """
        # Mensaje de éxito personalizado
        messages.success(request, f'La categoria "{obj.name}" se ha creado exitosamente.')

        # Redirigir a la lista de categorias después de la eliminación
        return HttpResponseRedirect(reverse('admin:category_category_changelist'))


    # Métodos para verificar permisos personalizados
    def has_module_permission(self, request):
        """
        Verifica si el usuario actual tiene permisos para acceder al módulo de administración de categorías.

        :param request: Objeto de solicitud HTTP.
        :type request: HttpRequest
        :return: True si el usuario tiene permisos de visualización, de lo contrario False.
        :rtype: bool
        """

        return request.user.has_perm('app.view_category')

    def has_view_permission(self, request, obj=None):
        """
        Verifica si el usuario actual tiene permisos para ver categorías específicas.

        :param request: Objeto de solicitud HTTP.
        :type request: HttpRequest
        :param obj: Objeto categoría específico (opcional).
        :type obj: Model, opcional
        :return: True si el usuario tiene permisos de visualización, de lo contrario False.
        :rtype: bool
        """

        return request.user.has_perm('app.view_category')

    def has_add_permission(self, request):
        """
        Verifica si el usuario actual tiene permisos para añadir nuevas categorías.

        :param request: Objeto de solicitud HTTP.
        :type request: HttpRequest
        :return: True si el usuario tiene permisos para añadir categorías, de lo contrario False.
        :rtype: bool
        """

        return request.user.has_perm('app.create_category')

    def has_change_permission(self, request, obj=None):
        """
        Verifica si el usuario actual tiene permisos para cambiar categorías.

        :param request: Objeto de solicitud HTTP.
        :type request: HttpRequest
        :param obj: Objeto categoría específico (opcional).
        :type obj: Model, opcional
        :return: True si el usuario tiene permisos para cambiar categorías, de lo contrario False.
        :rtype: bool
        """

        return request.user.has_perm('app.edit_category')

    def has_delete_permission(self, request, obj=None):
        """
        Verifica si el usuario actual tiene permisos para eliminar categorías.

        Verifica si las categorías tienen contenidos asociados y suscripciones activas antes de permitir la eliminación.

        :param request: Objeto de solicitud HTTP.
        :type request: HttpRequest
        :param obj: Objeto categoría específico (opcional).
        :type obj: Model, opcional
        :return: True si el usuario tiene permisos para eliminar categorías y no hay contenidos asociados, de lo contrario False.
        :rtype: bool
        """
        # Validar permisos y que no existan contenidos asociados ni suscripciones activas antes de permitir eliminar
        if obj:
            subscription = Suscription.objects.filter(category=obj).first()
            if obj.content_set.exists() and subscription:
                self.message_user(request,"No se puede eliminar esta categoría porque tiene contenidos y suscripciones asociados.", level=messages.ERROR)
                return False
            elif subscription:
                self.message_user(request, "No se puede eliminar esta categoría porque tiene suscripciones asociadas.", level=messages.ERROR)
                return False
            elif obj.content_set.exists():
                self.message_user(request, "No se puede eliminar esta categoría porque tiene contenidos asociados.", level=messages.ERROR)
                return False
        return request.user.has_perm('app.delete_category')

# Registrar el modelo con el admin
admin.site.register(Category, CategoryAdmin)
Category._meta.verbose_name = _("Categoría")  # Singular: "Categoría"
Category._meta.verbose_name_plural = _("Categorías")  # Plural: "Categorías"