from django.contrib import admin, messages
from .models import Category
from .forms import CategoryForm

class CategoryAdmin(admin.ModelAdmin):

    form = CategoryForm

    # Mostrar estos campos en la lista de categorías
    list_display = ('name', 'type', 'is_active', 'price', 'date_create')

    # Añadir filtros para estos campos
    list_filter = ('type', 'is_active', 'is_moderated')

    # Habilitar búsqueda por estos campos
    search_fields = ('name', 'description')

    # Campos a mostrar en el formulario de creación y edición
    fields = ('name', 'description', 'type', 'is_active', 'is_moderated', 'price')

    # Ordenar los registros por fecha de creación de manera descendente
    ordering = ('-date_create',)

    # Definir acciones personalizadas
    actions = ['activar_categorias', 'desactivar_categorias']

    @admin.action(description='Activar categorías seleccionadas')
    def activar_categorias(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Categorías seleccionadas activadas.", level=messages.SUCCESS)

    @admin.action(description='Desactivar categorías seleccionadas')
    def desactivar_categorias(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Categorías seleccionadas desactivadas.", level=messages.SUCCESS)


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
        return request.user.has_perm('app.delete_category')

# Registrar el modelo con el admin
admin.site.register(Category, CategoryAdmin)
