from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, Role, UserRole


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """
    אפשר להציג roles כ-readonly list, אבל לא בתוך fieldsets.
    """

    fieldsets = DjangoUserAdmin.fieldsets + (
        ('פרטים נוספים', {
            'fields': ('phone',),
        }),
    )

    # לא ניתן להשתמש ב-filter_horizontal בגלל through model
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
