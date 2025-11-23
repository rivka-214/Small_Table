from rest_framework import permissions

class IsVendorOwnerOrAdmin(permissions.BasePermission):

#בדיקה ברמת האובייקט
    def has_object_permission(self, request, view, obj):

        #  בדיקה 1: האם המשתמש הוא מנהל? (RBAC)
        if request.user and request.user.is_authenticated:
            has_admin_role = request.user.user_roles.filter(
                role__name='admin'
            ).exists()

            if has_admin_role:
                return True

        #  בדיקה 2: האם המשתמש הוא הבעלים? (Least Privilege)
        if request.user and obj.user == request.user:
            return True  # בעלים - מורשה לערוך את עצמו בלבד

        #  ברירת מחדל: אסור (Fail Secure)
        return False