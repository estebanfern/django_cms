from django.contrib import admin, messages
from django.utils.html import format_html

from .models import Content, Report
from django.urls import reverse, path
from .views import view_content_detail, report_detail


class ContentAdmin(admin.ModelAdmin):
    """
    Configuración personalizada para la administración del modelo `Content`.

    Define cómo se gestionan los contenidos en el panel de administración, incluyendo la visualización
    de campos, filtros, búsqueda, acciones personalizadas y permisos de usuario.

    :attribute list_display: Campos que se mostrarán en la lista de contenidos.
    :type list_display: tuple
    :attribute list_filter: Filtros disponibles para filtrar los contenidos.
    :type list_filter: tuple
    :attribute search_fields: Campos disponibles para la búsqueda de contenidos.
    :type search_fields: tuple
    :attribute fields: Campos mostrados en el formulario de creación y edición de contenidos.
    :type fields: tuple
    :attribute readonly_fields: Campos de solo lectura en el formulario de edición.
    :type readonly_fields: tuple
    :attribute actions: Lista de acciones personalizadas disponibles para los contenidos.
    :type actions: list
    """

    # Mostrar estos campos en la lista de contenidos
    list_display = ('title', 'category', 'autor', 'state', 'date_create', 'date_expire', 'is_active', 'important')

    # Añadir filtros para estos campos
    list_filter = ('state', 'is_active', 'category', 'important')

    # Habilitar búsqueda por estos campos
    search_fields = ('title', 'summary', 'autor__name', 'category__name')

    # Campos a mostrar en el formulario de creación y edición
    fields = ('title', 'summary', 'category', 'autor', 'state', 'is_active', 'date_create', 'date_published' ,'date_expire','display_tags', 'important')

    # Hacer todos los campos de solo lectura, excepto 'is_active'
    readonly_fields = ('title', 'summary', 'category', 'autor', 'state', 'date_create', 'date_expire', 'date_published', 'display_tags', 'important')

    # Definir acciones personalizadas
    actions = ['activar_contenidos', 'desactivar_contenidos', 'destacar_contenido', 'quitar_destacado']

    def display_tags(self, obj):
        """
        Muestra las etiquetas asociadas a un contenido.

        Este método genera una cadena de texto con los nombres de las etiquetas asociadas
        a un contenido, separadas por comas.

        :param obj: Instancia del modelo `Content` para obtener las etiquetas asociadas.
        :type obj: Content
        :return: Una cadena de texto con las etiquetas asociadas al contenido, separadas por comas.
        :rtype: str
        """

        return ", ".join([tag.name for tag in obj.tags.all()])

    display_tags.short_description = 'Etiquetas'

    def get_urls(self):
        """
        Personaliza las URLs disponibles en el panel de administración para contenidos.

        Añade rutas personalizadas para visualizar reportes y detalles de contenido en el
        panel de administración.

        :return: Una lista de URLs que incluye las rutas personalizadas y las predeterminadas del modelo.
        :rtype: list
        """

        urls = super().get_urls()
        custom_urls = [
            path('<int:report_id>/report/', report_detail, name='content-report'),
            path('<int:content_id>/view/', view_content_detail, name='content-view-detail'),
        ]
        return custom_urls + urls

    # Boton de Cancelar al modificar
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        Modifica la vista de cambio en el panel de administración para agregar un botón de cancelar.

        Esta función personaliza la vista de modificación de un objeto en el panel de administración, añadiendo un botón de cancelar que redirige a la lista de objetos del mismo tipo.

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

        # Obtener el contenido que se está editando
        content = self.get_object(request, object_id)

        if request.user.has_perm('app.view_reports'):
            # Obtener los reportes relacionados con ese contenido
            related_reports = Report.objects.filter(content=content)
            # Pasar los reportes relacionados al contexto
            extra_context['related_reports'] = related_reports
        else:
            extra_context['related_reports'] = 'no_permission'

        # Pasar la URL de cancelar al contexto
        cancel_url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
        extra_context['cancel_url'] = cancel_url

        # Agregar la URL del botón "Ver contenido"
        view_content_url = reverse('admin:content-view-detail', args=[content.pk])
        extra_context['view_content_url'] = view_content_url

        # Llamar a la vista original con el contexto adicional
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    # Acción para activar contenidos seleccionados
    @admin.action(description='Activar contenidos seleccionados')
    def activar_contenidos(self, request, queryset):
        """
        Activa los contenidos seleccionados en el panel de administración.

        Verifica que el usuario tenga permisos para editar el estado activo de los contenidos
        antes de realizar la activación.

        :param request: La solicitud HTTP recibida.
        :type request: HttpRequest
        :param queryset: QuerySet con los contenidos seleccionados para la acción.
        :type queryset: QuerySet

        :raises PermissionError: Si el usuario no tiene permiso para activar contenidos.
        """

        # Verificar el permiso 'edit_is_active'
        if not request.user.has_perm('app.edit_is_active'):
            self.message_user(request, "No tienes permiso para activar contenidos.", level=messages.ERROR)
            return
        # Actualizar y obtener los títulos de los contenidos activados
        updated = queryset.update(is_active=True)
        nombres = ', '.join([content.title for content in queryset])
        self.message_user(request, f"Contenidos activados: {nombres}.", level=messages.SUCCESS)

    # Acción para desactivar contenidos seleccionados
    @admin.action(description='Desactivar contenidos seleccionados')
    def desactivar_contenidos(self, request, queryset):
        """
        Desactiva los contenidos seleccionados en el panel de administración.

        Verifica que el usuario tenga permisos para editar el estado activo de los contenidos
        antes de realizar la desactivación.

        :param request: La solicitud HTTP recibida.
        :type request: HttpRequest
        :param queryset: QuerySet con los contenidos seleccionados para la acción.
        :type queryset: QuerySet

        :raises PermissionError: Si el usuario no tiene permiso para desactivar contenidos.
        """

        # Verificar el permiso 'edit_is_active'
        if not request.user.has_perm('app.edit_is_active'):
            self.message_user(request, "No tienes permiso para desactivar contenidos.", level=messages.ERROR)
            return
        # Actualizar y obtener los títulos de los contenidos desactivados
        updated = queryset.update(is_active=False)
        nombres = ', '.join([content.title for content in queryset])
        self.message_user(request, f"Contenidos desactivados: {nombres}.", level=messages.SUCCESS)

    @admin.action(description='Destacar contenidos')
    def destacar_contenido(self, request, queryset):
        """
        Destaca los contenidos seleccionados en el panel de administración.

        Verifica que el usuario tenga permisos para establecer contenidos como destacados
        antes de realizar la acción.

        :param request: La solicitud HTTP recibida.
        :type request: HttpRequest
        :param queryset: QuerySet con los contenidos seleccionados para la acción.
        :type queryset: QuerySet

        :raises PermissionError: Si el usuario no tiene permiso para destacar contenidos.
        """

        if not self.has_set_important_permission(request):
            self.message_user(request, "No tienes permiso para destacar contenidos.", level=messages.ERROR)
            return
        updated = queryset.update(important=True)
        nombres = ', '.join([content.title for content in queryset])
        self.message_user(request, f"Contenidos destacados: {nombres}.", level=messages.SUCCESS)

    @admin.action(description='Quitar destacados')
    def quitar_destacado(self, request, queryset):
        """
        Elimina el estado de destacado de los contenidos seleccionados.

        Verifica que el usuario tenga permisos para modificar contenidos antes de realizar la acción.

        :param request: La solicitud HTTP recibida.
        :type request: HttpRequest
        :param queryset: QuerySet con los contenidos seleccionados para la acción.
        :type queryset: QuerySet

        :raises PermissionError: Si el usuario no tiene permiso para modificar destacados.
        """

        if not self.has_set_important_permission(request):
            self.message_user(request, "No tienes permiso para destacar contenidos.", level=messages.ERROR)
            return
        updated = queryset.update(important=True)
        nombres = ', '.join([content.title for content in queryset])
        self.message_user(request, f"Se ha quitado el destacado en los contenidos: {nombres}.", level=messages.SUCCESS)

    def has_add_permission(self, request):
        """
        Controla el permiso para añadir nuevos contenidos desde el panel de administración.

        Esta función siempre devuelve False, impidiendo que los usuarios puedan agregar
        contenidos desde el panel de administración.

        :param request: La solicitud HTTP recibida.
        :type request: HttpRequest
        :return: False
        :rtype: bool
        """

        # No permitir agregar nuevos contenidos desde el admin
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Controla el permiso para eliminar contenidos desde el panel de administración.

        Esta función siempre devuelve False, impidiendo que los usuarios puedan eliminar
        contenidos directamente desde el panel de administración.

        :param request: Objeto de solicitud HTTP.
        :type request: HttpRequest
        :param obj: Objeto del modelo específico para verificar permisos (opcional).
        :type obj: Model, opcional

        :return: False, indicando que no se permite la eliminación de contenidos.
        :rtype: bool
        """
        # No permitir eliminar contenidos desde el admin
        return False

    def has_view_permission(self, request, obj=None):
        """
        Controla el permiso para ver los contenidos en el panel de administración.

        Permite la visualización de los contenidos solo si el usuario tiene el permiso 'view_content'.
        Esta función asegura que solo los usuarios con el permiso adecuado puedan acceder
        a la lista de contenidos y ver detalles.

        :param request: Objeto de solicitud HTTP.
        :type request: HttpRequest
        :param obj: Objeto del modelo específico para verificar permisos (opcional).
        :type obj: Model, opcional

        :return: True si el usuario tiene el permiso 'view_content', de lo contrario False.
        :rtype: bool
        """
        # Permite la visualización solo si el usuario tiene el permiso 'view_content'
        return request.user.has_perm('app.view_content')

    def has_change_permission(self, request, obj=None):
        """
        Controla el permiso para editar contenidos desde el panel de administración.

        Permite la edición de los contenidos solo si el usuario tiene el permiso 'edit_is_active'.
        Esto asegura que solo los usuarios con permisos específicos puedan cambiar el estado
        de activación de los contenidos, sin modificar otros campos de solo lectura.

        :param request: Objeto de solicitud HTTP.
        :type request: HttpRequest
        :param obj: Objeto del modelo específico para verificar permisos (opcional).
        :type obj: Model, opcional

        :return: True si el usuario tiene el permiso 'edit_is_active', de lo contrario False.
        :rtype: bool
        """
        # Permite la edición solo si el usuario tiene el permiso 'edit_is_active'
        if obj:
            return request.user.has_perm('app.block_content')
        return False

    def has_module_permission(self, request):
        """
        Controla el permiso para acceder al módulo de contenidos en el panel de administración.

        Permite el acceso al módulo de contenidos solo si el usuario tiene el permiso 'view_content'.
        Este permiso general asegura que solo los usuarios autorizados puedan ver y navegar por el módulo
        de contenidos en el panel de administración.

        :param request: Objeto de solicitud HTTP.
        :type request: HttpRequest

        :return: True si el usuario tiene el permiso 'view_content', de lo contrario False.
        :rtype: bool
        """
        return request.user.has_perm('app.view_content')

    def has_set_important_permission(self, request, obj=None):
        return request.user.has_perm('app.set_important_content')

class ReportAdmin(admin.ModelAdmin):
    """
    Configuración personalizada para la administración del modelo `Report`.

    Define cómo se gestionan los reportes de contenido en el panel de administración,
    incluyendo la visualización de campos, búsqueda, y permisos específicos.

    :attribute list_display: Campos que se mostrarán en la lista de reportes.
    :type list_display: tuple
    :attribute search_fields: Campos disponibles para la búsqueda de reportes.
    :type search_fields: tuple
    :attribute fields: Campos mostrados en el formulario de edición de reportes.
    :type fields: tuple
    :attribute readonly_fields: Campos de solo lectura en el formulario de edición.
    :type readonly_fields: tuple
    """

    list_display = ('created_at', 'reason', 'name', 'email', 'content', 'view_report_link')
    search_fields = ('content__title', 'name', 'email', 'reason')
    list_display_links = None

    fields = ('content', 'get_reported_by_info', 'reason', 'description', 'created_at')
    readonly_fields = ('content', 'reported_by', 'email', 'name', 'reason', 'description', 'created_at')

    def get_reported_by_info(self, obj):
        """
        Obtiene información del usuario que realizó el reporte.

        Este método devuelve una cadena con el nombre y correo electrónico del usuario.

        :param obj: Instancia del reporte.
        :type obj: Report
        :return: Información del usuario que realizó el reporte.
        :rtype: str
        """

        return f'{obj.name} ({obj.email})'

    get_reported_by_info.short_description = 'Realizado por'

    def view_report_link(self, obj):
        """
        Genera un enlace a los detalles del reporte.

        El enlace se utiliza para redirigir al administrador a la vista de edición del reporte.

        :param obj: Instancia del reporte.
        :type obj: Report
        :return: HTML con el enlace al reporte.
        :rtype: str
        """

        url = reverse('admin:content_report_change', args=[obj.pk])
        return format_html('<a href="{}">Ver reporte</a>', url)

    view_report_link.short_description = 'Accion'
    view_report_link.admin_order_field = 'id'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        Modifica la vista de edición de un reporte en el panel de administración.

        Personaliza la vista de modificación para incluir información adicional sobre el contenido
        relacionado con el reporte y permite acciones adicionales, como visualizar el contenido reportado.

        :param request: La solicitud HTTP recibida.
        :type request: HttpRequest
        :param object_id: ID del objeto reporte que se está editando.
        :type object_id: str
        :param form_url: URL del formulario, si existe. Por defecto es una cadena vacía.
        :type form_url: str, opcional
        :param extra_context: Contexto adicional para la plantilla. Por defecto es None.
        :type extra_context: dict, opcional

        :return: La respuesta HTTP renderizada para la vista de cambio del reporte, con información adicional.
        :rtype: HttpResponse
        """

        extra_context = extra_context or {}

        # Obtener el contenido que se está editando
        report = self.get_object(request, object_id)
        content = report.content

        # Agregar la URL del botón "Ver contenido"
        view_content_url = reverse('admin:content_content_change', args=[content.pk])
        extra_context['view_content_url'] = view_content_url

        permContent = request.user.has_perm('app.view_content')
        extra_context['permContent'] = permContent

        # Pasar la URL de cancelar al contexto
        cancel_url = None
        extra_context['cancel_url'] = cancel_url

        # Llamar a la vista original con el contexto adicional
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def has_add_permission(self, request):
        """
        Controla el permiso para añadir nuevos reportes desde el panel de administración.

        Esta función siempre devuelve False, impidiendo que los usuarios puedan agregar
        reportes desde el panel de administración.

        :param request: La solicitud HTTP recibida.
        :type request: HttpRequest
        :return: False
        :rtype: bool
        """

        return False

    def has_delete_permission(self, request, obj=None):
        """
        Controla el permiso para eliminar reportes desde el panel de administración.

        Esta función siempre devuelve False, impidiendo que los usuarios puedan eliminar
        reportes desde el panel de administración.

        :param request: La solicitud HTTP recibida.
        :type request: HttpRequest
        :param obj: Objeto del modelo específico para verificar permisos (opcional).
        :type obj: Model, opcional
        :return: False
        :rtype: bool
        """

        return False

    def has_view_permission(self, request, obj=None):
        """
        Controla el permiso para visualizar reportes en el panel de administración.

        Permite la visualización de los reportes solo si el usuario tiene el permiso `view_reports`.

        :param request: La solicitud HTTP recibida.
        :type request: HttpRequest
        :param obj: Objeto del modelo específico para verificar permisos (opcional).
        :type obj: Model, opcional
        :return: True si el usuario tiene el permiso `view_reports`, de lo contrario False.
        :rtype: bool
        """

        return request.user.has_perm('app.view_reports')

    def has_change_permission(self, request, obj=None):
        """
        Controla el permiso para modificar reportes desde el panel de administración.

        Esta función siempre devuelve False, impidiendo que los usuarios puedan modificar
        los reportes directamente desde el panel de administración.

        :param request: La solicitud HTTP recibida.
        :type request: HttpRequest
        :param obj: Objeto del modelo específico para verificar permisos (opcional).
        :type obj: Model, opcional
        :return: False
        :rtype: bool
        """

        return False

    def has_module_permission(self, request):
        """
        Controla el permiso para acceder al módulo de reportes en el panel de administración.

        Permite el acceso al módulo de reportes solo si el usuario tiene el permiso `view_reports`.

        :param request: La solicitud HTTP recibida.
        :type request: HttpRequest
        :return: True si el usuario tiene el permiso `view_reports`, de lo contrario False.
        :rtype: bool
        """

        return request.user.has_perm('app.view_reports')


# Registra el modelo Report en el admin
admin.site.register(Report, ReportAdmin)

# Registrar el modelo Content con la clase ContentAdmin
admin.site.register(Content, ContentAdmin)

Content._meta.verbose_name = ("Contenido")
Content._meta.verbose_name_plural = ("Contenidos")

Report._meta.verbose_name = ("Reporte")
Report._meta.verbose_name_plural = ("Reportes")
