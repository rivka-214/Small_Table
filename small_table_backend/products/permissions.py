from rest_framework import permissions


class IsVendorOwnerOrReadOnly(permissions.BasePermission):


    def has_permission(self, request, view):

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        # ✅ בדיקה 2: האם המשתמש הוא מנהל? (RBAC)
        if request.user and request.user.is_authenticated:
            # בדיקה אם יש תפקיד admin
            has_admin_role = request.user.user_roles.filter(
                role__name='admin'
            ).exists()

            if has_admin_role:
                return True


        # בדיקה 3: האם המשתמש הוא בעל המוצר?
        # המוצר שייך לספק → הספק מקושר למשתמש
        # obj.vendor.user == request.user

        if request.user and request.user.is_authenticated:
            # בדיקה שהמשתמש הוא הספק של המוצר
          return obj.vendor.user == request.user

          return False


class IsVendorOwner(permissions.BasePermission):
    """
    Stricter permission - only the owner (or administrator) can access
    """
    def has_object_permission(self, request, view, obj):

        if not request.user or not request.user.is_authenticated:
            return False

        # בדיקת מנהל
        has_admin_role = request.user.user_roles.filter(
            role__name='admin'
        ).exists()

        if has_admin_role:
            return True

        # בדיקת בעלות
        return obj.vendor.user == request.user


class IsVendor(permissions.BasePermission):
    """
    Check that the user is a vendor (has a VendorProfile)

    Usage: to create new products
    """
    message = "רק ספקים רשומים יכולים לבצע פעולה זו"

    def has_permission(self, request, view):
        """
        Checking that the user is logged in and is a provider
        """
        if not request.user or not request.user.is_authenticated:
            return False


        try:
            vendor_profile = request.user.vendor_profile
            return vendor_profile.is_active
        except:
            return False