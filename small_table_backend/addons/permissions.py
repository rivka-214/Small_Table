from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    General permission for add-on categories:
    - Read (GET/HEAD/OPTIONS): Allowed for everyone
    - Write: Only admin / staff / superuser
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        if not user or not user.is_authenticated:
            return False

        has_admin_role = getattr(user, 'user_roles', None) and user.user_roles.filter(
            role__name='admin'
        ).exists()

        return bool(has_admin_role or user.is_staff or user.is_superuser)


class IsAddonOwnerOrAdmin(permissions.BasePermission):
    """
    Permissions for Addon:
    - Read: Everyone (set at View level)
    - Create / Update / Delete:
    * admin/staff/superuser – can do everything
    * Provider – only add-ons of their packages
    """
    def has_permission(self, request, view):

        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        if not user or not user.is_authenticated:
            return False

        has_admin_role = getattr(user, 'user_roles', None) and user.user_roles.filter(
            role__name='admin'
        ).exists()

        if has_admin_role or user.is_staff or user.is_superuser:
            return True

        # ספקים רשאים להגיש בקשות כתיבה – נבדוק בעלות ברמת האובייקט
        return hasattr(user, 'vendor_profile')

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # admin
        has_admin_role = getattr(user, 'user_roles', None) and user.user_roles.filter(
            role__name='admin'
        ).exists()

        if has_admin_role or user.is_staff or user.is_superuser:
            return True

        # ספק בעל החבילה
        if hasattr(user, 'vendor_profile') and obj.package.vendor == user.vendor_profile:
            return True

        return False
