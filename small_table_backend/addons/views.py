from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import AddonCategory, Addon
from .serializers import AddonCategorySerializer, AddonSerializer
from .permissions import IsAdminOrReadOnly, IsAddonOwnerOrAdmin


class AddonCategoryViewSet(viewsets.ModelViewSet):
    """
    Manage add-on categories:
    - list/retrieve: read
    - create/update/delete: admin/staff/superuser only
    """
    queryset = AddonCategory.objects.all()
    serializer_class = AddonCategorySerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticatedOrReadOnly]
        else:
            permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
        return [p() for p in permission_classes]


class AddonViewSet(viewsets.ModelViewSet):
    """
    Manage package add-ons:

    - list/retrieve:
    * Customer only sees add-ons is_active=True
    * Provider only sees add-ons of their packages
    * admin sees everything

    """
    serializer_class = AddonSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['package', 'category', 'is_active', 'pricing_type', 'is_included']
    search_fields = [
        'name',
        'package__name',
        'category__name',
        'package__vendor__business_name',
    ]
    ordering_fields = ['created_at', 'price', 'name']
    ordering = ['name']

    def get_queryset(self):
        qs = Addon.objects.select_related('package', 'package__vendor', 'category')
        user = self.request.user

        # לא מחובר – רק תוספות פעילות
        if not user.is_authenticated:
            return qs.filter(is_active=True)

        # admin – רואה הכל
        has_admin_role = getattr(user, 'user_roles', None) and user.user_roles.filter(
            role__name='admin'
        ).exists()
        if user.is_staff or user.is_superuser or has_admin_role:
            return qs

        # ספק – רואה רק תוספות של החבילות שלו
        if hasattr(user, 'vendor_profile'):
            return qs.filter(package__vendor=user.vendor_profile)

        # לקוח רגיל – רק תוספות פעילות
        return qs.filter(is_active=True)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticatedOrReadOnly]
        else:
            permission_classes = [IsAuthenticated, IsAddonOwnerOrAdmin]
        return [p() for p in permission_classes]
