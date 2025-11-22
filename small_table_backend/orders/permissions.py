from rest_framework import permissions


class IsOrderOwnerOrVendorOrAdmin(permissions.BasePermission):
    """
    הרשאה להזמנה:
    - לקוח: רואה/מעדכן רק את ההזמנות שלו (ללא שינוי סטטוס)
    - ספק: רואה/מעדכן הזמנות ששייכות אליו (יכול לשנות סטטוס)
    - admin (role 'admin' או staff/superuser): רואה הכל
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        has_admin_role = getattr(user, 'user_roles', None) and user.user_roles.filter(
            role__name='admin'
        ).exists()

        if has_admin_role or user.is_staff or user.is_superuser:
            return True

        # האם זה הלקוח שביצע את ההזמנה?
        if obj.user == user:
            if request.method in permissions.SAFE_METHODS:
                return True
            if 'status' in request.data:
                return False
            return True

        # האם זה הספק של ההזמנה?
        if hasattr(user, 'vendor_profile') and obj.vendor == user.vendor_profile:
            return True

        return False


class IsOrderAddonOwnerOrVendorOrAdmin(permissions.BasePermission):
    """
    הרשאה לפריטי OrderAddon:
    - admin: הכל
    - ספק: יכול לקרוא/לערוך תוספות להזמנות שלו
    - לקוח: יכול רק לראות תוספות בהזמנות שלו (לא לערוך)
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        order = obj.order

        has_admin_role = getattr(user, 'user_roles', None) and user.user_roles.filter(
            role__name='admin'
        ).exists()

        if has_admin_role or user.is_staff or user.is_superuser:
            return True

        # לקוח – רק קריאה
        if order.user == user:
            return request.method in permissions.SAFE_METHODS

        # ספק שייך להזמנה – יכול לערוך
        if hasattr(user, 'vendor_profile') and order.vendor == user.vendor_profile:
            return True

        return False
