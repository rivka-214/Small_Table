# users/views.py
from rest_framework import viewsets, filters, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import User, Role, UserRole
from .serializers import (
    UserSerializer,
    RoleSerializer,
    UserRoleSerializer,
    RegisterSerializer,
)
from .permissions import IsAdmin, IsAdminOrSelf


class RegisterView(generics.CreateAPIView):
    """
    הרשמה:
    POST /api/auth/register/
    פתוח לכולם, בלי JWT.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    """
    User Management (API):
    - JWTAuthentication חובה
    - הרשאות לפי פעולה:
        * list      → רק אדמין
        * destroy   → רק אדמין
        * create    → רק אדמין (יצירה ידנית אם תרצי)
        * retrieve  → אדמין או המשתמש עצמו
        * update    → אדמין או המשתמש עצמו
        * partial_update → אדמין או המשתמש עצמו
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]

    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["username", "email", "date_joined"]
    ordering = ["username"]
    search_fields = ["username", "email"]

    def get_permissions(self):
        if self.action in ["list", "destroy", "create"]:
            permission_classes = [IsAuthenticated, IsAdmin]
        elif self.action in ["retrieve", "update", "partial_update"]:
            permission_classes = [IsAuthenticated, IsAdminOrSelf]
        else:
            # ברירת מחדל – ננעל כאילו זה רק אדמין
            permission_classes = [IsAuthenticated, IsAdmin]
        return [perm() for perm in permission_classes]


class RoleViewSet(viewsets.ModelViewSet):
    """
    Role Management:
    בפועל – רק אדמין
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    authentication_classes = [JWTAuthentication]

    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["name"]
    ordering = ["name"]
    search_fields = ["name", "description"]

    def get_permissions(self):
        return [IsAuthenticated(), IsAdmin()]


class UserRoleViewSet(viewsets.ModelViewSet):
    """
    Assigning roles to users:
    גם כאן – רק אדמין
    """
    queryset = UserRole.objects.select_related("user", "role")
    serializer_class = UserRoleSerializer
    authentication_classes = [JWTAuthentication]

    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["assigned_at"]
    ordering = ["-assigned_at"]
    search_fields = ["user__username", "role__name"]

    def get_permissions(self):
        return [IsAuthenticated(), IsAdmin()]
