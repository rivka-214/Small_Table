from rest_framework import permissions

class IsPackageOwnerOrAdmin(permissions.BasePermission):
    """
    Package permissions:
     admin (role 'admin') – can edit any package
     Provider – can only edit packages that belong to them
     Others – read only
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user or not user.is_authenticated:
            # קריאה ציבורית תטופל ברמת ה-View (list/retrieve)
            return False

        # בדיקה האם המשתמש admin דרך טבלת UserRoles
        has_admin_role = user.user_roles.filter(
            role__name='admin'
        ).exists()

        if has_admin_role or user.is_staff or user.is_superuser:
            return True

        if hasattr(user, 'vendor_profile') and obj.vendor == user.vendor_profile:
            return True

        return False
