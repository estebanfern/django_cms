from django.contrib import admin, messages
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

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.

        Retorna:
            dict: Diccionario con las acciones disponibles, excluyendo la acción de eliminación predeterminada.
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

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.
            object_id (str): ID del objeto que se va a modificar.
            form_url (str, opcional): URL del formulario, si existe. Por defecto es una cadena vacía.
            extra_context (dict, opcional): Contexto adicional para la plantilla. Por defecto es None.

        Retorna:
            HttpResponse: La respuesta HTTP renderizada para la vista de cambio del objeto,
            incluyendo el contexto adicional con la URL de cancelación.
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

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.
            form_url (str, opcional): URL del formulario, si existe. Por defecto es una cadena vacía.
            extra_context (dict, opcional): Contexto adicional para la plantilla. Por defecto es None.

        Retorna:
            HttpResponse: La respuesta HTTP renderizada para la vista de adición del objeto,
            incluyendo el contexto adicional con la URL de cancelación.
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

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.
            queryset (QuerySet): QuerySet que contiene las categorías seleccionadas para la acción.

        Acciones:
            - Verifica si el usuario tiene permisos para moderar categorías.
            - Si el usuario no tiene permisos, muestra un mensaje de error.
            - Si tiene permisos, marca las categorías seleccionadas como moderadas y muestra un mensaje de éxito.
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

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.
            queryset (QuerySet): QuerySet que contiene las categorías seleccionadas para la acción.

        Acciones:
            - Verifica si el usuario tiene permisos para modificar la moderación de categorías.
            - Si el usuario no tiene permisos, muestra un mensaje de error.
            - Si tiene permisos, marca las categorías seleccionadas como no moderadas y muestra un mensaje de éxito.
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

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.
            queryset (QuerySet): QuerySet que contiene las categorías seleccionadas para la acción.

        Acciones:
            - Verifica si el usuario tiene permisos para activar categorías.
            - Si el usuario no tiene permisos, muestra un mensaje de error.
            - Si tiene permisos, activa las categorías seleccionadas y muestra un mensaje de éxito.
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

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.
            queryset (QuerySet): QuerySet que contiene las categorías seleccionadas para la acción.

        Acciones:
            - Verifica si el usuario tiene permisos para desactivar categorías.
            - Si el usuario no tiene permisos, muestra un mensaje de error.
            - Si tiene permisos, desactiva las categorías seleccionadas y muestra un mensaje de éxito.
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

        Verifica si las categorías tienen contenidos asociados antes de eliminarlas.
        Si hay contenidos asociados, muestra un mensaje de error; de lo contrario, elimina las categorías seleccionadas.

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.
            queryset (QuerySet): QuerySet que contiene las categorías seleccionadas para la acción.

        Acciones:
            - Verifica permisos y la existencia de contenidos asociados antes de eliminar.
            - Muestra mensajes de éxito o error según corresponda.
        """
        if not request.user.has_perm('app.delete_category'):
            self.message_user(request, "No tienes permiso para eliminar categorías.", level=messages.ERROR)
            return

        # Filtrar las categorías con contenidos asociados
        categories_with_content = queryset.filter(content__isnull=False).distinct()

        if categories_with_content.exists():
            # Mostrar mensaje de error para categorías con contenidos asociados
            self.message_user(
                request,
                f"No se pueden eliminar las siguientes categorías porque tienen contenidos asociados: {', '.join([str(cat) for cat in categories_with_content])}.",
                level=messages.ERROR
            )
        else:
            # Guardar los nombres antes de eliminar
            nombres = ', '.join([str(cat) for cat in queryset])
            # Continuar con la eliminación solo si no hay categorías con contenidos
            super().delete_queryset(request, queryset)
            # Mostrar mensaje de éxito después de eliminar
            self.message_user(request, f"Categorías eliminadas con éxito: {nombres}.", level=messages.SUCCESS)

    # Sobrescribir delete_model para manejar la eliminación individual
    def delete_model(self, request, obj):
        """
        Sobrescribe la eliminación individual de un modelo en el panel de administración.

        Verifica si el objeto tiene contenidos asociados antes de permitir la eliminación.
        Si hay contenidos asociados, muestra un mensaje de error.

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.
            obj (Model): Objeto del modelo que se va a eliminar.

        Acciones:
            - Verifica contenidos asociados antes de eliminar.
            - Muestra un mensaje de error si existen contenidos asociados.
        """
        if obj.content_set.exists():
            self.message_user(request, "No se puede eliminar esta categoría porque tiene contenidos asociados.",
                              level=messages.ERROR)
        else:
            super().delete_model(request, obj)
            # Mostrar mensaje de éxito personalizado
            # self.message_user(request, f"La categoría “{obj}” fue eliminada con éxito.", level=messages.SUCCESS)

    # Métodos para verificar permisos personalizados
    def has_module_permission(self, request):
        """
        Verifican si el usuario actual tiene permisos específicos de module en el panel de administración.

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.
            obj (Model, opcional): Objeto del modelo específico para verificar permisos (opcional en algunas funciones).

        Retorna:
            bool: True si el usuario tiene los permisos necesarios, de lo contrario False.

        Notas:
            - Se incluyen validaciones adicionales para la eliminación de objetos que tienen contenidos asociados.
        """
        return request.user.has_perm('app.view_category')

    def has_view_permission(self, request, obj=None):
        """
        Verifican si el usuario actual tiene permisos de view en el panel de administración.

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.
            obj (Model, opcional): Objeto del modelo específico para verificar permisos (opcional en algunas funciones).

        Retorna:
            bool: True si el usuario tiene los permisos necesarios, de lo contrario False.

        Notas:
            - Se incluyen validaciones adicionales para la eliminación de objetos que tienen contenidos asociados.
        """
        return request.user.has_perm('app.view_category')

    def has_add_permission(self, request):
        """
        Verifican si el usuario actual tiene permisos de add en el panel de administración.

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.
            obj (Model, opcional): Objeto del modelo específico para verificar permisos (opcional en algunas funciones).

        Retorna:
            bool: True si el usuario tiene los permisos necesarios, de lo contrario False.

        Notas:
            - Se incluyen validaciones adicionales para la eliminación de objetos que tienen contenidos asociados.
        """
        return request.user.has_perm('app.create_category')

    def has_change_permission(self, request, obj=None):
        """
        Verifican si el usuario actual tiene permisos de change en el panel de administración.

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.
            obj (Model, opcional): Objeto del modelo específico para verificar permisos (opcional en algunas funciones).

        Retorna:
            bool: True si el usuario tiene los permisos necesarios, de lo contrario False.

        Notas:
            - Se incluyen validaciones adicionales para la eliminación de objetos que tienen contenidos asociados.
        """
        return request.user.has_perm('app.edit_category')

    def has_delete_permission(self, request, obj=None):
        """
        Verifican si el usuario actual tiene permisos de delete en el panel de administración.

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.
            obj (Model, opcional): Objeto del modelo específico para verificar permisos (opcional en algunas funciones).

        Retorna:
            bool: True si el usuario tiene los permisos necesarios, de lo contrario False.

        Notas:
            - Se incluyen validaciones adicionales para la eliminación de objetos que tienen contenidos asociados.
        """
        # Validar permisos y que no existan contenidos asociados antes de permitir eliminar
        if obj:
            if obj.content_set.exists():  # Verificar si hay contenidos asociados
                self.message_user(request, ("No se puede eliminar esta categoría porque tiene contenidos asociados."), level=messages.ERROR)
                return False
        return request.user.has_perm('app.delete_category')

# Registrar el modelo con el admin
admin.site.register(Category, CategoryAdmin)
Category._meta.verbose_name = _("Categoría")  # Singular: "Categoría"
Category._meta.verbose_name_plural = _("Categorías")  # Plural: "Categorías"