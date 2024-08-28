from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
#from app.models import Role, CustomUser


# from app.models import User

# Register your models here.

# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('nombre', 'email')


class CustomGroupAdmin(BaseGroupAdmin):
    def has_module_permission(self, request):
        return request.user.is_staff and request.user.has_perm('app.manage_roles')

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff and request.user.has_perm('app.manage_roles')

    def has_add_permission(self, request):
        return request.user.is_staff and request.user.has_perm('app.manage_roles')

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff and request.user.has_perm('app.manage_roles')

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff and request.user.has_perm('app.manage_roles')

# Desregistrar el modelo Group
admin.site.unregister(Group)

# Registrar el modelo Group con la clase CustomGroupAdmin
admin.site.register(Group, CustomGroupAdmin)