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
    ViewSet לניהול חבילות:
    - list/retrieve: כולם יכולים לראות חבילות פעילות
    - create: רק ספק מחובר (או admin)
    - update/destroy: בעל החבילה או admin
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
        הרשאות דינמיות:
        - list, retrieve: קריאה חופשית (עם סינון is_active)
        - my_packages: ספק מחובר בלבד
        - create/update/partial_update/destroy: ספק בעלים או admin
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
        - admin/staff רואים את כל החבילות
        - משתמש רגיל: רואה רק חבילות is_active=True
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
        """
        יצירת חבילה:
        - ספק חייב להיות מחובר
        """
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
        """
        רשימת החבילות של הספק המחובר
        """
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
    ניהול קטגוריות בתוך חבילה
    (בד"כ ישמש במסכי ניהול ספק, פחות לציבור)
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
    ניהול פריטים בתוך קטגוריות של חבילה
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
