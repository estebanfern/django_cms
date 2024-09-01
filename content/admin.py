from django.contrib import admin, messages
from .models import Content

class ContentAdmin(admin.ModelAdmin):
    # Mostrar estos campos en la lista de contenidos
    list_display = ('title', 'category', 'autor', 'state', 'date_create', 'date_expire', 'is_active')

    # Añadir filtros para estos campos
    list_filter = ('state', 'is_active', 'category')

    # Habilitar búsqueda por estos campos
    search_fields = ('title', 'summary', 'autor__name', 'category__name')

    # Campos a mostrar en el formulario de creación y edición
    fields = ('title', 'summary', 'category', 'autor', 'state', 'is_active', 'date_create', 'date_expire')

    # Hacer todos los campos de solo lectura, excepto 'is_active'
    readonly_fields = ('title', 'summary', 'category', 'autor', 'state', 'date_create', 'date_expire')

    # Definir acciones personalizadas
    actions = ['activar_contenidos', 'desactivar_contenidos']

    # Acción para activar contenidos seleccionados
    @admin.action(description='Activar contenidos seleccionados')
    def activar_contenidos(self, request, queryset):
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
        # Verificar el permiso 'edit_is_active'
        if not request.user.has_perm('app.edit_is_active'):
            self.message_user(request, "No tienes permiso para desactivar contenidos.", level=messages.ERROR)
            return
        # Actualizar y obtener los títulos de los contenidos desactivados
        updated = queryset.update(is_active=False)
        nombres = ', '.join([content.title for content in queryset])
        self.message_user(request, f"Contenidos desactivados: {nombres}.", level=messages.SUCCESS)

    def has_add_permission(self, request):
        # No permitir agregar nuevos contenidos desde el admin
        return False

    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar contenidos desde el admin
        return False

    def has_view_permission(self, request, obj=None):
        # Permite la visualización solo si el usuario tiene el permiso 'view_content'
        return request.user.has_perm('app.view_content')

    def has_change_permission(self, request, obj=None):
        # Permite la edición solo si el usuario tiene el permiso 'edit_is_active'
        if obj:
            return request.user.has_perm('app.edit_is_active')
        return False

    def has_module_permission(self, request):
        return request.user.has_perm('app.view_content')

# Registrar el modelo Content con la clase ContentAdmin
admin.site.register(Content, ContentAdmin)
