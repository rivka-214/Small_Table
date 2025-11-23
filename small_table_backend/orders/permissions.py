from rest_framework import permissions


class IsOrderOwnerOrVendorOrAdmin(permissions.BasePermission):
    """
Order Permission:
- Customer: Sees/updates only his orders (no status change)
- Supplier: Sees/updates orders belonging to him (can change status)
- admin (role 'admin' or staff/superuser): Sees everything
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
    Permission for OrderAddon items:
    - admin: All
    - Vendor: Can read/edit add-ons to their orders
    - Customer: Can only view add-ons to their orders (not edit)
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


        if order.user == user:
            return request.method in permissions.SAFE_METHODS


        if hasattr(user, 'vendor_profile') and order.vendor == user.vendor_profile:
            return True

        return False
