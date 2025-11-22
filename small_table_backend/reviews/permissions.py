from rest_framework import permissions


class IsReviewOwnerVendorOrAdmin(permissions.BasePermission):
    """
    הרשאות:
    - כולם יכולים לראות חוות דעת פומביות (is_public=True)
      (הסינון בפועל נעשה ב-View דרך get_queryset)
    - לקוח (owner): יכול לעדכן/למחוק רק את החוות דעת שלו
    - ספק: יכול לראות את כל החוות דעת עליו (גם אם is_public=False),
      אבל לא יכול לערוך אותן
    - admin / staff: יכולים הכל
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user or not user.is_authenticated:
            # קריאה אנונימית תטופל ברמת ה-Queryset (לא כאן)
            return False

        # admin דרך role בטבלת UserRoles או staff/superuser
        has_admin_role = getattr(user, 'user_roles', None) and user.user_roles.filter(
            role__name='admin'
        ).exists()

        if has_admin_role or user.is_staff or user.is_superuser:
            return True

        # SAFE_METHODS - קריאה בלבד
        if request.method in permissions.SAFE_METHODS:
            # בעל החוות דעת תמיד יכול לקרוא
            if obj.user_id == user.id:
                return True

            # ספק – יכול לקרוא את כל מה שקשור אליו
            if hasattr(user, 'vendor_profile') and obj.vendor_id == user.vendor_profile.id:
                return True

            # אחרים – יראו רק אם is_public=True (אכיפה ב-get_queryset)
            return obj.is_public

        # שיטות כתיבה: רק בעל החוות דעת
        if obj.user_id == user.id:
            return True

        return False
