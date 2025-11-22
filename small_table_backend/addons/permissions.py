from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    הרשאה כללית לקטגוריות תוספות:
    - קריאה (GET/HEAD/OPTIONS): מותר לכולם
    - כתיבה: רק admin / staff / superuser
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
    הרשאות עבור Addon:
    - קריאה: כולם (מוגדר ברמת ה-View)
    - יצירה / עדכון / מחיקה:
        * admin/staff/superuser – יכולים הכל
        * ספק – רק תוספות של החבילות שלו
    """

    def has_permission(self, request, view):
        """
        בדיקה כללית לפני גישה:
        - לקריאה: מותר לכולם (ה-View מגביל אם צריך)
        - לכתיבה: חייבים להיות ספק או אדמין
        """
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
