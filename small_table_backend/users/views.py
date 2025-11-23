# users/views.py
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import User, Role, UserRole
from .serializers import UserSerializer, RoleSerializer, UserRoleSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ניהול משתמשים:
    - JWTAuthentication
    - אפשר חיפוש/מיון לפי שם, מייל ותאריך הצטרפות
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["username", "email", "date_joined"]
    ordering = ["username"]
    search_fields = ["username", "email"]


class RoleViewSet(viewsets.ModelViewSet):
    """
    ניהול תפקידים:
    בפועל – בדרך כלל רק אדמין יגע בזה,
    אבל כרגע ההרשאה הכללית היא IsAuthenticated
    (אפשר לשדרג בהמשך ל- IsAdminUser ).
    """

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["name"]
    ordering = ["name"]
    search_fields = ["name", "description"]


class UserRoleViewSet(viewsets.ModelViewSet):
    """
    שיוך תפקידים למשתמשים:
    משתמשים אחרים בקוד (כמו הרשאות של Packages / Orders)
    עובדים מול user.user_roles, ולכן חשוב שהמודל הזה יישאר.
    """

    queryset = UserRole.objects.select_related("user", "role")
    serializer_class = UserRoleSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["assigned_at"]
    ordering = ["-assigned_at"]
    search_fields = ["user__username", "role__name"]
