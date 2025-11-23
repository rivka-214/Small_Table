from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Package, PackageCategory, PackageCategoryItem
from .serializers import (
    PackageSerializer,
    PackageCategorySerializer,
    PackageCategoryItemSerializer,
)
from .permissions import IsPackageOwnerOrAdmin


class PackageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing packages:
    - list/retrieve: everyone can see active packages
    - create: only connected provider (or admin)
    - update/destroy: package owner or admin
    """
    queryset = Package.objects.select_related('vendor', 'vendor__user').all()
    serializer_class = PackageSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        'vendor',
        'is_active',
    ]

    search_fields = [
        'name',
        'description',
        'vendor__business_name',
        'vendor__user__username',
        'vendor__user__email',
    ]

    ordering_fields = [
        'created_at',
        'price_per_person',
        'min_guests',
        'max_guests',
    ]

    ordering = ['-created_at']

    def get_permissions(self):
        """
        Dynamic permissions:
        - list, retrieve: free read (with is_active filtering)
        - my_packages: only for logged in users
        - create/update/partial_update/destroy: only for owner or admin
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticatedOrReadOnly]

        elif self.action in ['create', 'update', 'partial_update', 'destroy', 'my_packages']:
            permission_classes = [IsAuthenticated, IsPackageOwnerOrAdmin]

        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        - admin/staff see all packages
        - regular user: sees only packages is_active=True
        """
        qs = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            return qs.filter(is_active=True)

        has_admin_role = user.user_roles.filter(role__name='admin').exists()

        if user.is_staff or user.is_superuser or has_admin_role:
            return qs

        return qs.filter(is_active=True)

    def create(self, request, *args, **kwargs):

        user = request.user
        if not user.is_authenticated:
            return Response(
                {"detail": "יש להתחבר כדי ליצור חבילה."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not (hasattr(user, 'vendor_profile') or user.is_staff or user.is_superuser):
            return Response(
                {"detail": "רק ספקים יכולים ליצור חבילות."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_packages(self, request):

        user = request.user
        if not hasattr(user, 'vendor_profile'):
            return Response(
                {"detail": "משתמש זה אינו ספק."},
                status=status.HTTP_400_BAD_REQUEST
            )

        qs = self.get_queryset().filter(vendor=user.vendor_profile)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class PackageCategoryViewSet(viewsets.ModelViewSet):
    """
    Manage categories within a package
    (Usually used in vendor management screens, less for the public)
    """
    queryset = PackageCategory.objects.select_related('package', 'package__vendor').all()
    serializer_class = PackageCategorySerializer
    permission_classes = [IsAuthenticated, IsPackageOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['package', 'is_active']
    ordering_fields = ['created_at']
    ordering = ['id']


class PackageCategoryItemViewSet(viewsets.ModelViewSet):
    """
    Managing items within package categories
    """
    queryset = PackageCategoryItem.objects.select_related(
        'package_category',
        'package_category__package',
        'product',
    ).all()
    serializer_class = PackageCategoryItemSerializer
    permission_classes = [IsAuthenticated, IsPackageOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['package_category', 'is_active', 'is_premium']
    ordering_fields = ['created_at', 'extra_price_per_person']
    ordering = ['id']
