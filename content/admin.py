from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Content, Report
from django.urls import reverse


class ReportInline(admin.TabularInline):
    """
    Muestra los reportes relacionados con un contenido dentro de la vista de edición de contenido.
    Solo se muestran algunos campos y se añade un enlace para ver los detalles completos del reporte.
    """
    model = Report
    extra = 0  # No mostrar filas vacías por defecto
    fields = ('name', 'email', 'reason', 'view_report_link')  # Mostrar solo estos campos
    readonly_fields = ('name', 'email', 'reason', 'view_report_link')  # Hacer estos campos solo lectura
    can_delete = False  # No permitir eliminar reportes desde esta vista

    def view_report_link(self, obj):
        """
        Genera un enlace a la vista de detalles del reporte en el admin.
        """
        url = reverse('admin:content_report_change', args=[obj.id])
        return format_html('<a href="{}">Ver detalles</a>', url)

    view_report_link.short_description = 'Ver detalles'  # Nombre que aparecerá en el admin

    def has_add_permission(self, request, obj=None):
        """
        Deshabilita la opción de agregar reportes desde el inline.
        """
        return False

    def has_view_permission(self, request, obj=None):
        return True


class ContentAdmin(admin.ModelAdmin):
    """
    Configuración personalizada para la administración del modelo Content en el panel de administración de Django.
    """
    list_display = ('title', 'category', 'autor', 'state', 'date_create', 'date_expire', 'is_active')
    list_filter = ('state', 'is_active', 'category')
    search_fields = ('title', 'summary', 'autor__name', 'category__name')
    fields = ('title', 'summary', 'category', 'autor', 'state', 'is_active', 'date_create', 'date_published', 'date_expire', 'view_content_link', 'report_status')
    readonly_fields = ('title', 'summary', 'category', 'autor', 'state', 'date_create', 'date_published', 'date_expire', 'view_content_link', 'report_status')
    actions = ['activar_contenidos', 'desactivar_contenidos']

    # Agregar los reportes relacionados como inline
    inlines = [ReportInline]

    # Mostrar el enlace a la vista de detalle del contenido
    def view_content_link(self, obj):
        url = reverse('content_view', args=[obj.pk])
        return mark_safe(f'<a href="{url}" target="_blank">Ver contenido</a>')

    view_content_link.short_description = 'Contenido'

    # Campo para mostrar si hay o no reportes
    def report_status(self, obj):
        """
        Retorna un mensaje si no hay reportes para el contenido.
        """
        if obj.report_set.exists():
            return "Hay reportes asociados"
        return "No hay reportes"

    report_status.short_description = 'Estado de los reportes'

    def get_inline_instances(self, request, obj=None):
        """
        Oculta el ReportInline si no hay reportes.
        """
        inline_instances = []
        # Llama a la versión original de la función 'get_inline_instances' del super
        for inline in super().get_inline_instances(request, obj):
            # Verifica si el inline es del tipo 'ReportInline' y si no hay reportes
            if isinstance(inline, ReportInline) and obj and not obj.report_set.exists():
                continue  # Si no hay reportes, no agregar este inline
            inline_instances.append(inline)  # Si hay reportes o es otro inline, lo añade
        return inline_instances  # Retorna la lista de inlines que sí deben mostrarse

    # Lógica condicional para mostrar el campo report_status solo si no hay reportes
    def get_fields(self, request, obj=None):
        """
        Muestra o esconde el campo 'report_status' dependiendo si hay reportes.
        """
        fields = ['title', 'summary', 'category', 'autor', 'state', 'is_active', 'date_create', 'date_published',
                  'date_expire', 'view_content_link']

        # Solo agregar el campo 'report_status' si no hay reportes
        if obj and not obj.report_set.exists():
            fields.append('report_status')

        return fields

    # Acción para activar contenidos seleccionados
    @admin.action(description='Activar contenidos seleccionados')
    def activar_contenidos(self, request, queryset):
        """
        Acción personalizada para activar los contenidos seleccionados en el panel de administración.

        Verifica si el usuario tiene el permiso 'edit_is_active' antes de activar los contenidos.
        Si se activan con éxito, muestra un mensaje de éxito con los títulos de los contenidos activados.

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.
            queryset (QuerySet): QuerySet que contiene los contenidos seleccionados para la acción.

        Acciones:
            - Verifica si el usuario tiene el permiso requerido.
            - Actualiza el campo `is_active` de los contenidos seleccionados a True.
            - Muestra un mensaje de éxito si la activación es exitosa.
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
        Acción personalizada para desactivar los contenidos seleccionados en el panel de administración.

        Verifica si el usuario tiene el permiso 'edit_is_active' antes de desactivar los contenidos.
        Si se desactivan con éxito, muestra un mensaje de éxito con los títulos de los contenidos desactivados.

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.
            queryset (QuerySet): QuerySet que contiene los contenidos seleccionados para la acción.

        Acciones:
            - Verifica si el usuario tiene el permiso requerido.
            - Actualiza el campo `is_active` de los contenidos seleccionados a False.
            - Muestra un mensaje de éxito si la desactivación es exitosa.
        """

        # Verificar el permiso 'edit_is_active'
        if not request.user.has_perm('app.edit_is_active'):
            self.message_user(request, "No tienes permiso para desactivar contenidos.", level=messages.ERROR)
            return
        # Actualizar y obtener los títulos de los contenidos desactivados
        updated = queryset.update(is_active=False)
        nombres = ', '.join([content.title for content in queryset])
        self.message_user(request, f"Contenidos desactivados: {nombres}.", level=messages.SUCCESS)

    def has_add_permission(self, request):
        """
        Controla el permiso para añadir nuevos contenidos desde el panel de administración.

        Esta función siempre devuelve False, impidiendo que los usuarios puedan agregar
        nuevos contenidos directamente desde el panel de administración.

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.

        Retorna:
            bool: False, indicando que no se permite la adición de nuevos contenidos.
        """
        # No permitir agregar nuevos contenidos desde el admin
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Controla el permiso para eliminar contenidos desde el panel de administración.

        Esta función siempre devuelve False, impidiendo que los usuarios puedan eliminar
        contenidos directamente desde el panel de administración.

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.
            obj (Model, opcional): Objeto del modelo específico para verificar permisos (opcional).

        Retorna:
            bool: False, indicando que no se permite la eliminación de contenidos.
        """
        # No permitir eliminar contenidos desde el admin
        return False

    def has_view_permission(self, request, obj=None):
        """
        Controla el permiso para ver los contenidos en el panel de administración.

        Permite la visualización de los contenidos solo si el usuario tiene el permiso 'view_content'.
        Esta función asegura que solo los usuarios con el permiso adecuado puedan acceder
        a la lista de contenidos y ver detalles.

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.
            obj (Model, opcional): Objeto del modelo específico para verificar permisos (opcional).

        Retorna:
            bool: True si el usuario tiene el permiso 'view_content', de lo contrario False.
        """
        # Permite la visualización solo si el usuario tiene el permiso 'view_content'
        return request.user.has_perm('app.view_content')

    def has_change_permission(self, request, obj=None):
        """
        Controla el permiso para editar contenidos desde el panel de administración.

        Permite la edición de los contenidos solo si el usuario tiene el permiso 'edit_is_active'.
        Esto asegura que solo los usuarios con permisos específicos puedan cambiar el estado
        de activación de los contenidos, sin modificar otros campos de solo lectura.

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.
            obj (Model, opcional): Objeto del modelo específico para verificar permisos (opcional).

        Retorna:
            bool: True si el usuario tiene el permiso 'edit_is_active', de lo contrario False.
        """
        # Permite la edición solo si el usuario tiene el permiso 'edit_is_active'
        if obj:
            return request.user.has_perm('app.edit_is_active')
        return False

    def has_module_permission(self, request):
        """
        Controla el permiso para acceder al módulo de contenidos en el panel de administración.

        Permite el acceso al módulo de contenidos solo si el usuario tiene el permiso 'view_content'.
        Este permiso general asegura que solo los usuarios autorizados puedan ver y navegar por el módulo
        de contenidos en el panel de administración.

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.

        Retorna:
            bool: True si el usuario tiene el permiso 'view_content', de lo contrario False.
        """
        return request.user.has_perm('app.view_content')

class ReportAdmin(admin.ModelAdmin):
    """
    Configuración personalizada para la administración del modelo Report.
    """
    list_display = ('content', 'reported_by', 'email', 'reason', 'created_at',)
    search_fields = ('content__title', 'name', 'email', 'reason')

    fields = ('content', 'reported_by', 'email', 'name', 'reason', 'description', 'created_at')
    readonly_fields = ('content', 'reported_by', 'email', 'name', 'reason', 'description', 'created_at')


    def has_add_permission(self, request):
        """
        Controla el permiso para añadir nuevos contenidos desde el panel de administración.

        Esta función siempre devuelve False, impidiendo que los usuarios puedan agregar
        nuevos contenidos directamente desde el panel de administración.

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.

        Retorna:
            bool: False, indicando que no se permite la adición de nuevos contenidos.
        """
        # No permitir agregar nuevos contenidos desde el admin
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Controla el permiso para eliminar contenidos desde el panel de administración.

        Esta función siempre devuelve False, impidiendo que los usuarios puedan eliminar
        contenidos directamente desde el panel de administración.

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.
            obj (Model, opcional): Objeto del modelo específico para verificar permisos (opcional).

        Retorna:
            bool: False, indicando que no se permite la eliminación de contenidos.
        """
        # No permitir eliminar contenidos desde el admin
        return False

    def has_view_permission(self, request, obj=None):
        """
        Controla el permiso para ver los contenidos en el panel de administración.

        Permite la visualización de los contenidos solo si el usuario tiene el permiso 'view_content'.
        Esta función asegura que solo los usuarios con el permiso adecuado puedan acceder
        a la lista de contenidos y ver detalles.

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.
            obj (Model, opcional): Objeto del modelo específico para verificar permisos (opcional).

        Retorna:
            bool: True si el usuario tiene el permiso 'view_content', de lo contrario False.
        """
        # Permite la visualización solo si el usuario tiene el permiso 'view_content'
        return request.user.has_perm('app.view_content')

    def has_change_permission(self, request, obj=None):
        """
        Controla el permiso para editar contenidos desde el panel de administración.

        Permite la edición de los contenidos solo si el usuario tiene el permiso 'edit_is_active'.
        Esto asegura que solo los usuarios con permisos específicos puedan cambiar el estado
        de activación de los contenidos, sin modificar otros campos de solo lectura.

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.
            obj (Model, opcional): Objeto del modelo específico para verificar permisos (opcional).

        Retorna:
            bool: True si el usuario tiene el permiso 'edit_is_active', de lo contrario False.
        """
        # Permite la edición solo si el usuario tiene el permiso 'edit_is_active'
        if obj:
            return request.user.has_perm('app.edit_is_active')
        return False

    def has_module_permission(self, request):
        """
        Controla el permiso para acceder al módulo de contenidos en el panel de administración.

        Permite el acceso al módulo de contenidos solo si el usuario tiene el permiso 'view_content'.
        Este permiso general asegura que solo los usuarios autorizados puedan ver y navegar por el módulo
        de contenidos en el panel de administración.

        Parámetros:
            request (HttpRequest): Objeto de solicitud HTTP.

        Retorna:
            bool: True si el usuario tiene el permiso 'view_content', de lo contrario False.
        """
        return request.user.has_perm('app.view_content')


# Registra el modelo Report en el admin
admin.site.register(Report, ReportAdmin)

# Registrar el modelo Content con la clase ContentAdmin
admin.site.register(Content, ContentAdmin)

Content._meta.verbose_name = ("Contenido")  # Singular: "Contenido"
Content._meta.verbose_name_plural = ("Contenidos")  # Plural: "Contenidos"

Report._meta.verbose_name = ("Reporte")  # Singular: "Reporte"
Report._meta.verbose_name_plural = ("Reportes")  # Plural: "Reportes"
