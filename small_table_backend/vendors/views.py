from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from .models import VendorProfile
from .serializers import VendorProfileSerializer
from .permissions import IsVendorOwnerOrAdmin


class VendorProfileViewSet(viewsets.ModelViewSet):


    queryset = VendorProfile.objects.select_related('user').all()
    serializer_class = VendorProfileSerializer

    # פילטרים, חיפוש ומיון
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        'business_name',
        'kashrut_level',
        'address',
        'user__username',
        'user__email',
    ]

    ordering_fields = [
        'business_name',
        'created_at',
        'is_active',
    ]

    ordering = ['-created_at']

    def get_permissions(self):
        """
        Dynamic permission selection by action:
     """
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticatedOrReadOnly]

        elif self.action == 'become':
            permission_classes = [IsAuthenticated]

        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsVendorOwnerOrAdmin]

        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Admins see all providers.
        Regular users only see approved providers (is_active=True).
        """
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return queryset

        return queryset.filter(is_active=True)

    def create(self, request, *args, **kwargs):
        """
        חוסמים יצירה ישירה של ספק דרך /vendors/
        ומכוונים לשימוש ב-/vendors/become/
        כדי למנוע שליחת user_id חיצוני ולשמור על אבטחה.
        """
        return Response(
            {
                "detail": "יצירת ספק מתבצעת רק דרך /api/vendors/become/ על ידי המשתמש המחובר."
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def become(self, request):
        user = request.user

        # אם כבר יש לו VendorProfile – לא ניצור שוב
        if hasattr(user, 'vendor_profile'):
            return Response(
                {"error": "כבר קיים פרופיל ספק עבור משתמש זה."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # ניצור את הספק עם user מהבקשה ו-is_active=False (מחכה לאישור מנהל)
        vendor = serializer.save(user=user, is_active=False)

        return Response(
            {
                "message": "הבקשה להירשם כספק התקבלה וממתינה לאישור מנהל.",
                "vendor": VendorProfileSerializer(
                    vendor,
                    context=self.get_serializer_context()
                ).data,
            },
            status=status.HTTP_201_CREATED
        )
