from rest_framework import permissions


class IsReviewOwnerVendorOrAdmin(permissions.BasePermission):
    """
    Permissions:
    - Everyone can see public reviews (is_public=True)
    (Actual filtering is done in the View via get_queryset)
    - Customer (owner): can only update/delete his own reviews
    - Supplier: can see all reviews about him (even if is_public=False),
    but cannot edit them
    - admin / staff: can do everything
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

        # SAFE_METHODS - קריאה בלבד
        if request.method in permissions.SAFE_METHODS:
            if obj.user_id == user.id:
                return True

            if hasattr(user, 'vendor_profile') and obj.vendor_id == user.vendor_profile.id:
                return True

            return obj.is_public

        if obj.user_id == user.id:
            return True

        return False
