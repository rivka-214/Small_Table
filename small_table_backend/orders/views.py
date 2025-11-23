from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated

from .models import Order, OrderAddon
from .serializers import OrderSerializer, OrderAddonSerializer
from .permissions import IsOrderOwnerOrVendorOrAdmin, IsOrderAddonOwnerOrVendorOrAdmin


class OrderViewSet(viewsets.ModelViewSet):
    """
    Order Management:
    - Customer: Sees only their own orders
    - Supplier: Sees only orders to them (vendor)
    - Admin: Sees everything
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOrderOwnerOrVendorOrAdmin]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'vendor', 'package']
    search_fields = ['user__username', 'vendor__business_name', 'note']
    ordering_fields = ['created_at', 'total_price', 'guests_count', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user

        has_admin_role = getattr(user, 'user_roles', None) and user.user_roles.filter(
            role__name='admin'
        ).exists()

        if user.is_staff or user.is_superuser or has_admin_role:
            return Order.objects.select_related('user', 'vendor', 'package') \
                .prefetch_related('items', 'addons')

        # ספק – רואה הזמנות אליו
        if hasattr(user, 'vendor_profile'):
            return Order.objects.filter(
                vendor=user.vendor_profile
            ).select_related('user', 'vendor', 'package') \
             .prefetch_related('items', 'addons')

        return Order.objects.filter(
            user=user
        ).select_related('user', 'vendor', 'package') \
         .prefetch_related('items', 'addons')

    def perform_create(self, serializer):

        serializer.save()


class OrderAddonViewSet(viewsets.ModelViewSet):
    """
    Managing add-ons selected in an order (OrderAddon):
 """

    queryset = OrderAddon.objects.select_related(
        'order',
        'order__user',
        'order__vendor',
        'addon',
        'addon__package',
        'addon__category',
    )
    serializer_class = OrderAddonSerializer
    permission_classes = [IsAuthenticated, IsOrderAddonOwnerOrVendorOrAdmin]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['order', 'addon', 'addon__category']
    search_fields = ['addon__name', 'addon__category__name', 'order__user__username']
    ordering_fields = ['created_at', 'subtotal']
    ordering = ['-created_at']
