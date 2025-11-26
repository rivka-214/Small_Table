# users/permissions.py
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    הרשאה: רק אדמין (is_staff=True)
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )


class IsAdminOrSelf(permissions.BasePermission):
    """
    הרשאה: אדמין יכול הכל.
    משתמש רגיל – רק על עצמו.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_staff:
            return True

        # obj הוא אובייקט של User
        return obj == user
