from django.contrib import admin, messages
from .models import Category
from .forms import CategoryForm
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

class CategoryAdmin(admin.ModelAdmin):
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
        actions = super().get_actions(request)
        # Eliminar la acción predeterminada de eliminación
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

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

    # Acción personalizada para moderar categorías
    @admin.action(description='Moderar categorías seleccionadas')
    def moderar_categorias(self, request, queryset):
        queryset.update(is_moderated=True)
        self.message_user(request, "Categorías seleccionadas moderadas.", level=messages.SUCCESS)

    # Acción personalizada para quitar la moderación de categorías
    @admin.action(description='Quitar moderación de categorías seleccionadas')
    def quitar_moderacion_categorias(self, request, queryset):
        queryset.update(is_moderated=False)
        self.message_user(request, "Moderación quitada de las categorías seleccionadas.", level=messages.SUCCESS)

    @admin.action(description='Activar categorías seleccionadas')
    def activar_categorias(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Categorías seleccionadas activadas.", level=messages.SUCCESS)

    @admin.action(description='Desactivar categorías seleccionadas')
    def desactivar_categorias(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Categorías seleccionadas desactivadas.", level=messages.SUCCESS)

    # Definir una acción personalizada para la eliminación
    @admin.action(description='Eliminar categorías seleccionadas')
    def delete_selected_categories(self, request, queryset):
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
            # Continuar con la eliminación solo si no hay categorías con contenidos
            super().delete_queryset(request, queryset)

    # Sobrescribir delete_model para manejar la eliminación individual
    def delete_model(self, request, obj):
        if obj.content_set.exists():
            self.message_user(request, "No se puede eliminar esta categoría porque tiene contenidos asociados.", level=messages.ERROR)
        else:
            super().delete_model(request, obj)

    # Métodos para verificar permisos personalizados
    def has_module_permission(self, request):
        return request.user.has_perm('app.view_category')

    def has_view_permission(self, request, obj=None):
        return request.user.has_perm('app.view_category')

    def has_add_permission(self, request):
        return request.user.has_perm('app.create_category')

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('app.edit_category')

    def has_delete_permission(self, request, obj=None):
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