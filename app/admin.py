from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from app.models import Role, CustomUser


# from app.models import User

# Register your models here.

# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('nombre', 'email')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('permissions',)

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
