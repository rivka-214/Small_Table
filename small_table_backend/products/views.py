from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product
from .permissions import IsVendorOwnerOrReadOnly, IsVendor
from .serializers import ProductSerializer




class ProductViewSet(viewsets.ModelViewSet):

    queryset = Product.objects.select_related('vendor', 'vendor__user').all()
    serializer_class = ProductSerializer

    filter_backends = [
        DjangoFilterBackend,  # סינון מדויק
        filters.SearchFilter,  # חיפוש טקסט
        filters.OrderingFilter  # מיון
    ]

    # חיפוש טקסט חופשי
    search_fields = [
        'product_name',
        'description',
        'category',
        'vendor__business_name'
    ]

    # שדות למיון
    ordering_fields = [
        'name',

        'created_at',
        'category'
    ]

    ordering = ['-created_at']  # ברירת מחדל: חדשים ראשון

    # סינון מדויק
    filterset_fields = {
        'category': ['exact', 'icontains'],

        'is_available': ['exact'],
        'vendor': ['exact']
    }

    # ──────────────────────────────────────────────────────────
    #  הרשאות דינמיות לפי פעולה
    # ──────────────────────────────────────────────────────────
    def get_permissions(self):
        """
        הרשאות משתנות לפי סוג הפעולה
        """
        # קריאה - כולם (גם לא מחוברים)
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsVendorOwnerOrReadOnly]

        # יצירה - רק ספקים רשומים
        elif self.action == 'create':
            permission_classes = [IsAuthenticated, IsVendor]

        # עריכה / מחיקה - רק בעל המוצר או אדמין
        else:
            permission_classes = [IsVendorOwnerOrReadOnly]

        return [permission() for permission in permission_classes]

    # ──────────────────────────────────────────────────────────
    # סינון חכם של QuerySet
    # ──────────────────────────────────────────────────────────
    def get_queryset(self):
        """
        סינון מוצרים לפי פרמטרים נוספים
        """
        queryset = super().get_queryset()

        # הצג רק מוצרים זמינים (אלא אם מבקשים אחרת)
        show_all = self.request.query_params.get('show_all', None)
        if not show_all:
            queryset = queryset.filter(is_available=True)
        return queryset

    # ──────────────────────────────────────────────────────────
    # ️ יצירת מוצר חדש
    # ──────────────────────────────────────────────────────────
    def create(self, request, *args, **kwargs):
        """
        יצירת מוצר חדש עם וולידציה
        """
        # בדיקה שהמשתמש הוא ספק
        try:
            vendor_profile = request.user.vendor_profile
        except:
            return Response(
                {
                    'error': 'רק ספקים יכולים ליצור מוצרים',
                    'detail': 'יש להירשם כספק תחילה'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        שמירת מוצר חדש
        """
        product = serializer.save()
        print(f"✅ מוצר חדש: {product.product_name} (ספק: {product.vendor.business_name})")

    # ──────────────────────────────────────────────────────────
    #  עדכון מוצר
    # ──────────────────────────────────────────────────────────
    def perform_update(self, serializer):
        """
        עדכון מוצר קיים
        """
        product = serializer.save()
        print(f"✏️ מוצר עודכן: {product.product_name}")

    # ──────────────────────────────────────────────────────────
    #  מחיקת מוצר
    # ──────────────────────────────────────────────────────────
    def perform_destroy(self, instance):
        """
        מחיקת מוצר
        """
        print(f" מוצר נמחק: {instance.product_name} (ID: {instance.id})")
        instance.delete()
