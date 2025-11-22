from rest_framework import permissions


class IsVendorOwnerOrReadOnly(permissions.BasePermission):
    """
    כללים:
    ========
      כולם:           GET (קריאה) - כל המוצרים זמינים לצפייה
      מנהל (admin):    הכל על כולם
      ספק-בעלים:      יכול לערוך/למחוק רק את המוצרים שלו
      משתמש רגיל:     GET בלבד
    """

    def has_permission(self, request, view):
        """
        בדיקה ברמת ה-View (לפני גישה לאובייקט ספציפי)
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        בדיקה ברמת אובייקט ספציפי (מוצר)

        obj = Product instance
        """
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
    הרשאה מחמירה יותר - רק הבעלים (או מנהל) יכול לגשת
    """

    def has_object_permission(self, request, view, obj):
        """
        רק הבעלים או מנהל
        """
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
    בדיקה שהמשתמש הוא ספק (יש לו VendorProfile)

    שימוש: ליצירת מוצרים חדשים
    """

    message = "רק ספקים רשומים יכולים לבצע פעולה זו"

    def has_permission(self, request, view):
        """
        בדיקה שהמשתמש מחובר והוא ספק
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # בדיקה שיש לו VendorProfile
        try:
            vendor_profile = request.user.vendor_profile
            return vendor_profile.is_active
        except:
            return False