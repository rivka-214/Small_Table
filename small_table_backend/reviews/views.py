from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Review
from .serializers import ReviewSerializer
from .permissions import IsReviewOwnerVendorOrAdmin


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ניהול חוות דעת:
    - list:
        * כולם יכולים לראות חוות דעת פומביות (is_public=True)
        * ספק רואה את כל החוות דעת עליו
        * לקוח רואה חוות דעת שלו + פומביות
    - create:
        * רק משתמש מחובר, ועל הזמנה ששייכת לו
    - update/destroy:
        * בעל החוות דעת או admin
    """

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsReviewOwnerVendorOrAdmin]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['vendor', 'rating', 'is_public']
    search_fields = ['comment', 'title', 'user__username', 'vendor__business_name']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        qs = Review.objects.select_related('user', 'vendor', 'order', 'order__package')

        # משתמש אנונימי – רואה רק פומבי
        if not user.is_authenticated:
            return qs.filter(is_public=True)

        # admin
        has_admin_role = getattr(user, 'user_roles', None) and user.user_roles.filter(
            role__name='admin'
        ).exists()

        if user.is_staff or user.is_superuser or has_admin_role:
            return qs

        # ספק – רואה כל מה שנכתב עליו
        if hasattr(user, 'vendor_profile'):
            return qs.filter(vendor=user.vendor_profile)

        # לקוח – רואה פומבי + מה שהוא כתב בעצמו
        return qs.filter(
            models.Q(is_public=True) | models.Q(user=user)
        ).distinct()
