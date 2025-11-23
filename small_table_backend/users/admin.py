from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, Role, UserRole


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """
    You can display roles as a read-only list, but not within fieldsets.
    """

    fieldsets = DjangoUserAdmin.fieldsets + (
        ('פרטים נוספים', {
            'fields': ('phone',),
        }),
    )

    readonly_fields = []

    list_display = ('username', 'email', 'phone', 'is_staff')

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'assigned_at']
    list_filter = ['role']
    search_fields = ['user__username', 'role__name']
