from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from .models import VendorProfile
from .serializers import VendorProfileSerializer
from .permissions import IsVendorOwnerOrAdmin


class VendorProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet לניהול פרופילי ספקים:
    - לקוחות רגילים רואים רק ספקים פעילים
    - מנהלים רואים את כולם
    - ספק יכול לערוך רק את עצמו
    - הרשמה כספק נעשית דרך /vendors/become/
    """

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
        בחירת הרשאות דינמית לפי פעולה:
        - list / retrieve: כולם יכולים לקרוא (קריאה בלבד)
        - become: רק משתמש מחובר
        - update / partial_update / destroy: רק בעלים או מנהל
        - ברירת מחדל: משתמש מחובר
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticatedOrReadOnly]

        elif self.action == 'become':
            permission_classes = [IsAuthenticated]

        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsVendorOwnerOrAdmin]

        else:
            # ברירת מחדל – דורש התחברות
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        מנהלים רואים את כל הספקים.
        משתמשים רגילים רואים רק ספקים מאושרים (is_active=True).
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
        """
        פעולה לוגית: 'הפוך לספק'
        - משתמש מחובר שולח פרטי עסק
        - נוצר עבורו VendorProfile חדש במצב is_active=False
        - אם כבר קיים לו ספק – נחזיר שגיאה
        """
        user = request.user

        # אם כבר יש לו VendorProfile – לא ניצור שוב
        if hasattr(user, 'vendor_profile'):
            return Response(
                {"error": "כבר קיים פרופיל ספק עבור משתמש זה."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # שולפים רק את שדות העסק מהבקשה (לא user ולא is_active)
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
